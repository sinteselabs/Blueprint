# Working on Blueprint

This file is for people and AI agents changing Blueprint itself. It is not what
Blueprint installs in a project.

## What this repository is

Blueprint takes a software project from an idea in plain language to requirements
and a repository ready for agentic development. It is delivered as agent skills
(the product), a Claude Code plugin that carries them, and a CLI.

The seven skills in `skills/` are written, the CLI has its three commands, and
the method is measured in real sessions of Claude Code, Codex and the
Antigravity CLI. The previous form of Blueprint, a template to copy into a
project, was absorbed by the skills and deleted in October 2026; it is in the
history, and in the repository it came from.

The repository is public, and the CLI is published to npm as `blueprintlabs`. So a
change here reaches people: anything that ships — `skills/`, `cli/`, `LICENSE`,
`README.md` — is public the moment it is released.

## Map

| Path | What it is |
|---|---|
| `skills/` | The product: one folder per skill, in the open Agent Skills format |
| `.claude-plugin/` | The plugin manifest and the marketplace file. The repository root is the plugin root |
| `cli/` | The CLI: `init`, `check` and `update`. Node, no dependencies. Shipped to people, together with `skills/`. The check itself lives in `skills/blueprint-status/check.js`, so the CLI and an agent run the same file |
| `tooling/` | This repository's own tooling: the checks that guard a change, and the tests that run Blueprint in real agent sessions. Not shipped to anyone, and the plugin never loads or runs any of it |

## Rules

1. **English.** Every file in this repository is written in English.
2. **Nothing at the root that the plugin would load.** Because the root is the
   plugin root, never add any of these there: `.mcp.json`, `.lsp.json`,
   `settings.json`, `hooks/`, `agents/`, `commands/`, `bin/`, `output-styles/`,
   `workflows/`, `themes/`, `monitors/`. `check_root_names.py` guards this.
3. **Skills follow the format.** A skill is a folder under `skills/` with a
   `SKILL.md`. The folder name equals the `name` in its frontmatter, and the
   `description` says what the skill does and when to use it. `SKILL.md` stays
   under 500 lines, with detail in `references/` and templates in `assets/`. A
   skill points only at files inside its own folder.
4. **No local configuration and no keys in git.** `.env`, `.ai-memory.toml`,
   `.claude/` and anything that binds a clone to one person's tools stay out.
   The files a project starts from live in
   `skills/blueprint-setup/assets/project-files/`, with an `.example` suffix.
5. **Blueprint is a general tool.** It carries no team's internal process and no
   client-service documents.
6. **Say when something does not work.** A skill, a script or a check that
   cannot do its job says so. It never degrades silently.
7. **Small commits, one concern each.**

## Before integrating a change

Run, from the repository root:

```
python tooling/checks/check_links.py
python tooling/checks/check_root_names.py
python tooling/checks/check_skills.py
python tooling/checks/check_shared_text.py
python tooling/checks/check_state.py
python tooling/checks/test_checks.py
npm test
claude plugin validate .
```

`npm test` runs the CLI's own tests with Node's test runner, and needs Node 22
or newer; there are no dependencies to install. Every one of these also runs on
GitHub, on every push, and the CLI's tests run there on Windows, macOS and
Linux with Node 22 and 24 (`.github/workflows/checks.yml`). `claude plugin
validate` is the one gate that stays local: it needs Claude Code, and it has to
pass with no warnings. What each check guards is in
[tooling/README.md](tooling/README.md).

**This file is the one that holds the rules, and there is no `CLAUDE.md` beside
it on purpose.** The repository root is the plugin root, so a `CLAUDE.md` here
ships to everyone who installs the plugin and is loaded by nobody — the
validator says so. Claude Code reads `AGENTS.md` when a folder has no
`CLAUDE.md`, which is this case. If your Claude Code does not pick it up, say
so rather than adding a `CLAUDE.md` back: the fallback depends on a feature
flag, and `/config` has the setting under project instructions.

That asymmetry is deliberate and does not apply to the projects Blueprint
prepares. There, the CLI and `blueprint-setup` do write `CLAUDE.md` and
`GEMINI.md` pointing at `AGENTS.md`, because a project folder is not a plugin
root and a silent fallback is not good enough for someone else's repository.

## Project memory

To use lore while working on Blueprint, make your own `.ai-memory.toml` at the
root from `skills/blueprint-setup/assets/project-files/ai-memory.toml.example`.
It is git-ignored here on purpose.
