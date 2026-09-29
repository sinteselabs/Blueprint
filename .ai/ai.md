# {{PROJECT_NAME}} — AI Context Index

<!--
  THIS IS THE SINGLE ENTRY POINT for any AI assistant working in this repository.
  AGENTS.md and CLAUDE.md both redirect here. Fill in every {{PLACEHOLDER}} and
  delete the guidance comments. Keep this file a MAP — short summaries that point
  to the detailed files. Don't dump everything here.
-->

This file is the **single entry point** for any AI assistant working in this repository. Read this first, then navigate to the specific file listed for the topic you need.

> **Starting a brand-new project?** Follow [workflows/project-kickoff.md](workflows/project-kickoff.md) —
> a guided, step-by-step interview that produces the core Software Engineering
> documents in order and saves them to your chosen store (Notion by default).

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

**Project memory:** lore — workspace `{{WORKSPACE}}`, project `{{PROJECT}}` (see [workflows/project-memory.md](workflows/project-memory.md)). It holds what happened and who is working on what; it does not replace the PM tool or these files.

<!-- Add any other top-level pointers (e.g. the spec/form/design that defines the product). -->

---

## Navigation Map — What to consult for what

| Topic | Local file | Source link |
|---|---|---|
| **Start a new project** (guided doc generation) | [workflows/project-kickoff.md](workflows/project-kickoff.md) | — |
| **System description** (wide-angle: what, who, why) | [docs/system-description.md](docs/system-description.md) | {{LINK}} |
| **System architecture**, structure, data model, hosting | [architecture.md](architecture.md) | {{LINK}} |
| **Architecture decisions** (ARDs, rationale) | [docs/ARD.md](docs/ARD.md) | {{LINK}} |
| **Feature requirements**, user stories, NFRs, scope | [docs/SRS.md](docs/SRS.md) | {{LINK}} |
| **Use cases & user flows** (actors, diagrams) | [docs/use-cases.md](docs/use-cases.md) | {{LINK}} |
| **Data model** (entities, schema, ERD, classes) | [docs/data-model.md](docs/data-model.md) | {{LINK}} |
| **Wireframes** (low-fi screens per device) | [docs/wireframes.md](docs/wireframes.md) | {{LINK}} |
| **UI components**, colour tokens, typography, screens | [ui_guidelines.md](ui_guidelines.md) | {{LINK}} |
| **Design system** (component specs, prototypes) | [docs/design-doc.md](docs/design-doc.md) | {{LINK}} |
| **Coding standards** (language, DB, git, security) | [coding_conventions.md](coding_conventions.md) | — |
| **AI/LLM role and hard rules** | [config/system.md](config/system.md) | — |
| **How to read/update tasks & docs** | [workflows/notion-workflow.md](workflows/notion-workflow.md) | {{LINK}} |
| **Sequential task queue** (what's next) | [workflows/task-queue.md](workflows/task-queue.md) | {{LINK}} |
| **Running agents in parallel** (git worktree isolation) | [workflows/parallel-agents.md](workflows/parallel-agents.md) | — |
| **Project memory** (lore: recall, handoffs, who is working on what) | [workflows/project-memory.md](workflows/project-memory.md) | {{LINK to the lore web app}} |

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
5. When starting a task: fetch it from the PM tool first, **set status to `In progress` before touching any code**, implement, then set `To test`. A task reaches `Done` only after the user has tested it: when the user says it is tested and done, the assistant sets `Done` (see [workflows/notion-workflow.md](workflows/notion-workflow.md) for the full status lifecycle).
6. **Parallel agents work in separate git worktrees.** Never run two writing agents in the same working directory — one agent = one worktree = one branch, integrated one at a time by the orchestrator (see [workflows/parallel-agents.md](workflows/parallel-agents.md)). If the tasks aren't independent, don't parallelise them: sequence them through [workflows/task-queue.md](workflows/task-queue.md).
7. **New-project kickoff is interactive.** When running `workflows/project-kickoff.md`, do one step per turn, ask the step's questions and WAIT for answers before drafting, and never invent or unilaterally pick the tech stack / framework / hosting / architecture — present options and let the user choose.
8. **Measure before asserting; correct yourself out loud when the measurement disproves you.** Never state a cause, a size, or an improvement you haven't verified — and when a number contradicts something you already told the user, say so plainly and move on. One real measurement beats three plausible explanations. A hypothesis that survives only because nobody checked it is worse than no hypothesis: it sends the next person down the wrong path. This applies to your own past claims in the same conversation — if you said the bottleneck was X and the data says Y, lead with the correction.
9. **Prefer loud failure to silent degradation.** When code meets an unexpected state, fail with a message that names what is missing rather than defaulting, skipping, or swallowing. Guards against bad data must also *report* it — a defence that stays quiet turns a loud error into a slow, invisible loss. Let the asymmetry decide: forgetting a permission breaks visibly and points at the fix, while forgetting a revoke does nothing and leaves a hole nobody sees. Choose the failure mode that gets noticed.
10. **Declare your work in project memory before you start, and close it when you stop.** Check lore for other agents' `work/` pages first; write your own (`agentwork · status: in-progress`); update it as the scope changes; close it as `done`, `abandoned`, `paused` or `waiting-response` every time you stop. If another agent's page overlaps yours, **wait and keep checking on your own** until it is released, then proceed without asking the user (see [workflows/project-memory.md](workflows/project-memory.md)).
