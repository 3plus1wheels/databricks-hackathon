from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid4())


class Task(BaseModel):
    task_id: str = Field(default_factory=_uuid)
    title: str
    description: str
    status: Literal["todo", "in_progress", "awaiting_approval", "completed", "failed"] = "todo"
    assigned_agents: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    result: str | None = None


class Message(BaseModel):
    message_id: str = Field(default_factory=_uuid)
    task_id: str
    role: Literal["user", "assistant", "system", "checkpoint"]
    content: str
    agent_name: str | None = None
    created_at: datetime = Field(default_factory=_now)
    metadata: dict | None = None


class SubTask(BaseModel):
    subtask_id: str = Field(default_factory=_uuid)
    task_id: str
    agent_name: str
    description: str
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    result: str | None = None


class ChatRequest(BaseModel):
    message: str
    task_id: str | None = None


class CheckpointResponse(BaseModel):
    task_id: str
    checkpoint_id: str
    approved: bool
    feedback: str | None = None
