"""Databricks Genie conversational interface."""
from __future__ import annotations

import asyncio
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
        return bool(config.DATABRICKS_HOST and config.DATABRICKS_TOKEN and config.GENIE_SPACE_ID)

    async def chat(self, message: str, task_id: str) -> AsyncGenerator[dict, None]:
        """Send a message to Genie, stream thinking status, then yield the final response."""
        if not self.is_configured():
            yield {
                "type": "genie_response",
                "content": (
                    "Genie is not connected. Add DATABRICKS_HOST, DATABRICKS_TOKEN, "
                    "and GENIE_SPACE_ID to backend/.env to enable it."
                ),
            }
            return

        try:
            space_id = config.GENIE_SPACE_ID
            conv_id = self._conversations.get(task_id)

            if conv_id is None:
                # New conversation
                wait = await asyncio.to_thread(
                    self.client.genie.start_conversation,
                    space_id,
                    message,
                )
                conv_id = wait.response.conversation_id
                message_id = wait.response.message_id
                self._conversations[task_id] = conv_id
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
