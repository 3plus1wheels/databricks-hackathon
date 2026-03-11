from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from models import Task, Message
from services import delta_store
from services.genie_chat import genie_chat
from services.orchestrator import orchestrator

router = APIRouter()


def _parse_analyze_command(message: str) -> tuple[str | None, str | None]:
    remainder = message[8:].strip()
    if not remainder:
        return None, None

    parts = remainder.split(None, 1)
    if len(parts) == 2:
        space_name = parts[0].rstrip(":")
        prompt = parts[1].strip()
        if space_name and prompt:
            return space_name, prompt

    if ":" in remainder:
        space_name, prompt = remainder.split(":", 1)
        space_name = space_name.strip()
        prompt = prompt.strip()
        if space_name and prompt:
            return space_name, prompt

    return None, None


def _parse_user_command(message: str) -> dict[str, str] | None:
    trimmed = message.strip()
    lowered = trimmed.lower()

    if lowered.startswith("do:"):
        prompt = trimmed[3:].strip()
        if not prompt:
            return None
        return {"kind": "do", "prompt": prompt}

    if lowered.startswith("analyze:"):
        space_name, prompt = _parse_analyze_command(trimmed)
        if not space_name or not prompt:
            return None
        return {"kind": "analyze", "space_name": space_name, "prompt": prompt}

    return None


def _invalid_command_message() -> str:
    return (
        "Message must start with do: for agent work or analyze:space_name for Genie analysis. "
        "Example: do: build a launch checklist or analyze:sales_ops top customers this month"
    )


def _build_task_title(command: dict[str, str]) -> str:
    if command["kind"] == "do":
        return command["prompt"][:80]
    return f"Analyze {command['space_name']}: {command['prompt']}"[:80]


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid JSON"})
                continue

            msg_type = msg.get("type", "user_message")
            if msg_type == "approval":
                task_id = msg.get("task_id")
                approved = msg.get("approved", False)
                feedback = msg.get("feedback")
                if task_id:
                    await orchestrator.handle_approval(task_id, approved, feedback)
                continue

            if msg_type != "user_message":
                await websocket.send_json({"type": "error", "content": f"Unknown message type: {msg_type}"})
                continue

            message = msg.get("message", "")
            task_id = msg.get("task_id")

            if not message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            command = _parse_user_command(message)
            if command is None:
                await websocket.send_json({"type": "error", "content": _invalid_command_message()})
                continue

            is_agent_task = command["kind"] == "do"

            # Create task entry
            if not task_id:
                title = _build_task_title(command)
                task = Task(
                    title=title,
                    description=message,
                    status="in_progress",
                )
                delta_store.create_task(task)
                task_id = task.task_id
                await websocket.send_json({"type": "task_created", "task_id": task_id, "title": task.title})

            delta_store.add_message(Message(task_id=task_id, role="user", content=message))

            try:
                if is_agent_task:
                    prompt = command["prompt"]
                    async for event in orchestrator.run(prompt, task_id):
                        await websocket.send_json(event)
                        if event.get("type") == "agent_step" and event.get("status") == "done":
                            delta_store.add_message(Message(
                                task_id=task_id,
                                role="assistant",
                                content=event.get("content", ""),
                                agent_name=event.get("agent_name"),
                            ))
                else:
                    async for event in genie_chat.chat(
                        command["prompt"],
                        task_id,
                        space_name=command["space_name"],
                    ):
                        event["task_id"] = task_id
                        await websocket.send_json(event)
                        if event.get("type") == "genie_response":
                            delta_store.add_message(Message(
                                task_id=task_id,
                                role="assistant",
                                content=event.get("content", ""),
                                agent_name="analyst",
                                metadata={"query_result": event["query_result"]} if event.get("query_result") else None,
                            ))
            except Exception as e:
                await websocket.send_json({"type": "error", "content": str(e)})
    except WebSocketDisconnect:
        pass



