from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import delta_store
from services.orchestrator import orchestrator

router = APIRouter()


class RejectBody(BaseModel):
    feedback: str | None = None


@router.get("/tasks")
async def list_tasks():
    return delta_store.get_tasks()


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = delta_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    messages = delta_store.get_messages(task_id)
    return {"task": task, "messages": messages}


@router.post("/tasks/{task_id}/approve")
async def approve_checkpoint(task_id: str):
    task = delta_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await orchestrator.handle_approval(task_id, approved=True)
    return {"task_id": task_id, "approved": True}


@router.post("/tasks/{task_id}/reject")
async def reject_checkpoint(task_id: str, body: RejectBody | None = None):
    task = delta_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    feedback = body.feedback if body else None
    await orchestrator.handle_approval(task_id, approved=False, feedback=feedback)
    return {"task_id": task_id, "approved": False}
