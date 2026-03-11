"""
Task and message persistence.

Uses Databricks Delta tables when credentials are configured,
falls back to in-memory storage for local development.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import config
from models import Task, Message


# ── In-memory fallback ────────────────────────────────────────────────────────

_tasks: dict[str, Task] = {}
_messages: dict[str, list[Message]] = {}  # keyed by task_id


def _use_databricks() -> bool:
    """Return True only when real (non-placeholder) credentials are present."""
    placeholders = {"your-warehouse-id", "your-token-here", "your-workspace.cloud.databricks.com"}
    host = config.DATABRICKS_HOST
    token = config.DATABRICKS_TOKEN
    wh_id = config.DATABRICKS_WAREHOUSE_ID
    if not (host and token and wh_id):
        return False
    if any(p in v for p in placeholders for v in (host, token, wh_id)):
        return False
    return True


def _conn():
    from databricks import sql as dbsql
    return dbsql.connect(
        server_hostname=config.DATABRICKS_HOST.replace("https://", ""),
        http_path=f"/sql/1.0/warehouses/{config.DATABRICKS_WAREHOUSE_ID}",
        access_token=config.DATABRICKS_TOKEN,
    )


def _fqn(table: str) -> str:
    return f"{config.DATABRICKS_CATALOG}.{config.DATABRICKS_SCHEMA}.{table}"


# ── Tasks ────────────────────────────────────────────────────────────────────


def create_task(task: Task) -> Task:
    if not _use_databricks():
        _tasks[task.task_id] = task
        return task
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""INSERT INTO {_fqn("tasks")}
            (task_id, title, description, status, assigned_agents, created_at, updated_at, result)
            VALUES (%(task_id)s, %(title)s, %(description)s, %(status)s,
                    %(assigned_agents)s, %(created_at)s, %(updated_at)s, %(result)s)""",
            {
                "task_id": task.task_id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "assigned_agents": json.dumps(task.assigned_agents),
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "result": task.result,
            },
        )
    return task


def get_tasks() -> list[Task]:
    if not _use_databricks():
        return sorted(_tasks.values(), key=lambda t: t.created_at, reverse=True)
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {_fqn('tasks')} ORDER BY created_at DESC")
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [_row_to_task(dict(zip(cols, r))) for r in rows]


def get_task(task_id: str) -> Task | None:
    if not _use_databricks():
        return _tasks.get(task_id)
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT * FROM {_fqn('tasks')} WHERE task_id = %(task_id)s",
            {"task_id": task_id},
        )
        row = cur.fetchone()
        if not row:
            return None
        cols = [d[0] for d in cur.description]
        return _row_to_task(dict(zip(cols, row)))


def update_task(task_id: str, **fields: Any) -> None:
    if not _use_databricks():
        task = _tasks.get(task_id)
        if task:
            for k, v in fields.items():
                setattr(task, k, v)
            task.updated_at = datetime.now(timezone.utc)
        return
    sets = ", ".join(f"{k} = %({k})s" for k in fields)
    fields["task_id"] = task_id
    fields["updated_at"] = datetime.now(timezone.utc).isoformat()
    sets += ", updated_at = %(updated_at)s"
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"UPDATE {_fqn('tasks')} SET {sets} WHERE task_id = %(task_id)s",
            fields,
        )


def _row_to_task(row: dict) -> Task:
    agents = row.get("assigned_agents", "[]")
    if isinstance(agents, str):
        agents = json.loads(agents)
    return Task(
        task_id=row["task_id"],
        title=row["title"],
        description=row["description"],
        status=row["status"],
        assigned_agents=agents,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        result=row.get("result"),
    )


# ── Messages ─────────────────────────────────────────────────────────────────


def add_message(msg: Message) -> Message:
    if not _use_databricks():
        _messages.setdefault(msg.task_id, []).append(msg)
        return msg
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"""INSERT INTO {_fqn("messages")}
            (message_id, task_id, role, content, agent_name, created_at, metadata)
            VALUES (%(message_id)s, %(task_id)s, %(role)s, %(content)s,
                    %(agent_name)s, %(created_at)s, %(metadata)s)""",
            {
                "message_id": msg.message_id,
                "task_id": msg.task_id,
                "role": msg.role,
                "content": msg.content,
                "agent_name": msg.agent_name,
                "created_at": msg.created_at.isoformat(),
                "metadata": json.dumps(msg.metadata) if msg.metadata else None,
            },
        )
    return msg


def get_messages(task_id: str) -> list[Message]:
    if not _use_databricks():
        return _messages.get(task_id, [])
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            f"SELECT * FROM {_fqn('messages')} WHERE task_id = %(task_id)s ORDER BY created_at",
            {"task_id": task_id},
        )
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [_row_to_message(dict(zip(cols, r))) for r in rows]


def _row_to_message(row: dict) -> Message:
    meta = row.get("metadata")
    if isinstance(meta, str):
        meta = json.loads(meta)
    return Message(
        message_id=row["message_id"],
        task_id=row["task_id"],
        role=row["role"],
        content=row["content"],
        agent_name=row.get("agent_name"),
        created_at=row["created_at"],
        metadata=meta,
    )
