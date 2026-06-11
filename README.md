# ai-template

A reusable **AI context scaffold** for new projects. Copy this structure into any repo so that every AI assistant (Claude Code, Codex, Cursor, etc.) has one consistent, discoverable place to learn how the project works, what the rules are, and where the source of truth lives.

The core idea: **a single entry point.** `AGENTS.md` and `CLAUDE.md` at the repo root do nothing but point to [`.ai/ai.md`](.ai/ai.md). From there, a navigation map sends the assistant to the right file for the topic at hand — architecture, conventions, design, requirements, decisions, or workflow.

---

## Why this exists

Without a convention, AI context ends up scattered across READMEs, stale comments, and chat history. This template fixes that:

- **One entry point** — assistants always start at `.ai/ai.md`.
- **Separation of concerns** — architecture, conventions, UI, requirements, and decisions each live in a dedicated file.
- **Source-of-truth links** — every doc points back to its authoritative source (e.g. a Notion page) so local files stay summaries, not forks.
- **Hard rules up front** — non-negotiable constraints are listed where they can't be missed.
- **Tooling wired in** — `mcp.json` declares the MCP servers (Notion, Firebase, etc.) the project uses.

---

## How to use this template

1. **Copy** the contents of this repo into your new project (everything except this `README.md`'s template-specific notes — keep the structure).
2. **Find & replace** every `{{PLACEHOLDER}}` token and every `TODO:` / `<!-- ... -->` guidance comment with real project content.
3. **Set the entry point** — fill in `.ai/ai.md`: project summary, tech stack, source-of-truth links, the navigation map, and hard rules.
4. **Fill the topic files** — `architecture.md`, `coding_conventions.md`, `ui_guidelines.md`, and the `docs/` summaries. Delete sections that don't apply.
5. **Wire tooling** — edit `mcp.json` for the MCP servers you actually use; delete the rest.
6. **Pick a `.gitignore`** appropriate to your stack (the included one is generic).
7. **Keep it alive** — when a decision changes, update `architecture.md` / `docs/ARD.md`. These files are meant to be maintained, not written once.

> Tip: the fastest way to fill the template is to point your AI assistant at `.ai/ai.md` and have it interview you / read your design docs, then write each file.

---

## Structure

```
.
├── AGENTS.md                    → points to .ai/ai.md (entry point for any AI assistant)
├── CLAUDE.md                    → points to .ai/ai.md (Claude Code reads this by default)
├── mcp.json                     MCP servers the project uses (Notion, Firebase, …)
├── .gitignore                   generic; replace with one for your stack
└── .ai/
    ├── ai.md                    THE ENTRY POINT — project at a glance + navigation map + hard rules
    ├── architecture.md          system architecture, structure, data model, hosting
    ├── coding_conventions.md    language/framework standards, naming, git, security
    ├── ui_guidelines.md         design tokens, typography, components, screens
    ├── config/
    │   └── system.md            the AI's role, behaviour, and hard rules (system prompt)
    ├── docs/
    │   ├── ARD.md               Architecture Decision Records (summary of decisions + rationale)
    │   ├── SRS.md               Software Requirements Specification (features, NFRs, scope)
    │   └── design-doc.md        visual system & component spec summary
    ├── workflows/
    │   ├── notion-workflow.md   how to read/update tasks & docs in Notion (or your PM tool)
    │   └── task-queue.md        sequential list of what to work on next
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
| `.ai/docs/ARD.md` | Decisions and their rationale (ADRs). Local summary of the authoritative source. | When a decision's "why" is needed. |
| `.ai/docs/SRS.md` | Requirements, user stories, NFRs, scope, out-of-scope. | When clarifying what to build. |
| `.ai/docs/design-doc.md` | Visual identity, screens, components, prototypes. | When clarifying how it should look. |
| `.ai/workflows/notion-workflow.md` | How to fetch/update tasks and docs in the PM tool. | When picking up or closing a task. |
| `.ai/workflows/task-queue.md` | Ordered list of tasks to process top-to-bottom. | To decide what's next. |
| `.ai/templates/` | Reusable boilerplate (PR templates, code snippets, doc skeletons). | When generating repetitive artifacts. |
| `.ai/tools/` | Project-specific helper scripts for AI workflows. | When a workflow needs them. |

---

## Conventions baked in

- **Local files are summaries, not sources of truth.** Each links to its authoritative source (Notion, a design tool, etc.). Update both when something changes.
- **Hard rules are explicit and numbered.** They live in `.ai/ai.md` and `.ai/config/system.md` so they can't be missed.
- **`architecture.md` + `docs/ARD.md` are the structural source of truth in-repo.** Change them when decisions change.
- **One topic per file.** Don't dump everything into `ai.md`; it's a map, not the territory.

---

## License

Use freely as a starting point for your own projects.
