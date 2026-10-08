# Blueprint

**Blueprint** was called `ai-template` until October 2026, and the GitHub repository still carries that name.

A reusable **AI context scaffold** for new projects. Copy this structure into any repo so that every AI assistant (Claude Code, Codex, Cursor, etc.) has one consistent, discoverable place to learn how the project works, what the rules are, and where the source of truth lives.

The core idea: **a single entry point.** `AGENTS.md` and `CLAUDE.md` at the repo root do nothing but point to [`.ai/ai.md`](.ai/ai.md). From there, a navigation map sends the assistant to the right file for the topic at hand — architecture, conventions, design, requirements, decisions, or workflow.

---

## Why this exists

Without a convention, AI context ends up scattered across READMEs, stale comments, and chat history. This template fixes that:

- **One entry point** — assistants always start at `.ai/ai.md`.
- **Separation of concerns** — architecture, conventions, UI, requirements, and decisions each live in a dedicated file.
- **Source-of-truth links** — every doc points back to its authoritative source (e.g. a Notion page) so local files stay summaries, not forks.
- **Hard rules up front** — non-negotiable constraints are listed where they can't be missed.
- **Tooling wired in** — `.mcp.json` declares the MCP servers (Notion, Firebase, etc.) the project uses.
- **Project memory by default** — every project uses [lore](.ai/workflows/project-memory.md) as the agents' shared long-term memory: what happened, handoffs between agents, and who is working on what right now. It sits beside the PM tool and the repo docs; it doesn't replace them.
- **Autonomous runs (optional)**: say "autonomous run" and the agents work through the pending tasks on their own, for example overnight. They coordinate through lore, take the recommended option where a decision would be yours, record it for review, and leave you a to-do list. Kickoff asks whether to enable it ([workflow](.ai/workflows/autonomous-run.md)).

---

## How to use this template

