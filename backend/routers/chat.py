from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

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
            if msg_type != "user_message":
                await websocket.send_json({"type": "error", "content": f"Unknown message type: {msg_type}"})
                continue

            message = msg.get("message", "")
            task_id = msg.get("task_id")

            if not message:
                await websocket.send_json({"type": "error", "content": "Empty message"})
                continue

            async def send_ws(payload: dict):
                await websocket.send_json(payload)

            try:
                await orchestrator.process_message(message, task_id, send_ws)
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Orchestrator error: {str(e)}",
                })
    except WebSocketDisconnect:
        pass
