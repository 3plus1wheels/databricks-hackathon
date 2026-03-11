"""Databricks Genie conversational interface."""
from __future__ import annotations

import asyncio
import re
from typing import AsyncGenerator

import config


class GenieChat:
    def __init__(self):
        self._client = None
        # Map task_id -> genie conversation_id so follow-up messages stay in context
        self._conversations: dict[str, str] = {}

    @property
    def client(self):
        if self._client is None:
            from databricks.sdk import WorkspaceClient
            self._client = WorkspaceClient(
                host=config.DATABRICKS_HOST,
                token=config.DATABRICKS_TOKEN,
            )
        return self._client

    def is_configured(self) -> bool:
        """Only HOST + TOKEN are required; analyze commands provide the space name."""
        placeholders = {"your-token-here", "your-workspace.cloud.databricks.com"}
        return bool(
            config.DATABRICKS_HOST and config.DATABRICKS_TOKEN
            and not any(p in v for p in placeholders for v in (config.DATABRICKS_HOST, config.DATABRICKS_TOKEN))
        )

    def _normalize_space_name(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")

    async def _resolve_space_id(self, space_name: str | None) -> tuple[str | None, str | None]:
        if not space_name:
            if config.GENIE_SPACE_ID:
                return config.GENIE_SPACE_ID, None
            return None, "No Genie space resolved. Use analyze:space_name before your prompt."

        requested_raw = space_name.strip().lower()
        requested_normalized = self._normalize_space_name(space_name)

        if config.GENIE_SPACE_ID and requested_raw in {
            "default",
            config.GENIE_SPACE_ID.strip().lower(),
            self._normalize_space_name(config.GENIE_SPACE_ID),
        }:
            return config.GENIE_SPACE_ID, None

        if not self.is_configured():
            return None, None

        resp = await asyncio.to_thread(self.client.genie.list_spaces)
        spaces = getattr(resp, "spaces", None) or []
        for space in spaces:
            candidates = {
                (space.space_id or "").strip().lower(),
                (space.title or "").strip().lower(),
                self._normalize_space_name(space.space_id or ""),
                self._normalize_space_name(space.title or ""),
            }
            if requested_raw in candidates or requested_normalized in candidates:
                return space.space_id, None

        available = sorted(
            {
                self._normalize_space_name(space.title or space.space_id or "")
                for space in spaces
                if (space.title or space.space_id)
            }
        )
        if available:
            joined = ", ".join(available[:8])
            return None, f"Unknown Genie space '{space_name}'. Use analyze:space_name with one of: {joined}"

        return None, f"Unknown Genie space '{space_name}'. No spaces were returned from Databricks."

    async def chat(self, message: str, task_id: str, space_name: str | None = None) -> AsyncGenerator[dict, None]:
        """Send a message to Genie, stream thinking status, then yield the final response."""
        if not self.is_configured():
            yield {
                "type": "genie_response",
                "content": (
                    "Genie is not connected. Add DATABRICKS_HOST and DATABRICKS_TOKEN "
                    "to backend/.env to enable it."
                ),
            }
            return

        resolved_space, resolution_error = await self._resolve_space_id(space_name)
        if resolution_error:
            yield {
                "type": "genie_response",
                "content": resolution_error,
            }
            return

        try:
            space_id = resolved_space
            # Key conversations by (task_id, space_id) so switching spaces starts fresh
            conv_key = f"{task_id}:{space_id}"
            conv_id = self._conversations.get(conv_key)

            if conv_id is None:
                # New conversation
                wait = await asyncio.to_thread(
                    self.client.genie.start_conversation,
                    space_id,
                    message,
                )
                conv_id = wait.response.conversation_id
                message_id = wait.response.message_id
                self._conversations[conv_key] = conv_id
            else:
                # Continue existing conversation
                wait = await asyncio.to_thread(
                    self.client.genie.create_message,
                    space_id,
                    conv_id,
                    message,
                )
                message_id = wait.response.message_id

            # Poll for completion, streaming status updates
            from databricks.sdk.service.dashboards import MessageStatus

            DONE = {MessageStatus.COMPLETED, MessageStatus.FAILED,
                    MessageStatus.CANCELLED, MessageStatus.QUERY_RESULT_EXPIRED}

            for _ in range(120):  # up to 2 minutes
                msg = await asyncio.to_thread(
                    self.client.genie.get_message,
                    space_id,
                    conv_id,
                    message_id,
                )

                if msg.status in (MessageStatus.FAILED, MessageStatus.CANCELLED):
                    yield {"type": "genie_response", "content": "Genie couldn't answer that. Try rephrasing."}
                    return

                if msg.status == MessageStatus.COMPLETED:
                    break

                friendly = str(msg.status).replace("MessageStatus.", "").replace("_", " ").lower()
                yield {"type": "genie_thinking", "content": friendly}
                await asyncio.sleep(1)
            else:
                yield {"type": "genie_response", "content": "Genie timed out. Please try again."}
                return

            # Extract text from attachments
            text_content = ""
            if msg.attachments:
                for att in msg.attachments:
                    if att.text and att.text.content:
                        text_content = att.text.content
                        break

            # Try to get the query result table (if Genie ran SQL)
            query_result = None
            try:
                qr = await asyncio.to_thread(
                    self.client.genie.get_message_query_result,
                    space_id,
                    conv_id,
                    message_id,
                )
                if qr and qr.statement_response:
                    query_result = self._format_query_result(qr.statement_response)
            except Exception:
                pass

            payload: dict = {
                "type": "genie_response",
                "content": text_content or ("Here are the results:" if query_result else "Done."),
            }
            if query_result:
                payload["query_result"] = query_result
            yield payload

        except Exception as e:
            yield {"type": "genie_response", "content": f"Genie error: {e}"}

    def _format_query_result(self, stmt_response) -> dict | None:
        try:
            cols = [c.name for c in stmt_response.manifest.schema.columns]
            rows = []
            if stmt_response.result and stmt_response.result.data_array:
                for row in stmt_response.result.data_array[:100]:
                    rows.append(list(row))
            return {"columns": cols, "rows": rows}
        except Exception:
            return None


genie_chat = GenieChat()
