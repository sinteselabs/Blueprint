<div align="center">

# 🧭 Blueprint

> **From plain words to a repository ready for agentic development.**

You describe the project you want. Blueprint interviews you, researches the
choices, writes the requirements and hands back a repository where any coding
agent already knows the rules, the plan and where to record what it did.

[![npm](https://img.shields.io/npm/v/blueprintlabs?label=blueprintlabs)](https://www.npmjs.com/package/blueprintlabs)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Node](https://img.shields.io/badge/node-%E2%89%A522-brightgreen)](package.json)
[![Agent Skills](https://img.shields.io/badge/format-Agent%20Skills-blue)](https://agentskills.io)

</div>

---

## Why Blueprint

A coding agent will build whatever you ask, immediately, from whatever you said.
That is the problem. The code arrives fast and faithful to a sentence, not to
the project you had in mind — and three weeks later nobody can say why it was
built that way.

What is usually missing is not the code. It is everything before it:

- **The questions nobody asked.** What is out of scope, what happens when it
  fails, whether there is personal data, who pays for what. An agent guesses
  these, silently, and the guesses become architecture.
- **The research.** Picking a stack, a host or a database from what sounds
  likely rather than from what was read today.
- **The reason.** A decision with no reason attached is a decision you cannot
  revisit, only reverse.
- **The handover.** A new session, a new machine, a different agent: the context
  is gone and you explain the project again.

Blueprint is the part before the code, done properly, by the agent you already
use:

- **It asks one block of questions at a time** and never invents what you did
  not say.
- **It researches while you answer** — similar tools, stack, known limits — and
  every recommendation names its sources and their date.
- **A decision that is costly to undo is always yours.** The agent brings
  options and one recommendation, and waits.
- **It writes the documents** in your language: requirements, research,
  architecture, the decisions with their reasons, a plan with one spec per task,
  and the others your kind of project asks for.
- **It leaves the repository ready**, so the next session — any session, any
  agent — opens the folder and knows what to do.
- **Nothing is mandatory but files.** No server, no account, no model of ours.
  Your project never leaves your machine because of Blueprint.

## Works with any agent

Blueprint is Markdown. The method lives in seven folders in the open
[Agent Skills](https://agentskills.io) format, which is a filename convention
and plain text — no SDK, no API, no model of its own. Any coding agent that
reads skills can run it, whatever LLM is behind it.

| Where | How it gets there | State |
|---|---|---|
| **Claude Code** | Plugin, claude.ai, the skills folder, or the CLI | **Best supported.** Where it is developed, and measured end to end in real sessions |
| **Codex** | The skills folder or the CLI | **Measured** in real sessions: it finds the entry skill on its own, says which step the conversation is in, and continues a project started elsewhere |
| **Antigravity CLI** (`gemini`) | Its own installer, the skills folder, or the CLI | **Measured**, except a model turn: it discovers every skill and reads the entry file |
| **Any other agent that reads skills** | The skills folder, or its own installer | Should work, and is not measured. The format is the same for everyone |
| **An agent with no skills at all** | — | The prepared repository still works. `AGENTS.md`, the documents and the plan are plain Markdown that anything can read |

Windows, macOS and Linux, tested on all three with Node 22 and 24.

## How it works

```
         YOU                              what you say, in your own words
          │
          v
    YOUR CODING AGENT  ◄──────  the seven Blueprint skills
          │
          │  one block of questions at a time, research in between
          v
   ┌──────────────────────────────────────────────────────┐
   │  docs/            requirements, research, decisions, │
   │                   architecture, the plan, the specs  │
   │  .blueprint/      where the project is, the journal  │
   │  AGENTS.md        the rules, for the next session    │
   └──────────────────────────────────────────────────────┘
          │
          v
    DEVELOPMENT, task by task, from the plan
```

The state of the interview lives in a file, so it stops and resumes — tomorrow,
on another machine, with another agent — without asking you anything twice.

## Four starting points

You say what you want, in your own words. There is one way in, and the agent
works out where you are from the state of the folder.

| You have | You say | What it does |
|---|---|---|
| Only an idea | *"I want to start a new project"* | Interviews, researches, writes the documents, prepares the repository |
| A project that went through Blueprint and stopped | *"let's carry on"* | Reads what exists and resumes from the question it stopped on |
| A project that exists, and something to add | *"I want to add payments"* | Reads the code first, then specifies only the change |
| A project that exists, to reorganise inside | *"this file does too much"* | Documents what is there, writes what must keep working, then the change |

A small change does not become a document. It becomes one task with its spec.

## Quick start

Pick one. All four give you the same eight skills.

### 1. Claude Code, from the terminal

```bash
claude plugin marketplace add sinteselabs/Blueprint
claude plugin install blueprint@sinteselabs
```

From inside a session, the same two with a slash: `/plugin marketplace add
sinteselabs/Blueprint`, then `/plugin install blueprint@sinteselabs`. The skills
work in every project you open, and nothing is written into your projects.

### 2. claude.ai, the desktop app and Cowork

Open **[Customize → Plugins](https://claude.ai/customize/plugins)**, then
**Add → Add marketplace**, and paste:

```
sinteselabs/Blueprint
```

Installed this way it is saved to your account, so it also turns up in Cowork
and in Claude Code the next time you start a session signed in to the same
account. (There is no link that installs it in one click — pasting the
`owner/repo` above into that dialog is the short path.)

### 3. Your agent's own skills installer

Because the folder follows the format, the installers do the copying:

```bash
# any agent, via the generic installer
npx skills add https://github.com/sinteselabs/Blueprint

# Antigravity CLI
gemini skills install https://github.com/sinteselabs/Blueprint --scope workspace
```

On Windows, that last one clones and then fails clearing its own temporary
folder (`EBUSY`), which is a bug in the installer. Clone the repository and give
it the path instead: `gemini skills install ./Blueprint/skills --scope
workspace`.

### 4. The CLI, in one project folder

Node 22 or newer, no dependencies to install:

```bash
npx blueprintlabs init
```

It copies the skills where each agent reads them, writes the Blueprint block of
`AGENTS.md`, points `CLAUDE.md` and `GEMINI.md` at it so an agent that reads
only its own file gets the same rules, and records what it installed and in
which version. It never overwrites a file that is already there, and
`--dry-run` shows what it would do without writing.

```bash
npx blueprintlabs check     # is the project whole? only reads
npx blueprintlabs update    # bring the new version, showing what changes first
```

`update` touches only Blueprint's own files, and only the ones you have not
edited. A file of Blueprint that you changed is kept, with the new version
written beside it. Your documents, your state and your journal are never
touched.

Then open your coding agent in the folder and say what you want to do.

## What you get

Six documents in every project, and the rest only when your project asks for
them — screens, stored data, personal data, an interface used by command or by
code, a product that calls a model.

| Always | When the project calls for it |
|---|---|
| System description | Use cases and flows |
| Requirements | Data model |
| Research, with dated sources | Data classification |
| Architecture | Wireframes, design |
| Decisions, each with its reason | Interface contract |
| The plan, one spec per task | AI features of the product |
| | Test plan, playbooks per role |

Every task the agent finishes ends with how to test it: what you run or open,
and what you should see.

## The eight skills

| Skill | What it does |
|---|---|
| `blueprint` | The way in. Finds the starting point and conducts the steps |
| `blueprint-research` | The standard research process: dated sources, your criteria, one recommendation |
| `blueprint-decide` | Decisions that are costly to undo: options, a recommendation, and your answer |
| `blueprint-survey` | Reads an existing project before asking anything |
| `blueprint-record` | The project's state and journal, and what it learns about how you work |
| `blueprint-status` | "Where are we?", answered from the files, and the project check |
| `blueprint-setup` | Prepares the repository: the entry file, the journal, the playbooks |
| `blueprint-explain` | Answers why a line of code is the way it is, from the code: the review brief, the tour |

## What stays yours

- **Nothing is sent anywhere.** Blueprint has no server and no telemetry. It is
  instructions your agent follows, inside the permissions you already gave it.
- **Installing runs nothing.** The plugin carries skills, not hooks or servers.
  The only script in the product is the project check, and it only reads.
- **Keys never reach a file of the project,** and never the journal.
- **Outside the project folder,** the agent reads only with your permission, and
  only folder names and Blueprint's own state.

One thing to be precise about, because the folder contains it: **`tooling/` is
this repository's own tooling and is not part of the product.** The plugin
never loads or runs any of it. It holds the checks that guard a change here
and the tests that run Blueprint in real agent sessions, and it reaches the
network for nothing. It travels in the plugin folder only because the
repository root is the plugin root. Nothing installs it, nothing calls it, and
deleting it would change nothing for anyone who uses Blueprint.

## Optional, never required

Everything mandatory works with Markdown files alone (that is a requirement, not
a fallback). These make it nicer, and Blueprint tells you when one of them is
worth it instead of just asking:

- **Memory across projects** — a folder of your own outside the projects, created
  only if you say yes, or [lore](https://github.com/akitaonrails/ai-memory) if
  you use it.
- **Observability** — the project's journal, written in files, or
  [Langfuse](https://langfuse.com). Which one to pick, and when it is not worth
  it at all, is in
  [the observability page](skills/blueprint-setup/references/observability.md).
- **Notion** — the documents and the tasks go there instead of into files.

## Documentation

| For | Where |
|---|---|
| How the method works, step by step | Each skill's `SKILL.md` under [`skills/`](skills/) |
| What the project check verifies | [`skills/blueprint-status/references/check-list.md`](skills/blueprint-status/references/check-list.md) |
| The state file's format | [`skills/blueprint-record/references/state-format.md`](skills/blueprint-record/references/state-format.md) |
| Observability: when a tool is worth it | [`skills/blueprint-setup/references/observability.md`](skills/blueprint-setup/references/observability.md) |
| Working on Blueprint itself | [`AGENTS.md`](AGENTS.md) |
| This repository's own tooling and checks | [`tooling/README.md`](tooling/README.md) |

## Contributing

Issues and pull requests are welcome. Before opening one, two things worth
knowing: every file in this repository is written in English, and a change has
to pass the checks in [`AGENTS.md`](AGENTS.md) — seven Python checks, the CLI's
tests on three operating systems, and the plugin validator.

The most useful thing you can send is a real run that went wrong: what you
asked, what the agent did, and what you expected instead.

## License

[MIT](LICENSE). Use it freely.

The license asks one thing: copies of Blueprint's files keep its copyright and
permission notice. Your project's own license is yours to choose.
