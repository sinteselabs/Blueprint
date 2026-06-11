# Notion Workflow

<!--
  How the assistant reads and updates project management (tasks + docs). This template
  assumes Notion via MCP, but adapt it to Linear/Jira/GitHub Issues — the shape is the
  same: where tasks live, the schema, and the lifecycle for working a task.
-->

## Workspace

All project management lives in: {{LINK to workspace}}

> **Setup:** the PM MCP server is declared in `mcp.json`. Enable/authorise the connector
> and restart the agent so the tools load. Fill in the IDs below on first authenticated read.

## Key Databases

| Database | Data Source ID | Purpose |
|---|---|---|
| {{Tasks Tracker}} | `{{collection://...}}` | All project tasks |
| {{Document Hub}} | `{{collection://...}}` | Reference documents |

## Task Schema

- **Task name** — title
- **Status** — `Not started` / `In progress` / `Done`
- **Priority** — `High` / `Medium` / `Low`
- **Task type** — `🐞 Bug` / `💬 Feature request` / `💅 Polish`
- **Phase** — {{your phases}}
- **Assignee** — person
- **Due date** — date

## Working on a Task

1. **Fetch the task** to read the spec and deliverables.
2. **Set status to "In progress"** before starting work.
3. **Check off deliverables** as you complete each one (`- [ ]` → `- [x]`).
4. **Set status to "Done"** once all deliverables are complete and verified.

## Closing a Bug Task

Before setting a `🐞 Bug` to "Done", record in the task's **Plan** section:

1. **Root Cause** — why it happened.
2. **Solution** — each file changed + a brief description.
3. **Result** — outcome and any safety improvements.
4. Set status to **"To test"** after writing the above.

## Updating a Task

Use the PM tool's update API to change properties. Status values: `Not started`, `In progress`, `Done`.
