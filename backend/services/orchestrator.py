import asyncio
from typing import AsyncGenerator
from models import Task, Message, SubTask
from services.agent_bricks import agent_service
from services import delta_store


class Orchestrator:
    def __init__(self):
        # Agent name -> Databricks serving endpoint (placeholder until real endpoints exist)
        self.agent_registry = {
            "researcher": "workbench_researcher",
            "analyst":   "workbench_analyst",
            "writer":    "workbench_writer",
        }

    def _choose_agents(self, prompt: str) -> list[str]:
        """Pick which agents to spin up based on prompt complexity/keywords."""
        prompt_lower = prompt.lower()
        agents = []
        if any(w in prompt_lower for w in ("research", "find", "look up", "who", "what is", "background")):
            agents.append("researcher")
        if any(w in prompt_lower for w in ("analyze", "data", "sql", "query", "stats", "numbers", "compare")):
            agents.append("analyst")
        if any(w in prompt_lower for w in ("write", "draft", "create", "generate", "summarize", "report")):
            agents.append("writer")
        # Default: all three for complex tasks
        if not agents:
            agents = ["researcher", "analyst", "writer"]
        return agents

    async def run(self, prompt: str, task_id: str) -> AsyncGenerator[dict, None]:
        """Stream agent events for a 'do:' task."""
        task = delta_store.get_task(task_id)
        if task is None:
            return

        agents = self._choose_agents(prompt)

        yield {
            "type": "agent_plan",
            "task_id": task_id,
            "agents": agents,
            "content": f"Spinning up {len(agents)} agent(s): {', '.join(agents)}",
        }

        subtasks = [
            SubTask(
                task_id=task_id,
                agent_name=name,
                description=self._subtask_desc(name, prompt),
            )
            for name in agents
        ]

        # Fan out in parallel; collect events via a queue
        queue: asyncio.Queue[dict | None] = asyncio.Queue()

        async def run_agent(subtask: SubTask):
            await queue.put({
                "type": "agent_step",
                "task_id": task_id,
                "agent_name": subtask.agent_name,
                "status": "working",
                "content": f"Starting: {subtask.description}",
            })

            endpoint = self.agent_registry.get(subtask.agent_name)
            if endpoint:
                try:
                    result = await asyncio.to_thread(
                        agent_service.query_endpoint,
                        endpoint,
                        [{"role": "user", "content": subtask.description}],
                    )
                except Exception:
                    result = f"[Placeholder] {subtask.agent_name} would: {subtask.description}"
            else:
                await asyncio.sleep(1.5)
                result = f"[Placeholder] {subtask.agent_name} would: {subtask.description}"

            subtask.result = result
            subtask.status = "completed"
            await queue.put({
                "type": "agent_step",
                "task_id": task_id,
                "agent_name": subtask.agent_name,
                "status": "done",
                "content": result,
            })
            return subtask

        async def producer():
            completed = await asyncio.gather(*[run_agent(st) for st in subtasks])
            await queue.put(None)  # sentinel
            return completed

        producer_task = asyncio.create_task(producer())

        # Stream events as they arrive
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event

        completed_subtasks = await producer_task
        combined = "\n\n".join(
            f"**{st.agent_name}**: {st.result}" for st in completed_subtasks
        )

        # Checkpoint
        delta_store.update_task(task_id, status="awaiting_approval")
        cp = Message(
            task_id=task_id,
            role="checkpoint",
            content="Agents finished. Review and approve to complete the task.",
            metadata={"combined_result": combined, "checkpoint_id": ""},
        )
        delta_store.add_message(cp)
        cp.metadata["checkpoint_id"] = cp.message_id  # type: ignore[index]

        yield {
            "type": "checkpoint",
            "task_id": task_id,
            "checkpoint_id": cp.message_id,
            "summary": combined,
        }

    def _subtask_desc(self, agent: str, prompt: str) -> str:
        descs = {
            "researcher": f"Research background and context for: {prompt}",
            "analyst":   f"Analyze and identify key data insights for: {prompt}",
            "writer":    f"Draft a comprehensive response for: {prompt}",
        }
        return descs.get(agent, f"Work on: {prompt}")

    async def handle_approval(self, task_id: str, approved: bool, feedback: str | None = None) -> None:
        if approved:
            delta_store.update_task(task_id, status="completed")
            delta_store.add_message(
                Message(task_id=task_id, role="system", content="Task approved and completed.")
            )
        else:
            delta_store.update_task(task_id, status="in_progress")
            delta_store.add_message(
                Message(
                    task_id=task_id,
                    role="system",
                    content=f"Task rejected. Feedback: {feedback or 'None provided'}",
                )
            )


