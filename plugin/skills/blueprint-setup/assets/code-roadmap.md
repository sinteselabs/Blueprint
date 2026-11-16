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
the ones under "Also read". Open any other file only when the task needs it, and
when you did, add it here in the same commit.

## Areas

| Area | Path | What lives there | Read it when the task | Also read |
|---|---|---|---|---|
| {{Orders}} | {{`src/orders/`}} | {{Creating, listing and cancelling orders}} | {{creates or changes an order}} | {{`src/db/schema.sql`}} |

## Entry points

| What starts | File |
|---|---|
| {{The server}} | {{`src/server.js`}} |

## Shared code

| Path | What it is | Changing it affects |
|---|---|---|
| {{`src/db/`}} | {{Database connection and queries}} | {{Every area that stores data}} |

## Do not read

{{Generated, vendored or bulky paths an agent has no reason to open: `node_modules/`, `dist/`, lock files, data dumps.}}

## Keeping it true

A commit that creates, moves, renames or deletes a folder or an important file
changes this roadmap in the same commit. A row whose path no longer exists is
wrong, and an agent that trusts it reads the wrong thing.

<!-- blueprint:planned -->
## Planned

| Area | Path | What will live there | Task |
|---|---|---|---|
| {{Orders}} | {{`src/orders/`}} | {{Creating and cancelling orders}} | {{01-02 Task name}} |
<!-- /blueprint:planned -->