1. **Copy** the contents of this repo into your new project (everything except this `README.md`'s template-specific notes — keep the structure).
2. **Find & replace** every `{{PLACEHOLDER}}` token and every `TODO:` / `<!-- ... -->` guidance comment with real project content.
3. **Set the entry point** — fill in `.ai/ai.md`: project summary, tech stack, source-of-truth links, the navigation map, and hard rules.
4. **Fill the topic files** — `architecture.md`, `coding_conventions.md`, `ui_guidelines.md`, and the `docs/` summaries. Delete sections that don't apply.
5. **Wire tooling** — edit `.mcp.json` for the MCP servers you actually use; delete the rest.
6. **Connect project memory** — fill `.ai-memory.toml` with the lore workspace and project, commit it, and register lore once per machine (never in `.mcp.json`). Steps in [`.ai/workflows/project-memory.md`](.ai/workflows/project-memory.md).
7. **Pick a `.gitignore`** appropriate to your stack (the included one is generic).
8. **Keep it alive** — when a decision changes, update `architecture.md` / `docs/ARD.md`. These files are meant to be maintained, not written once.

> Tip: for a brand-new project, point your AI assistant at [`.ai/workflows/project-kickoff.md`](.ai/workflows/project-kickoff.md). It runs a guided, step-by-step interview and produces the core Software Engineering documents in order — System Description → SRS → Use Cases → Data Model → Wireframes → Architecture → Design Doc — saving each to your chosen store (Notion by default). For an existing project, point it at `.ai/ai.md` and have it read your design docs, then write each file.

---

## Structure

```
.
├── AGENTS.md                    → points to .ai/ai.md (entry point for any AI assistant)
├── CLAUDE.md                    → points to .ai/ai.md (Claude Code reads this by default)
├── .mcp.json                    MCP servers the project uses (Notion, Firebase, …); lore is registered per machine instead
├── .ai-memory.toml              names this repo's project memory in lore (workspace + project); committed
├── .gitignore                   generic; replace with one for your stack
└── .ai/
    ├── ai.md                    THE ENTRY POINT — project at a glance + navigation map + hard rules
    ├── architecture.md          system architecture, structure, data model, hosting
    ├── coding_conventions.md    language/framework standards, naming, git, security
    ├── ui_guidelines.md         design tokens, typography, components, screens
    ├── config/
    │   └── system.md            the AI's role, behaviour, and hard rules (system prompt)
    ├── docs/
    │   ├── system-description.md wide-angle system overview (users, goals, scope)
    │   ├── SRS.md               Software Requirements Specification (features, NFRs, scope)
    │   ├── use-cases.md         actors, use cases, diagrams, user flows
    │   ├── data-model.md        entities, schema, types, ERD, class diagrams
    │   ├── wireframes.md        low-fidelity screens per target device
    │   ├── ARD.md               Architecture Decision Records (summary of decisions + rationale)
    │   └── design-doc.md        visual system & component spec summary
    ├── workflows/
    │   ├── project-kickoff.md   guided, step-by-step generation of the docs above for a new project
    │   ├── notion-workflow.md   how to read/update tasks & docs in Notion (or your PM tool)
    │   ├── task-queue.md        sequential list of what to work on next
    │   ├── parallel-agents.md   git worktree isolation when several agents run at once
    │   ├── project-memory.md    lore: what it's for, setup, and the declare-your-work rule
    │   └── autonomous-run.md    optional: agents working through tasks unattended, coordinated via lore
    ├── templates/               reusable snippets/boilerplate for the project (optional)
    └── tools/                   project-specific scripts/helpers for AI workflows (optional)
```

---

## File-by-file guide

| File | Purpose | When the assistant reads it |
|---|---|---|
| `AGENTS.md` / `CLAUDE.md` | Thin redirects to `.ai/ai.md`. | First, automatically. |
| `.ai/ai.md` | The map. Project summary, tech stack, source-of-truth links, navigation table, hard rules. | Every session, first. |
| `.ai/architecture.md` | How the system is built: services, structure, data model, hosting, key flows. | Before any structural change. |
| `.ai/coding_conventions.md` | Language/framework standards, naming, testing, git, security. | Before writing code. |
| `.ai/ui_guidelines.md` | Colour tokens, typography, components, screens, interaction patterns. | Before UI work. |
| `.ai/config/system.md` | The AI's role, behaviour constraints, and hard rules — the "system prompt". | As standing instructions. |
| `.ai/docs/system-description.md` | Wide-angle system overview: problem, users/actors, goals, scope. | First, when framing a new project. |
| `.ai/docs/ARD.md` | Decisions and their rationale (ARD entries, `ARD-01`…). Local summary of the authoritative source. | When a decision's "why" is needed. |
| `.ai/docs/SRS.md` | Requirements, user stories, NFRs, scope, out-of-scope. | When clarifying what to build. |
| `.ai/docs/use-cases.md` | Actors, use cases, use-case diagrams, and user flows. | When clarifying how users interact. |
| `.ai/docs/data-model.md` | Entities, fields/types, ERD, class diagrams, data rules. | When clarifying what the system stores. |
| `.ai/docs/wireframes.md` | Low-fidelity screen layouts per target device. | When clarifying screen structure/flow. |
| `.ai/docs/design-doc.md` | Visual identity, screens, components, prototypes. | When clarifying how it should look. |
| `.ai/workflows/project-kickoff.md` | Guided, step-by-step interview that generates all the docs above, in order, for a new project. | When starting a brand-new project. |
| `.ai/workflows/notion-workflow.md` | How to fetch/update tasks and docs — Notion **or** local Markdown; Documents Hub / Task Tracker schemas + task naming/ordering. | When picking up or closing a task. |
| `.ai/workflows/task-queue.md` | Ordered list of tasks to process top-to-bottom. | To decide what's next. |
| `.ai-memory.toml` | Names the repo's project memory in lore (`workspace`, `project`). Committed, so every clone shares one memory. | By the capture hooks and MCP clients, automatically. |
| `.ai/workflows/project-memory.md` | lore as project memory: what goes there vs. the PM tool and the repo, per-machine setup, and the rule that every agent declares its work before starting and waits on overlaps. | Before starting any task. |
| `.ai/workflows/parallel-agents.md` | How to isolate concurrent agents: one git worktree + one branch each, shared-state caveats, integration and cleanup. | Before spawning agents that work in parallel. |
| `.ai/workflows/autonomous-run.md` | Optional, enabled at kickoff. How agents work through the pending tasks unattended: the three kickoff questions, the board and claims in lore, collision rules, recorded decisions, to-dos for the user, and end-of-run summaries. | When the user says "autonomous run". |
| `.ai/templates/` | Reusable boilerplate (PR templates, code snippets, doc skeletons). | When generating repetitive artifacts. |
| `.ai/tools/` | Project-specific helper scripts for AI workflows. | When a workflow needs them. |

---

## Conventions baked in

- **Local files are summaries, not sources of truth.** Each links to its authoritative source (Notion, a design tool, etc.). Update both when something changes.
- **Hard rules are explicit and numbered.** They live in `.ai/ai.md` and `.ai/config/system.md` so they can't be missed.
- **`architecture.md` + `docs/ARD.md` are the structural source of truth in-repo.** Change them when decisions change.
- **Plan in the PM tool, decide in the repo, remember and coordinate in lore.** One fact lives in one place.
- **Agents declare their work in project memory** before starting, wait on their own when another agent holds what they need, and close their page when they stop.
- **`Done` follows the user's test.** Agents set `To test`; when the user says a task is tested and done, the agent may set `Done`.
- **One topic per file.** Don't dump everything into `ai.md`; it's a map, not the territory.

---

## License

Use freely as a starting point for your own projects.
