---
date: 2026-03-11
topic: workbench-agent-platform
---

# Workbench: AI Agent Team Platform for Work

## What We're Building

A productivity web application where teams submit tasks through a chat interface, and Databricks Agent Bricks-powered agent teams collaborate to accomplish them in the background. Think "OpenClaw for work" — users describe what they need done, and a multi-agent system orchestrates the work autonomously with human approval checkpoints at key milestones.

The platform has two primary views:
1. **Chat interface** — where users describe tasks and interact with agents conversationally
2. **Kanban board** — where the whole team can see all tasks and their agent-driven progress (To Do → In Progress → Done)

### Hero Demo Flow
User submits a task via chat → orchestrator agent receives it → checks if an existing internal tool can handle it → if yes, routes to that tool → if no, spins up and configures the best-fitting tool for the task → agents collaborate (researcher, executor, reviewer) → pause at checkpoints for human approval → deliver results.

## Target Users

Teams and departments — groups collaborating on shared workflows (e.g., data teams, ops teams, project managers). Not single-user, not enterprise-wide.

## Why This Approach

**Chat-First + Board (Approach A)** was chosen because:
- Chat is the fastest UI to build and maps perfectly to the hero demo (conversational task → agent orchestration)
- The Kanban board provides team visibility without being the primary interaction surface
- Maximizes demo impact with minimum frontend effort for a 1-2 day hackathon

Alternatives considered:
- **Board-First**: More visually impressive but requires significantly more frontend work (drag-and-drop, card components) — too much for 1-2 days
- **Minimal Chat**: Fastest to build but loses the team collaboration angle and looks like "just another chatbot"

## Key Decisions

- **Agent Framework**: Databricks Agent Bricks — workspace already set up and ready
- **Tech Stack**: React frontend + Python (FastAPI) backend
- **Task Flow**: Hybrid chat + board — chat for task creation and interaction, board for team-wide visibility
- **Agent Architecture**: Multi-agent collaboration — tasks get broken down and multiple specialized agents work together (researcher, executor, reviewer pattern)
- **Human-in-the-Loop**: Approval checkpoints — agents pause at key milestones for human review before continuing
- **Hero Demo**: Generic chatbot core — an orchestrator that routes to existing tools or creates new ones on the fly
- **Timeline**: Hackathon scope (1-2 days) — working demo over polish

## Resolved Questions

1. **Internal tools**: Mix of real Databricks tools (jobs, notebooks, SQL warehouses, ML endpoints) and mock external tools (email, Slack, etc.) for the demo
2. **Tool creation scope**: Template selection — agent selects from a library of pre-built Agent Brick templates and configures with the right parameters
3. **Auth & team management**: No auth needed — single shared workspace, all dev time focused on agent orchestration
4. **Data persistence**: Databricks Delta tables — keeps everything in-ecosystem

## Next Steps

→ `/ce:plan` for implementation details
