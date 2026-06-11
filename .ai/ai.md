# {{PROJECT_NAME}} — AI Context Index

<!--
  THIS IS THE SINGLE ENTRY POINT for any AI assistant working in this repository.
  AGENTS.md and CLAUDE.md both redirect here. Fill in every {{PLACEHOLDER}} and
  delete the guidance comments. Keep this file a MAP — short summaries that point
  to the detailed files. Don't dump everything here.
-->

This file is the **single entry point** for any AI assistant working in this repository. Read this first, then navigate to the specific file listed for the topic you need.

---

## Project at a Glance

**System:** {{ONE_LINE_DESCRIPTION — what the product is and who it's for}}

**Primary users:** {{WHO_USES_IT}}

**Tech stack:** {{STACK — e.g. Flutter · Firebase · …}}

**Stack details:**
```
{{KEY_LIBRARIES_AND_THEIR_ROLES — one per line}}
```

**Source of truth for the project:** {{LINK to Notion / wiki / PM workspace}}

<!-- Add any other top-level pointers (e.g. the spec/form/design that defines the product). -->

---

## Navigation Map — What to consult for what

| Topic | Local file | Source link |
|---|---|---|
| **System architecture**, structure, data model, hosting | [architecture.md](architecture.md) | {{LINK}} |
| **Architecture decisions** (ADRs, rationale) | [docs/ARD.md](docs/ARD.md) | {{LINK}} |
| **Feature requirements**, user stories, NFRs, scope | [docs/SRS.md](docs/SRS.md) | {{LINK}} |
| **UI components**, colour tokens, typography, screens | [ui_guidelines.md](ui_guidelines.md) | {{LINK}} |
| **Design system** (component specs, prototypes) | [docs/design-doc.md](docs/design-doc.md) | {{LINK}} |
| **Coding standards** (language, DB, git, security) | [coding_conventions.md](coding_conventions.md) | — |
| **AI/LLM role and hard rules** | [config/system.md](config/system.md) | — |
| **How to read/update tasks** | [workflows/notion-workflow.md](workflows/notion-workflow.md) | {{LINK}} |
| **Sequential task queue** (what's next) | [workflows/task-queue.md](workflows/task-queue.md) | {{LINK}} |

---

## Project Management IDs (for MCP tools)

<!-- If you use Notion/Linear/etc. via MCP, record the database/collection IDs here. -->

| Database | ID |
|---|---|
| {{Tasks Tracker}} | `{{collection://...}}` |
| {{Document Hub}} | `{{collection://...}}` |

---

## Key Decisions (ultra-short)

<!-- 3–7 bullets capturing the decisions an assistant must not violate or re-litigate. -->

- {{DECISION_1}}
- {{DECISION_2}}
- {{DECISION_3}}

---

## Hard Rules

<!-- Numbered, non-negotiable constraints. Keep them concrete and testable. -->

1. {{RULE_1}}
2. {{RULE_2}}
3. {{RULE_3}}
4. `architecture.md` and `docs/ARD.md` are the source of truth for structure decisions; update them when decisions change.
5. When starting a task: fetch it from the PM tool first, set status to "In progress", implement, then set "Done" (see `workflows/notion-workflow.md`).
