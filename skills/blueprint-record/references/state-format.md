# The project state file

`.blueprint/state.md` is where a Blueprint project remembers where it is. A
conversation with an agent has a limit and ends; this file does not. Any agent,
in any session, resumes from it, and "where are we?" is answered from it.

One file has three readers: the agent, the project check and the person. So the
keys and headings are fixed and in English, and what is written under them is in
the project's document language.

Format number: **1**. Template: [state.md](../assets/state.md). A filled example:
[state.example.md](../assets/state.example.md).

## Shape

A header of fixed fields between two `---` lines, then ten fixed sections.

## Header

One `key: value` per line. No nesting, no lists, no quotes.

| Key | Value |
|---|---|
| `blueprint_state` | The format number: `1` |
| `project` | The project's name |
| `starting_point` | How the project came to Blueprint: `start`, `improve` or `refactor` |
| `document_language` | The language the documents are written in, as the person said it: `pt-BR`, `English` |
| `developers` | How many people develop the project: a whole number, 1 or more |
| `documents_at` | Where the documents live: a folder such as `docs/`, or the name of a tool such as `notion` |
| `tasks_at` | Where the tasks live: a file or a folder, or the name of a tool |
| `memory` | `journal`, or the name of the tool that keeps the project's memory |
| `observability` | `journal`, or the name of the tool that records the sessions |
| `updated` | When the file was last saved, in UTC: `2026-10-09T15:30:00Z` |
| `updated_by` | The agent that saved it: `Claude Code`, `Codex`, `Antigravity CLI` |

Continuing a project is not a starting point. It is what this file makes possible.

## Sections

Each is a second-level heading, spelled exactly as below and in this order.

### `## Project kind`

The five facts that decide which documents the project gets, in a table with the
columns `Fact`, `Value` and `Known how`, one row per fact:

| Fact | Value | Known how |
|---|---|---|
| `has-screens`, `stores-data`, `holds-personal-data`, `used-by-command-or-code`, `calls-a-model` | `yes`, `no` or `unknown` | `said` when the person stated it, `deduced` when the agent inferred it, `-` while unknown |

Below the table, one line starting with `Deduced:` says in plain words what kind
of project this is.

### `## Criteria the person declared`

A list of what the person said limits or guides the choices: budget, deadline,
what they already use, what they refuse. A recommendation is made by these
criteria when the research does not single out one option. While it is empty,
one line says there is nothing yet.

### `## Steps`

A table with the columns `Step`, `Situation` and `Main questions`, one row for
each of the five steps: `system-description`, `requirements`, `modeling`,
`architecture`, `plan`.

| Situation | Meaning |
|---|---|
| `not-started` | No main question of the step was asked yet |
| `open` | A main question still has no answer |
| `advanced` | Every main question is answered. The next step may start, and this step's document is still being written |
| `closed` | The step's document is ready |

`Main questions` is written `2 of 4`: how many are answered, of how many. A step
never waits for approval, and more than one step may be under way at once.

### `## Documents`

A table with the columns `Document`, `Situation` and `Where`, one row per
document the project will have. Six are in every project: `system-description`,
`requirements`, `research`, `architecture`, `decisions`, `plan`. The others
appear when the project kind asks for them: `use-cases`, `data-model`,
`data-classification`, `wireframes`, `design`, `interface-contract`,
`ai-features`, `test-plan`, `playbooks`.

Which of the others a project gets follows from its kind:

<!-- shared: documents-by-kind -->
| Document | In the project when |
|---|---|
| `use-cases` | People use the product through journeys, step by step |
| `data-model` | `stores-data` is `yes` |
| `data-classification` | `holds-personal-data` is `yes` |
| `wireframes` | `has-screens` is `yes` |
| `design` | `has-screens` is `yes` and the visual identity is still to be decided |
| `interface-contract` | `used-by-command-or-code` is `yes` |
| `ai-features` | `calls-a-model` is `yes` |
| `test-plan` | Something must be validated beyond acceptance, the project is a refactor, or a decision left something to test |
| `playbooks` | `developers` is more than 1 |
<!-- /shared: documents-by-kind -->

A document whose fact is still `unknown` is not listed yet. It is added when the
fact becomes `yes`.

`Situation` is `not-started`, `in-progress` or `ready`. There is no "approved":
the person reads a document only if they want to. `Where` is the path or link of
the document, or `-` while there is none.

### `## Main questions`

One third-level heading per step, named with the step, and under it a checklist
of the step's main questions: `- [x]` answered, `- [ ]` not yet. The counts must
agree with the `Steps` table.

### `## Refinement questions left for later`

A checklist of questions that were not needed to move on. Each says which step it
belongs to and what it will be needed for. They are asked one at a time, only
when the agent cannot go on without the answer. While it is empty, one line says
there is nothing yet.

### `## Answers`

What the person answered, by block. One third-level heading per block, written
`### <step> · <block title>`, and under it a few lines. This is the record that
keeps the agent from asking twice.

### `## Decisions`

A list with one line per decision: its number in the decisions record, its
title, and `decided` or `open`. The reasons live in the decisions record, not
here. While it is empty, one line says there is nothing yet.

### `## Open points`

A list of what is unresolved and who it depends on. While it is empty, one line
says there is nothing yet.

### `## Next question`

The next question to ask, in the words it will be asked. When there is none, what
happens next.

## Rules for whoever writes the file

1. Save at the end of every block of questions, not at the end of the session.
2. Set `updated` and `updated_by` on every save.
3. Never write a key, a token or a password in it.
4. Never drop what was answered. Correct an answer in place and keep the rest.
5. Say in one line what was saved.

## What the project check verifies

- The header has every key, the format number is one the check knows, and each
  value is of the kind the table above asks for.
- The ten sections are there, in order.
- The three tables have their rows and only the values listed above.
- For each step, the checklist under `Main questions` agrees with the `Steps`
  table, and the situation agrees with the counts: `not-started` has none
  answered, `advanced` and `closed` have all of them.
- No template placeholder, `{{...}}`, is left.
