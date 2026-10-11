# Blueprint

**Blueprint** takes a software project from an idea in plain language to
requirements and a repository ready for agentic development. You talk to your
coding agent in a guided interview; the agent researches, recommends, writes the
project documents and prepares the environment.

It was called `ai-template` until October 2026.

> **Status: under construction.** The four starting points work today: starting
> a new project, continuing one, and improving or refactoring a project that
> already exists, with the project's state, the answer to "where are we?", the
> research standard, the decisions that are costly to undo, the documents the
> kind of project asks for and the prepared repository, and the CLI has its
> three commands. The previous form of Blueprint, a template
> to copy into a project, was absorbed by the skills and left the repository
> ([what it was](#before-the-skills)).

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
tasks) are optional — and for observability, Blueprint carries
[the page that says when a tool is worth it and when the project's own journal
is the better answer](skills/blueprint-setup/references/observability.md),
because the choice only means something if you know what you are choosing.

---

## Four ways to get it

**1. The Claude Code plugin.** This repository is its own marketplace, so two
commands are the whole of it:

```
claude plugin marketplace add sinteselabs/Blueprint
claude plugin install blueprint@sinteselabs
```

The same thing from inside a session: `/plugin marketplace add
sinteselabs/Blueprint`, then `/plugin install blueprint@sinteselabs`. The
skills then work in every project you open, and nothing is written into your
projects.

**While this repository is private,** a stranger cannot reach it. Anyone with
access clones it and adds the clone instead, which is the same two commands
with a path (measured 11/10/2026):

```
git clone https://github.com/sinteselabs/Blueprint
claude plugin marketplace add ./Blueprint
claude plugin install blueprint@sinteselabs
```

To bring a new version: `claude plugin marketplace update sinteselabs` (from a
clone, `git pull` first). To go back: `claude plugin uninstall
blueprint@sinteselabs`, and `claude plugin marketplace remove sinteselabs`.
Installing puts nothing in your projects and starts nothing running: the
plugin carries skills and no hooks or servers.

**2. The skills folder.** [`skills/`](skills/) follows the open
[Agent Skills](https://agentskills.io) format, so any agent that reads skills
can use it. Ask your agent to install the skills from this repository, or copy
the folders to where your agent looks: `.claude/skills/` for Claude Code,
`.agents/skills/` for Codex and Antigravity.

**3. Your agent's own skills installer.** Because the folder follows the
format, the installers do the copying. Measured on 10 and 11/10/2026, both
bringing all seven skills with their references, templates and the check
script:

```
gemini skills install <path to this repository>/skills --scope workspace
npx skills add https://github.com/sinteselabs/Blueprint
```

**4. The CLI.** In a project folder, with Node 22 or newer:

```
npx blueprintx init
```

It copies the skills where each agent reads them, writes the Blueprint block of
`AGENTS.md`, points `CLAUDE.md` and `GEMINI.md` at it so an agent that reads
only its own file gets the same rules, and records what it installed and in
which version. It never
overwrites a file that is already there, and `--dry-run` shows what it would do
without writing.

```
npx blueprintx check
```

says whether the project is whole and how to fix what is not, and only reads.

```
npx blueprintx update
```

brings the new version of Blueprint's own files, after showing what changes. A
file of Blueprint that you edited is kept, with the new version written beside
it, and your documents, your state and your journal are never touched. While
the package is not published, run it from a clone: `node cli/blueprint.js init`.

---

## How you use it

You say what you want, in your own words: "I want to start a new project", "let's
continue", "where are we?". There is one way in. The agent works out the starting
point from the state of the folder and tells you what it concluded.

The four starting points work this way today: starting, continuing, improving
and refactoring.

---

## Structure

```
.
├── .claude-plugin/          the plugin manifest and the marketplace file: the repository root is the plugin
├── cli/                     the CLI: one command per thing that needs no model
├── skills/                  THE PRODUCT: seven skills in the open Agent Skills format
│   ├── blueprint/           the way in: finds the starting point and conducts the steps
│   ├── blueprint-research/  the standard research process
│   ├── blueprint-decide/    decisions that are costly to undo
│   ├── blueprint-survey/    reads an existing project before asking
│   ├── blueprint-record/    the project's state and journal
│   ├── blueprint-status/    "where are we?"
│   └── blueprint-setup/     prepares the repository; carries the files a project starts from
├── tooling/                 this repository's own tooling: a Langfuse hook for Claude Code and the checks
├── AGENTS.md, CLAUDE.md     instructions for working on Blueprint itself
└── LICENSE                  MIT
```

---

## Before the skills

Until October 2026 Blueprint was a set of Markdown files that a project copied:
an entry point for AI assistants and a guided kickoff that interviewed you and
wrote the project's documents one at a time. The skills absorbed them, and
those files left the repository in October 2026. Copying this repository into a
project is no longer the way to use Blueprint; the three ways above are.

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
