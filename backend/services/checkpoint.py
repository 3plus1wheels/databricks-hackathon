from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PendingCheckpoint:
    task_id: str
    checkpoint_id: str
    summary: str


class CheckpointService:
    def __init__(self):
        self._pending: dict[str, PendingCheckpoint] = {}

    def add(self, task_id: str, checkpoint_id: str, summary: str):
        self._pending[task_id] = PendingCheckpoint(task_id, checkpoint_id, summary)

    def get(self, task_id: str) -> PendingCheckpoint | None:
        return self._pending.get(task_id)

    def resolve(self, task_id: str) -> PendingCheckpoint | None:
        return self._pending.pop(task_id, None)


checkpoint_service = CheckpointService()
