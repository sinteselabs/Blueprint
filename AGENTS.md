# Working on Blueprint

This file is for people and AI agents changing Blueprint itself. It is not what
Blueprint installs in a project.

## What this repository is

Blueprint takes a software project from an idea in plain language to requirements
and a repository ready for agentic development. It is delivered as agent skills
(the product), a Claude Code plugin that carries them, and a CLI.

It is under construction. The seven skills in `skills/` are written and the CLI
has its three commands. What is left is the testing in the other agents and the
publication. The previous form of Blueprint, a template
to copy into a project, was absorbed by the skills and deleted in October 2026;
it is in the history, and in the repository it came from.

## Map

| Path | What it is |
|---|---|
| `skills/` | The product: one folder per skill, in the open Agent Skills format |
| `.claude-plugin/` | The plugin manifest and the marketplace file. The repository root is the plugin root |
| `cli/` | The CLI: `init`, `check` and `update`. Node, no dependencies. Shipped to people, together with `skills/`. The check itself lives in `skills/blueprint-status/check.js`, so the CLI and an agent run the same file |
| `tooling/` | This repository's own tooling (a Langfuse hook for Claude Code, the checks). Not shipped to anyone |

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
python tooling/checks/test_langfuse_hook.py
npm test
claude plugin validate .
```

`npm test` runs the CLI's own tests with Node's test runner, and needs Node 22
or newer; there are no dependencies to install. Every one of these also runs on
GitHub, on every push, and the CLI's tests run there on Windows, macOS and
Linux with Node 22 and 24 (`.github/workflows/checks.yml`). `claude plugin
validate` is the one gate that stays local: it needs Claude Code. It reports one expected warning: a
`CLAUDE.md` at the plugin root is not loaded as plugin context. What each check
guards is in [tooling/README.md](tooling/README.md).

## Project memory

To use lore while working on Blueprint, make your own `.ai-memory.toml` at the
root from `skills/blueprint-setup/assets/project-files/ai-memory.toml.example`.
It is git-ignored here on purpose.
