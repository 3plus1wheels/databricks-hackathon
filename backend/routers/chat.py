from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from models import Task, Message
from services import delta_store
from services.genie_chat import genie_chat
from services.orchestrator import orchestrator

router = APIRouter()


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

            is_agent_task = message.lower().startswith("do:")

            # Create task entry
            if not task_id:
                title = message[3:].strip()[:80] if is_agent_task else message[:80]
                task = Task(
                    title=title,
                    description=message,
                    status="in_progress" if is_agent_task else "todo",
                )
                delta_store.create_task(task)
                task_id = task.task_id
                await websocket.send_json({"type": "task_created", "task_id": task_id, "title": task.title})

            delta_store.add_message(Message(task_id=task_id, role="user", content=message))

            try:
                if is_agent_task:
                    # Strip the "do:" prefix before sending to agents
                    prompt = message[3:].strip()
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
                    async for event in genie_chat.chat(message, task_id):
                        event["task_id"] = task_id
                        await websocket.send_json(event)
                        if event.get("type") == "genie_response":
                            delta_store.add_message(Message(
                                task_id=task_id,
                                role="assistant",
                                content=event.get("content", ""),
                                agent_name="genie",
                                metadata={"query_result": event["query_result"]} if event.get("query_result") else None,
                            ))
            except Exception as e:
                await websocket.send_json({"type": "error", "content": str(e)})
    except WebSocketDisconnect:
        pass



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
            if msg_type != "user_message":
                await websocket.send_json({"type": "error", "content": f"Unknown message type: {msg_type}"})
                continue

            message = msg.get("message", "")
            task_id = msg.get("task_id")

            if not message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            # Create a task entry if this is a new conversation
            if not task_id:
                task = Task(title=message[:80], description=message)
                delta_store.create_task(task)
                task_id = task.task_id
                await websocket.send_json({"type": "task_created", "task_id": task_id, "title": task.title})

            delta_store.add_message(Message(task_id=task_id, role="user", content=message))

            try:
                async for event in genie_chat.chat(message, task_id):
                    event["task_id"] = task_id
                    await websocket.send_json(event)
                    # Persist the final response
                    if event.get("type") == "genie_response":
                        delta_store.add_message(Message(
                            task_id=task_id,
                            role="assistant",
                            content=event.get("content", ""),
                            agent_name="genie",
                            metadata={"query_result": event["query_result"]} if event.get("query_result") else None,
                        ))
            except Exception as e:
                await websocket.send_json({"type": "error", "content": f"Genie error: {e}"})
    except WebSocketDisconnect:
        pass
