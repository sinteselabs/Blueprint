# Plan

<!-- Template. Write the document in the project's document language, headings
and labels included. Replace every {{placeholder}} and remove these comments.
Every task has a spec of its own, in the specs folder beside this file. -->

**Project:** {{PROJECT_NAME}} · **Version:** {{0.1}} · **Date:** {{YYYY-MM-DD}}

> **In short:** {{Up to five lines: how many phases and tasks, what comes first and why.}}

## How the work goes

- One task at a time, in the order below. A task starts only when the tasks it needs are done.
- A task fits in one delivery someone can review in one sitting: about 400 changed
  lines or 10 files. One that will not fit is split before it starts.
- A task is delivered with how to test it: what to run or open, and what should be seen.
- {{Who marks a task as done, and anything else the person asked for.}}

### Every task is done when

<!-- The definition of done all tasks share. A task's own "Done when" adds to
it and never repeats it. Keep only the lines this project can check. -->

- Its spec's "Done when" is checked, and "Result of the delivery" and "How to test" are written.
- {{The tests run and pass: the command, from "How it is built and checked".}}
- {{The checks that run on every change pass: lint, types, the project check.}}
- The code roadmap names any folder the task created, moved or deleted.

## How it is built and checked

<!-- What an agent needs before the first task: how to run the project, how it
is tested, and how a version reaches the people who use it. Taken from the
architecture and the decisions. Drop a row that does not apply: a tool used by
one person on their own machine has no staging and no release. A command that
does not exist yet names the task that creates it. -->

| What | How | Set up by |
|---|---|---|
| Run it locally | {{The command, or what to open}} | {{01-01, or "exists"}} |
| Tests | {{The levels, and what each covers: unit for the rules, integration for the data, end to end for the journeys that cannot go wrong. The command. What each target and failure case is checked by is in the test plan}} | {{Task}} |
| Checked on every change | {{What runs on its own, and where: lint, types, tests, on each push}} | {{Task}} |
| Environments | {{Where it runs, one line each: local, test, production}} | {{Task}} |
| Configuration and secrets | {{Where each environment reads them from. Never a file committed to git}} | {{Task}} |
| Release | {{How a version reaches the people who use it, and how it is undone}} | {{Task}} |

## What changes

<!-- Only in a plan that changes a project that already exists: drop this
section in a new project. One block per change, the newest last. Each line
names what it touches: the requirement, or the file. -->

### {{Name of the change}}

- **Enters:** {{What will exist that does not exist today.}}
- **Changes:** {{What exists and will behave differently, and how.}}
- **Leaves:** {{What stops existing. "Nothing" when nothing does.}}

## Phases

| Phase | What it delivers | Done when |
|---|---|---|
| {{1 · Name}} | {{What exists at the end}} | {{What can be checked}} |

## Tasks

### {{Phase 1 · Name}}

1. {{Task name}}: {{what it does, in one line}}. Needs: {{01-01, or nothing}}. Spec: `specs/{{01-01-task-name}}.md`

## What depends on people

- {{What only the person can decide or do, and which task waits for it. "Nothing" when there is none.}}
