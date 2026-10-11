---
name: blueprint-survey
description: Reads an existing project before asking anything. Use when the user wants to improve, refactor or document a project that already has code or documents, or asks what a project has. Reports what the code and the documents already answer, classifies each document as matching the code, outdated or missing, and sizes a change as small or not.
---

# Blueprint: survey

A project that already exists answers most questions by itself. Read it before
asking, so the person is asked only what the files do not say.

This skill only reads. It changes nothing: what is written afterwards is
decided with the person, by whoever called you.

## How to talk

- Answer in the person's language, in plain words.
- Say what you read and what you did not read. Never let a part you skipped
  pass as read.
- The report is short. The detail stays in the files, and you say where.

## 1. What to read

In this order. Stop when you can write the report: this is not an audit.

1. **The shape of the folder.** The names at the top, and two levels down. Skip
   dependency, build and hidden folders such as `node_modules`, `dist`, `.venv`
   and `.git`.
2. **What says what the project is.** The README. The manifest:
   `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, a
   `.csproj`, `Gemfile`, `composer.json`. The file agents read first:
   `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`. What says where it runs and how it is checked:
   a `Dockerfile`, a hosting configuration, the pipeline files, the tests
   folder. What says what it stores: the schema or the migrations.
3. **The documents.** `docs/` or `doc/`, decision records, a plan or a task
   list, the sections of the README, and `.blueprint/` when there is one.
4. **The area the change touches,** when a change was named: the files that do
   that part today, their tests, and what calls them.
5. **The history,** when you can read it: the last commits, to see what moves
   and how many people write. If you cannot, say so and go on.

Limits:

- **Only read.** Do not run the project, its tests, its install or its build.
  Say which command runs each, from what the files show.
- **Do not open secrets.** A `.env`, a key file, a credentials file: note that
  it exists, and do not read it. Never copy a key into the report.
- **When the repository is too large to read whole,** read the area the change
  touches and what step 2 lists, and say what you left out.

## 2. What the project is

From what you read, and marked as read from the code, not as said by the person:

- what it does and who uses it, as far as the files show;
- what it is built with, where it runs, how it is started and how it is tested;
- the five facts of the kind of project: it has screens, it stores data, it
  holds personal data, it is used by command or by code, it calls a model. Give
  `yes`, `no` or `unknown` for each, and leave `unknown` what the files do not
  settle.

## 3. The documents, in three states

A project keeps its documents under its own names, in its own places. Match
each one to what it is for, whatever it is called: a README that explains what
the system is serves as its system description; a folder of decision records
serves as its decisions record.

Go through the documents a project can have: system description, requirements,
research, architecture, decisions record, plan, and the ones its kind brings
(use cases, data model, data classification, wireframes, design, interface
contract, AI features, test plan, playbooks). Put each in one state:

| State | When | What you say |
|---|---|---|
| **Matches the code** | The concrete things it states are true in the code, where you checked | Where it is, and which part you checked |
| **Outdated** | At least one concrete thing it states is not true in the code | Where it is, and each difference: what the document says, what the code shows, and in which file |
| **Missing** | Nothing in the project serves that purpose | Only its name |

What to check in a document is what can be checked: a command, a path, the
name of a part, a dependency, a field that is stored, the steps of a flow. Check
the parts that speak of the area the change touches, and a few others. A
document is classified by what you checked: say which part you did not check,
and do not call it matching.

Do not correct an outdated document. Report it.

## 4. The size of the change

When a change was named, say whether it is small.

A change is **small** when all of this holds:

- it touches one part of the code: a few files that work together;
- it brings no decision that is costly to undo: no new service, nothing that
  generates cost, no change to the stack, to how the code is divided into
  parts, to hosting or to how personal data is handled;
- it brings no new fact about the kind of project: not the first screen, the
  first stored data, the first personal data, the first command or the first
  call to a model;
- it fits in one task: one spec can say what it does, what it does not, and
  when it is done.

Otherwise it is **not small**. A costly decision or a new fact always makes it
not small. In any other doubt, take it as small and say so: the person corrects
it.

Say the size with its reason in one line, and name the files the change touches.

## What you give back

In this order, about fifteen lines:

1. **What the project is,** in two or three lines, from the code.
2. **The documents:** one line for each that exists, with its state and, when
   it is outdated, the difference that matters most; then one line naming the
   missing ones.
3. **The change:** its size and the reason, and the files it touches. Nothing
   when no change was named.
4. **What you did not read,** in one line. "Nothing" is a valid answer only
   when it is true.
5. **What the files do not answer:** the questions left for the person, three
   at most.

When the `blueprint` skill called you, it is the one that talks to the person:
give it this report, and it decides what to show and what to ask.

When the person asked for the whole picture of what exists, the report is the
same, with every part of the code read and every document checked whole. Say
how much that is before you start when the repository is large.

## Never

- Never create, change or delete a file.
- Never say you read what you did not read, and never call a document matching
  without having checked it against the code.
- Never rewrite or "fix" a document that is outdated: report the difference.
- Never open a file of secrets, and never repeat a key.
- Never run the project's code.
- Never ask the person something the files answer.
