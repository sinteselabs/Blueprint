---
name: blueprint-setup
description: Prepares a project for agentic development once its Blueprint documents are written. Use when the plan is closed and the repository has to be made ready, or when the user asks to prepare the environment, the agent entry file or the project journal. Writes the Blueprint block of the entry file, connects memory and observability through a tool or the project journal, writes a roadmap of the code so an agent reads only the part a task touches, adds a playbook per role when a team develops, runs the project check, and says what it could not connect.
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
5. **Read the plan's "How it is built and checked".** It says how the project
   is run, tested and released. If the plan has no such section, say so: the
   commands of the entry file will then come from the code alone, or be left
   out where there is no code.

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
6. **The commands.** Where the code exists, take how to run, test and build it
   from the project's own files: the scripts of `package.json`, a `Makefile`,
   `pyproject.toml`, the CI configuration. Where it does not, take them from the
   plan, each with the task that creates it. You read them and do not run them,
   so say so: an agent learns whether they work at its first task. A command
   neither the files nor the plan give is left out, not guessed.

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

## 4. The code roadmap

For every project, whether one person develops it or a team. An agent that opens
a session with no map reads the codebase to find where to work, and pays for
that reading in every session. The roadmap is the map: which folder holds
what, and which paths a task has to read. It is one file,
`code-roadmap.md` in the documents folder, from
[assets/code-roadmap.md](assets/code-roadmap.md). If the project already has one,
keep it and bring it up to date.

**Where the code exists,** read the folder tree, and open a file only when its
name and place do not say what it is. Write one row per area: its path, what
lives there, when a task has to read it, and which paths go with it (a schema, a
shared module, the tests). Entry points, code that many areas depend on, and
paths not worth opening (generated, vendored, bulky) get their own sections.
This is the one time the codebase is read whole, and it is read once so that no
later session has to.

**Where there is no code yet,** write it from the architecture's "How the code
is organised" and from the plan: each area the tasks will create goes between
the planned marks, with the task that creates it. A delivery moves its rows
out of the planned block into the tables, which is what the entry file's rule
asks for.

Keep it short enough to read at the start of every session: about 150 lines.
Past that, group small folders into one row. Every path goes in backticks and
is a path that exists, outside the planned block. Do not describe what a file
does line by line: that is what opening it is for.

Then check that each task spec in the plan has a "Where in the code" section
naming areas of the roadmap. A spec without it is not rewritten: say which ones
lack it, and the agent will add it when it starts that task.

## 5. A playbook per role

Only when the state's `developers` is more than 1. One file per role, in a
`playbooks/` folder inside the documents folder, from
[assets/playbook.md](assets/playbook.md). Each playbook sends its role to the
rows of the code roadmap that are its own.

The roles come from the plan: who does what. If the plan does not say, ask the
person, once, naming the roles you would create. With `developers` at 1, create
nothing: a single person has no handover.

## 6. When more than one agent works

When agents will work on the project at the same time, or without the person
watching, the entry file gets one more section, the last of the block: one
worktree and one branch per agent, the work declared before it starts, what a
worktree does not isolate, who integrates, the work mode, and the unattended
run. [references/parallel-work.md](references/parallel-work.md) says when to
write it, the one question to ask when the state does not settle it, and why
each rule is there. Ask the work mode there too, once, with the recommendation.

With one agent at a time and nobody running one unattended, leave the section
out and ask nothing.

## 7. Run the check

Go through the project check with the `blueprint-status` skill, and report what
it found. A problem is reported with how to fix it; fix only what belongs to
this skill: the block of the entry file, the journal, the code roadmap, a playbook.

## What you give back

In this order, about ten lines:

1. **What the project has now,** in one line: prepared, and where its rules are.
2. **What you created and what you changed,** one line each. For the code
   roadmap, how many areas it has and whether it describes code that exists or
   code that is planned. For the commands, which ones the entry file has and
   where each came from.
3. **Memory and observability:** one line each, saying what records what, or
   what is missing and what the person has to do once.
   When the entry file got the section for more than one agent, one line
   saying so, with the work mode.
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
- Never write a path in the code roadmap, outside the planned block, that you
  did not see in the folder.
- Never write the first task yourself. Preparing the repository ends where the
  development begins.
