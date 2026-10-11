---
name: blueprint-setup
description: Prepares a project for agentic development once its Blueprint documents are written. Use when the plan is closed and the repository has to be made ready, or when the user asks to prepare the environment, the agent entry file or the project journal. Writes the Blueprint block of the entry file, connects memory and observability through a tool or the project journal, adds a playbook per role when a team develops, runs the project check, and says what it could not connect.
---

# Blueprint: setup

The documents are written and the plan is closed. What is missing is the
repository itself: an agent that opens this project has to find the rules, the
plan and where to record, without anyone explaining it again.

This skill writes inside the project folder only, and it never installs a tool
on the person's machine.

## How to talk

- Answer in the person's language, in plain words.
- Say every file you created and every file you changed, one line each.
- What did not work is said, never hidden: a tool that does not answer, a file
  that could not be written.

## 1. Before you write

1. **Find the project.** `.blueprint/state.md`, in this folder or in the
   folders above. If there is none, say that you found no Blueprint project
   here and stop: there is nothing to prepare yet.
2. **Read the state whole.** From it: `documents_at`, `tasks_at`,
   `document_language`, `developers`, `memory`, `observability`, and the plan's
   situation.
3. **If the plan is not closed,** say so and what is missing. Preparing a
   project whose plan is not written leaves an entry file pointing at a plan
   that does not exist. Ask whether to go on all the same.
4. **Look at what the project already has:** `AGENTS.md`, `CLAUDE.md`, a
   journal folder, a playbooks folder. What exists is kept.

## 2. The entry file

`AGENTS.md` at the project root is the person's file. Blueprint keeps one block
in it, between two marks, and touches nothing else:

```
<!-- blueprint:start -->
...
<!-- blueprint:end -->
```

1. **If the block is there,** replace what is between the marks, and keep every
   line outside them exactly as it is.
2. **If the file exists without the block,** add the block at the end, after one
   empty line. Read the file first: when a rule of the person says the same
   thing as a line of the block, keep theirs and drop that line, and say which.
3. **If the file does not exist,** create it with the block alone.
4. **Write the block from [assets/agents-block.md](assets/agents-block.md),** in
   the project's document language, with the project's real paths, taken from
   the state. Replace every `{{placeholder}}` and leave no section that does not
   apply.
5. **`CLAUDE.md` and `GEMINI.md`:** some agents read a file of their own and
   never open `AGENTS.md`. Claude Code reads `CLAUDE.md` first, and the
   Antigravity CLI reads `GEMINI.md` and does not read `AGENTS.md` at all (read
   in its version 0.63.0, 11/10/2026). So both files get one line:
   `See @AGENTS.md for how to work on this project.`, in the document language.
   One that does not exist is created with that line alone; one that exists and
   does not name `AGENTS.md` gets the line at the end, and you say so. Never
   move the person's rules out of either.

The block is also what says that this project was prepared. Nothing in the
state file records it: the mark in the entry file is the fact.

## 3. Memory and observability

The state's `memory` and `observability` say `journal` or name a tool.

**With the journal,** which is the way that needs nothing installed: make sure
`.blueprint/journal/` exists, with `milestones.md` and the session records.
Create what is missing through the `blueprint-record` skill. Say in one line
that the project records itself in files, and that there is no automatic
measure of cost this way.

**With a tool named,** check that it answers before you say it is connected:
read something from it, or write a test line and read it back. Then:

- it answers: say so, and what it records;
- it does not answer, or you have no way to reach it: say that, say what the
  person has to do once (install it, put a key where that tool reads it), and
  write to the journal until it is back. Never report a tool as connected
  because the state names it.
- a file the tool needs inside the project: write it from the examples in
  [assets/project-files/](assets/project-files/), with the values the person
  gave. A key, a token or a password is never written in a file of the project.

If the person says they want a tool that the state does not name, say what it
takes, and change the state only through the `blueprint-record` skill.

**When the state says `journal` and a tool would be worth it,** offer it once,
in one line, with the reason it fits this project, and go on either way. Most
people have never heard of the tools in this field and cannot answer a bare
"do you want observability?": the offer carries the reason or it is noise.
[references/observability.md](references/observability.md) has when it is worth
it, when it is not, what to ask first, and what the person does to wire it.
Blueprint ships no script for this and installs nothing: a no, or no answer, is
a closed subject, and the journal keeps recording.

## 4. A playbook per role

Only when the state's `developers` is more than 1. One file per role, in a
`playbooks/` folder inside the documents folder, from
[assets/playbook.md](assets/playbook.md).

The roles come from the plan: who does what. If the plan does not say, ask the
person, once, naming the roles you would create. With `developers` at 1, create
nothing: a single person has no handover.

## 5. Run the check

Go through the project check with the `blueprint-status` skill, and report what
it found. A problem is reported with how to fix it; fix only what belongs to
this skill: the block of the entry file, the journal, a playbook.

## What you give back

In this order, about ten lines:

1. **What the project has now,** in one line: prepared, and where its rules are.
2. **What you created and what you changed,** one line each.
3. **Memory and observability:** one line each, saying what records what, or
   what is missing and what the person has to do once.
4. **What the check found,** one line, or that it found nothing.
5. **The next thing:** the first task of the plan that is not done, by its
   number and its spec file, and that the person can say to start it.

## Never

- Never touch anything outside the marks of the entry file.
- Never delete or rewrite a rule the person wrote.
- Never say that a tool is connected without having read or written something
  through it.
- Never write a key, a token or a password in a file of the project.
- Never install anything on the person's machine, and never run the project's
  code.
- Never write the first task yourself. Preparing the repository ends where the
  development begins.
