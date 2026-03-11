"""Genie space management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import config

router = APIRouter()


def _client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient(
        host=config.DATABRICKS_HOST,
        token=config.DATABRICKS_TOKEN,
    )


def _is_configured() -> bool:
    placeholders = {"your-token-here", "your-workspace.cloud.databricks.com"}
    return bool(
        config.DATABRICKS_HOST and config.DATABRICKS_TOKEN
        and not any(p in v for p in placeholders for v in (config.DATABRICKS_HOST, config.DATABRICKS_TOKEN))
    )


@router.get("/genie/spaces")
def list_spaces():
    if not _is_configured():
        # Return the configured space as a single option, or empty
        if config.GENIE_SPACE_ID:
            return [{"space_id": config.GENIE_SPACE_ID, "title": "Default Space", "description": ""}]
        return []

    try:
        resp = _client().genie.list_spaces()
        spaces = getattr(resp, "spaces", None) or []
        return [
            {
                "space_id": s.space_id,
                "title": s.title or s.space_id,
                "description": s.description or "",
            }
            for s in spaces
        ]
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


class CreateSpaceRequest(BaseModel):
    title: str
    description: str = ""


@router.post("/genie/spaces")
def create_space(body: CreateSpaceRequest):
    if not _is_configured():
        raise HTTPException(status_code=400, detail="Databricks not configured. Add DATABRICKS_HOST and DATABRICKS_TOKEN to backend/.env")

    warehouse_id = config.DATABRICKS_WAREHOUSE_ID
    placeholders = {"your-warehouse-id"}
    if not warehouse_id or any(p in warehouse_id for p in placeholders):
        raise HTTPException(
            status_code=400,
            detail="DATABRICKS_WAREHOUSE_ID is not set. Add it to backend/.env to create spaces.",
        )

    try:
        space = _client().genie.create_space(
            warehouse_id=warehouse_id,
            serialized_space="{}",
            title=body.title,
            description=body.description or None,
        )
        return {
            "space_id": space.space_id,
            "title": space.title or body.title,
            "description": space.description or "",
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