orchestrator = Orchestrator()


    async def process_message(self, message: str, task_id: str | None, send_ws) -> Task:
        """
        Full lifecycle:
        1. Create task if new
        2. Decompose into sub-tasks
        3. Fan out to agents in parallel
        4. Stream results back via send_ws callback
        5. Checkpoint for approval
        """
        # Create task
        if not task_id:
            task = Task(title=message[:80], description=message, status="in_progress")
            delta_store.create_task(task)
            task_id = task.task_id
            await send_ws({"type": "task_created", "task_id": task_id, "title": task.title})
        else:
            task = delta_store.get_task(task_id)

        # Save user message
        delta_store.add_message(Message(task_id=task_id, role="user", content=message))

        # Decompose task
        await send_ws({
            "type": "agent_message",
            "task_id": task_id,
            "agent_name": "orchestrator",
            "content": "Analyzing task and assigning to agent team...",
        })

        subtasks = self._decompose(task_id, message)

        # Fan out in parallel
        async def run_agent(subtask: SubTask):
            await send_ws({
                "type": "agent_message",
                "task_id": task_id,
                "agent_name": subtask.agent_name,
                "content": f"Starting: {subtask.description}",
            })

            endpoint = self.agent_registry.get(subtask.agent_name)
            if endpoint:
                try:
                    result = agent_service.query_endpoint(
                        endpoint, [{"role": "user", "content": subtask.description}]
                    )
                except Exception:
                    result = f"[Simulated] Completed analysis for: {subtask.description}"
            else:
                # Simulate for demo
                await asyncio.sleep(1)
                result = f"[Simulated] Completed: {subtask.description}"

            subtask.result = result
            subtask.status = "completed"
            await send_ws({
                "type": "agent_message",
                "task_id": task_id,
                "agent_name": subtask.agent_name,
                "content": result,
            })
            return subtask

        # Execute all subtasks in parallel
        completed = await asyncio.gather(*[run_agent(st) for st in subtasks])

        # Synthesize results
        combined = "\n\n".join(f"**{st.agent_name}**: {st.result}" for st in completed)

        # Checkpoint
        delta_store.update_task(task_id, status="awaiting_approval")
        checkpoint_msg = Message(
            task_id=task_id,
            role="checkpoint",
            content="All agents have completed their work. Please review and approve.",
            metadata={"combined_result": combined},
        )
        delta_store.add_message(checkpoint_msg)

        await send_ws({
            "type": "checkpoint",
            "task_id": task_id,
            "checkpoint_id": checkpoint_msg.message_id,
            "summary": combined,
        })

        return task

    def _decompose(self, task_id: str, message: str) -> list[SubTask]:
        """Break a task into sub-tasks for parallel execution."""
        # For the demo, always create 3 sub-tasks
        return [
            SubTask(
                task_id=task_id,
                agent_name="researcher",
                description=f"Research background and context for: {message}",
            ),
            SubTask(
                task_id=task_id,
                agent_name="analyst",
                description=f"Analyze requirements and identify key considerations for: {message}",
            ),
            SubTask(
                task_id=task_id,
                agent_name="writer",
                description=f"Draft a comprehensive response for: {message}",
            ),
        ]

    async def handle_approval(self, task_id: str, approved: bool, feedback: str | None = None) -> None:
        if approved:
            delta_store.update_task(task_id, status="completed")
            delta_store.add_message(
                Message(task_id=task_id, role="system", content="Task approved and completed.")
            )
        else:
            delta_store.update_task(task_id, status="in_progress")
            delta_store.add_message(
                Message(
                    task_id=task_id,
                    role="system",
                    content=f"Task rejected. Feedback: {feedback or 'None provided'}",
                )
            )


orchestrator = Orchestrator()
