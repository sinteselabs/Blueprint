# Blueprint

**Blueprint** takes a software project from an idea in plain language to
requirements and a repository ready for agentic development. You talk to your
coding agent in a guided interview; the agent researches, recommends, writes the
project documents and prepares the environment.

It was called `ai-template` until October 2026.

> **Status: under construction.** The four starting points work today: starting
> a new project, continuing one, and improving or refactoring a project that
> already exists, with the project's state, the answer to "where are we?", the
> research standard and the decisions that are costly to undo. Preparing the
> repository for development is not built yet: that skill says so when it is
> called. The CLI does not exist yet. The previous form of Blueprint, a template
> to copy into a project, is still in [`.ai/`](#the-previous-template) while the
> skills absorb it.

---

## What it is for

Blueprint is for a software project you want to:

- **start**: there is only an idea;
- **continue**: the project went through Blueprint and stopped;
- **improve**: the project exists and you want to add or change something;
- **refactor**: the project exists and will be reorganised inside, which
  includes documenting what is there.

It is designed for Claude Code, which is the main experience, and for Codex and
Antigravity CLI. Nothing external is required: everything mandatory works with
Markdown files. lore (memory), Langfuse (observability) and Notion (documents and
tasks) are optional.

---

## Three ways to get it

**1. The Claude Code plugin.** In Claude Code 2.1.275 or later:

```
/plugin install blueprint --marketplace sinteselabs/Blueprint
```

While this repository is private, that needs access to it.

**2. The skills folder.** [`skills/`](skills/) follows the open
[Agent Skills](https://agentskills.io) format, so any agent that reads skills
can use it. Ask your agent to install the skills from this repository, or copy
the folders to where your agent looks: `.claude/skills/` for Claude Code,
`.agents/skills/` for Codex and Antigravity.

**3. The CLI.** Not built yet. It will install Blueprint in a project folder,
check that everything is in place, and update Blueprint without touching what
you wrote.

---

## How you use it

You say what you want, in your own words: "I want to start a new project", "let's
continue", "where are we?". There is one way in. The agent works out the starting
point from the state of the folder and tells you what it concluded.

Starting and continuing a project work this way today. The rest is still being
built.

---

## Structure

```
.
├── .claude-plugin/          the plugin manifest and the marketplace file: the repository root is the plugin
├── skills/                  THE PRODUCT: seven skills in the open Agent Skills format
│   ├── blueprint/           the way in: finds the starting point and conducts the steps
│   ├── blueprint-research/  the standard research process
│   ├── blueprint-decide/    decisions that are costly to undo
│   ├── blueprint-survey/    reads an existing project before asking
│   ├── blueprint-record/    the project's state and journal
│   ├── blueprint-status/    "where are we?"
│   └── blueprint-setup/     prepares the repository; carries the files a project starts from
├── .ai/                     the previous template, being absorbed into the skills
├── tooling/                 this repository's own tooling: a Langfuse hook for Claude Code and the checks
├── AGENTS.md, CLAUDE.md     instructions for working on Blueprint itself
└── LICENSE                  MIT
```

---

## The previous template

Until October 2026 Blueprint was a set of Markdown files that a project copied:
a single entry point for AI assistants, [`.ai/ai.md`](.ai/ai.md), and a guided
kickoff, [`.ai/workflows/project-kickoff.md`](.ai/workflows/project-kickoff.md),
that interviews you and writes the project's documents one at a time.

Those files are still in `.ai/`, written for a project that copies them. They
are the source material for the skills and leave the repository as the skills
absorb them. Copying this repository into a project is no longer the way to use
Blueprint.

---

## Working on Blueprint

[AGENTS.md](AGENTS.md) has the map and the rules for changing this repository.
[tooling/README.md](tooling/README.md) describes the checks that must pass
before a change is integrated.

---

## License

[MIT](LICENSE). Use it freely.

The license asks one thing: copies of Blueprint's files keep its copyright and
permission notice. Your project's own license is yours to choose.
