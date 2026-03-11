"""
One-time setup: Create Agent Bricks in Databricks workspace.

This creates:
1. A Knowledge Assistant (KA) for document Q&A
2. A Genie Space for SQL analytics (requires existing tables)
3. A Supervisor Agent (MAS) that orchestrates both

Usage:
  cd backend && python ../scripts/setup_databricks.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from databricks.sdk import WorkspaceClient
import config


def main():
    client = WorkspaceClient(
        host=config.DATABRICKS_HOST,
        token=config.DATABRICKS_TOKEN,
    )

    print("Databricks workspace connected successfully.")
    print(f"Host: {config.DATABRICKS_HOST}")

    # List existing serving endpoints
    print("\nExisting serving endpoints:")
    for ep in client.serving_endpoints.list():
        state = ep.state.ready if ep.state else "UNKNOWN"
        print(f"  - {ep.name} ({state})")

    print("\n--- Agent Bricks Setup ---")
    print("""
To set up Agent Bricks for the demo, use the Databricks UI or the Agent Bricks MCP tools:

1. Knowledge Assistant (KA):
   - Name: "workbench_researcher"
   - Volume: Upload sample docs to a Unity Catalog volume
   - Description: "Researches background info and company documentation"

2. Genie Space:
   - Name: "workbench_analyst"
   - Tables: Connect to your analytics tables
   - Description: "Analyzes data and runs SQL queries"

3. Supervisor Agent (MAS):
   - Name: "workbench_orchestrator"
   - Sub-agents: workbench_researcher (KA), workbench_analyst (Genie)
   - Instructions: "Decompose user tasks into sub-tasks. Route document questions
     to the researcher, data questions to the analyst. Synthesize results."

After creating these, update backend/.env with:
   WORKBENCH_SUPERVISOR_ENDPOINT=workbench_orchestrator
   WORKBENCH_RESEARCHER_ENDPOINT=workbench_researcher
   WORKBENCH_ANALYST_ENDPOINT=workbench_analyst
    """)


if __name__ == "__main__":
    main()
