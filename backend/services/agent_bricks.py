"""Wrapper around Databricks Agent Bricks / Model Serving endpoints."""

from __future__ import annotations

import config


class AgentBricksService:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from databricks.sdk import WorkspaceClient
            self._client = WorkspaceClient(
                host=config.DATABRICKS_HOST,
                token=config.DATABRICKS_TOKEN,
            )
        return self._client

    def query_endpoint(self, endpoint_name: str, messages: list[dict]) -> str:
        """Send messages to a serving endpoint and return the response text."""
        response = self.client.serving_endpoints.query(
            name=endpoint_name,
            messages=messages,
        )
        if hasattr(response, "choices") and response.choices:
            return response.choices[0].message.content
        if hasattr(response, "predictions"):
            return str(response.predictions)
        return str(response)

    def list_endpoints(self) -> list[dict]:
        """List available serving endpoints."""
        endpoints = self.client.serving_endpoints.list()
        return [
            {
                "name": ep.name,
                "state": ep.state.ready if ep.state else "UNKNOWN",
            }
            for ep in endpoints
        ]


# Singleton — lazy initialization, no Databricks connection until first use
agent_service = AgentBricksService()
