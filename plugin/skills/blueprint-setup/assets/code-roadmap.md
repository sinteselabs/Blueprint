# Code roadmap

<!-- Template. Write the document in the project's document language, headings
and labels included. One file per project, whether one person develops it or a
team. Replace every {{placeholder}}, drop a section that does not apply, and
remove these comments. Paths go in backticks, relative to the project root: the
project check reads them. A row for code that does not exist yet goes between
the two planned marks at the end, and moves up into the tables when the code is
written. The marks stay exactly as they are. -->

> **In short:** {{Up to three lines: how the code is organised, and the rule that tells where a new piece goes.}}

## How to use it

Find the task's area in the table below, and read only the paths on its row and
the ones under "Also read", and that area's line under "Gotchas". Run that area's
tests while you work, and the whole suite before you deliver. Open any other
file only when the task needs it, and when you did, add it here in the same
commit. Write code the way "How code is written here" says.

## Areas

<!-- "Its tests alone" is the command that runs only that area's tests, taken
from the project's test runner and its configuration: a path or a pattern given
to it. Leave the cell empty when the runner cannot select them, and say so once
under the table. A command with spaces in backticks is not read as a path. -->

| Area | Path | What lives there | Read it when the task | Also read | Its tests alone |
|---|---|---|---|---|---|
| {{Orders}} | {{`src/orders/`}} | {{Creating, listing and cancelling orders}} | {{creates or changes an order}} | {{`src/db/schema.sql`}} | {{`npx vitest run src/orders`}} |

## Gotchas

<!-- One line per area that has one: a fact about the code that the next agent
would otherwise learn by breaking something. Empty at setup unless the code or
its comments already say one; a task that learns one adds it. -->

- **{{Orders}}:** {{An order's total is recomputed on save, so a test that sets it by hand fails.}}

## Entry points

| What starts | File |
|---|---|
| {{The server}} | {{`src/server.js`}} |

## Shared code

| Path | What it is | Changing it affects |
|---|---|---|
| {{`src/db/`}} | {{Database connection and queries}} | {{Every area that stores data}} |

## How code is written here

<!-- Only what the project's own files or its decisions say: the linter and
formatter configuration, the test runner's, the migration tool's, the commit
history, the decisions record. Each line names where it comes from. Leave out a
line nothing says, and never write a convention the project does not have:
"none set" is an answer. Where there is no code yet, take them from the stack
decision, and write each as the task that sets it up. -->

- **Names:** {{Files in kebab-case, types in PascalCase · seen in `src/`}}
- **Format and lint:** {{Prettier and ESLint, run by `npm run lint` · `eslint.config.js`}}
- **Errors:** {{How an error reaches the caller or the person: a typed result, an exception caught at one place · D-003}}
- **Data migrations:** {{One file per change, never edited once applied · `migrations/`}}
- **Branches and commits:** {{`feat/` and `fix/` branches, Conventional Commits · the history}}

## Do not read

{{Generated, vendored or bulky paths an agent has no reason to open: `node_modules/`, `dist/`, lock files, data dumps.}}

## Keeping it true

A commit that creates, moves, renames or deletes a folder or an important file
changes this roadmap in the same commit, and so does one that changes how an
area's tests run or a convention above. A row whose path no longer exists is
wrong, and an agent that trusts it reads the wrong thing.

<!-- blueprint:planned -->
## Planned

| Area | Path | What will live there | Task |
|---|---|---|---|
| {{Orders}} | {{`src/orders/`}} | {{Creating and cancelling orders}} | {{01-02 Task name}} |
<!-- /blueprint:planned -->
