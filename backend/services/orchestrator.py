import asyncio
import json
from models import Task, Message, SubTask
from services.agent_bricks import agent_service
from services import delta_store


class Orchestrator:
    def __init__(self):
        # Map of agent names to their serving endpoint names
        self.agent_registry = {
            "researcher": "workbench_researcher",
            "analyst": "workbench_analyst",
            "writer": "workbench_writer",
        }

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
