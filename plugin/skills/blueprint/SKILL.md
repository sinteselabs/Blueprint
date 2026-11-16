---
name: blueprint
description: Guided path from an idea to a repository ready for agentic development. Use when the user wants to start a new software project, continue a project that went through Blueprint, improve or refactor an existing project, or asks to plan, specify or document a project or a change to one. Finds the starting point from the state of the folder, then interviews one block of questions at a time and writes the project documents.
---

# Blueprint

Blueprint takes a software project from an idea in plain language to
requirements and a repository ready for agentic development. This skill is the
way in. There is only one, whatever the person wants to do.

## How to talk

These hold from the first message to the last.

- **Open every message of the interview with where the conversation is,** in
  one line: the step, what was just settled, what comes now. For example, in
  Portuguese: "Etapa 2 de 5 · Requisitos. Ficou decidido quem usa o sistema.
  Agora: o que cada um precisa conseguir fazer."
- Answer in the person's language, in plain words.
- Say what you looked at, what you decided and what you saved. Nothing happens
  in silence.
- Ask at most three questions at a time, on one subject.
- The person never has to read a document or approve a step for the work to go on.

## 1. Find the starting point

The person does not have to say whether they are starting, continuing, improving
or refactoring. Work it out from the folder, and tell them what you concluded.

A Blueprint project is marked by the file `.blueprint/state.md`.

### First, say what you are going to do

Before you use any tool, write one line to the person: what you are going to
look at, and why. For example: "First I will look at this folder and, if I need
to, at the folders above and beside it, only their names and whether they hold a
Blueprint project, so I do not create again something that already exists."

This line comes before everything else because looking above and beside leaves
the project folder, and the coding agent may stop to ask the person for
permission. They must already know why.

### Where to look, in this order

1. **The folder you are in.** Does it have `.blueprint/state.md`? Does it have
   code or documents? Or is it empty? A folder is empty when it has nothing but
   version control, agent configuration, a license or a README with no content.
   If the state file is here, stop looking: go to "What to conclude".
2. **The folders inside it,** two levels down, for `.blueprint/state.md`. Skip
   dependency, build and hidden folders such as `node_modules`, `dist` and `.git`.
3. **The folders above it,** for `.blueprint/state.md`: up to the root of the
   repository, or, where there is no repository, the parent and the grandparent.
   This step and the next leave the project folder. If you have not yet told
   the person that you are going to look there, and why, tell them now, before
   you look.
4. **The folders beside it,** the ones with the same parent: their names, and
   whether each has `.blueprint/state.md`.
5. **The person's project list,** `~/.blueprint/projects.md`, only when it is
   there: it names every project that went through Blueprint, with its path.
   It is what finds a project that lives in another corner of the machine. If
   it is not there, or you cannot read it, go on without it and say nothing
   about it.

Outside the project folder, read folder names, Blueprint state files and that
list only. Open nothing else.

If the folder you are in is a home folder or the root of a drive, do not look
around and do not start a project there. Ask where the project should live.

### If you cannot look outside the folder

The coding agent may ask the person for permission, or refuse. When looking
outside is refused or blocked, say that you could not look, and ask the person
whether this project already exists somewhere else. Never conclude in silence
that it is new.

### What to conclude

| What you found | Starting point | What you do |
|---|---|---|
| `.blueprint/state.md` in this folder | continue | Say where the project stopped, from the state file. If the person asked to continue, go on without asking again. If they asked to change, add or reorganise something, it is a change to this project: section 4. Otherwise ask to confirm |
| `.blueprint/state.md` in a folder above | continue | The project is that one, and this folder is part of it. Use that state. Never create another |
| `.blueprint/state.md` in one or more folders inside | to be asked | List the projects found, with their paths, and ask which one, or whether this is a new project |
| An empty folder, and nothing like the project nearby | start | Say so. If the person asked to start a new project, go on to the first block of questions in the same message, without asking again; otherwise ask to confirm |
| An empty folder, and a project like the one described in a folder beside | to be asked | Name that folder and ask whether it is that project or a new one |
| Code or documents, and no state file anywhere | improve or refactor | If the request says which, take it, say what you took and go on to read the project. Otherwise ask which: to change or add something, or to reorganise it inside, which includes documenting what exists |

When what the person asked for does not match what you found, say both and ask:

- They ask to continue and there is no state file here or nearby: say that you
  found no Blueprint project, and ask where it is. Do not start a new one.
- They ask to start and this folder already holds a Blueprint project: say that
  there is a project here and where it stopped, and ask whether they mean to
  continue it or whether the new project should live in another folder.

### Say it, and ask only when there is something to choose

In one or two lines: what you looked at, what you found and what you conclude.

**When what the person asked for is what you found,** do not hold the
conversation for a "yes". They asked to start and the folder is empty with
nothing like the project around it, or they asked to continue and the state file
is here: say what you found, and go on in the same message. For example: "This
folder is empty and I found no project like it in the folders around, so we
start a new project here. Tell me if that is not it." The person corrects you
if it is wrong.

**When there is something to choose, ask, and wait for the answer.** For example:

- "There is a Blueprint project here, stopped at the requirements. Shall we
  continue from there?" (they did not say what they wanted)
- "This folder is empty, but there is a project like this one in
  `../bakery-orders`. Is it that one, or a new project?"
- "This folder has code and has not been through Blueprint yet. Do you want to
  change or add something, or to reorganise it inside?"

**Create nothing before the person answers that first message:** no folder, no
file. Their answer is the confirmation. Until then you have only read.

## 2. Starting a new project

When the starting point is a new project, conduct the interview. Read these
three references before the first question, and follow them:

- [references/steps.md](references/steps.md): the five steps, the main
  questions of each, and when a step moves on;
- [references/conduct.md](references/conduct.md): the shape of every message,
  what to do after each answer, decisions, research;
- [references/documents.md](references/documents.md): which documents the
  project has, where they go and how to write them.

The interview in short:

1. **The first message** asks the language of the documents, whether more than
   one person will develop, and the first block of the system description. Ask
   only what the person's first sentence did not already answer. If the person's
   folder `~/.blueprint/` is there, what it says about them is used from here on,
   and the message says in one line what you are using from it. When the
   person asked to start, this is the same message that says what you found in
   the folder, and nothing is created yet: the state file is written with
   their first answer.
2. **After each answer:** save the state with the `blueprint-record` skill,
   write the document of any step whose last main question was answered, and
   send the next message. That message opens with where the conversation is,
   says in a few lines what you understood, and asks the next block.
3. **A step moves on when its main questions are answered.** Do not wait for
   approval. The step's document is written at that moment, and you tell the
   person in one line where it is.
4. **A decision that is costly to undo** (the stack, hosting, the handling of
   personal data, anything that generates cost) is the one place where you wait:
   show the options, recommend one by the criteria the person declared, and let
   them choose.
5. **After the plan,** prepare the repository with the `blueprint-setup` skill,
   then say what the person has and which task is first.

The state file and the journal are kept by the `blueprint-record` skill. If it
is not available, tell the person, and keep the same information in
`.blueprint/state.md` yourself.

## 3. Continuing a project

When the starting point is to continue, read
[references/continue.md](references/continue.md) and follow it. In short:

1. **Read the state file whole,** and the newest session record. Never act as
   if you remembered the conversation that produced them.
2. **Open with one message:** where the project is, what you found in a few
   lines, any problem the project check found, and the next question, taken
   from the state. Do not wait for a "yes".
3. **Go on by the same rules as a new project.** What the state has as answered
   is not asked again.
4. **When the state is behind** what the documents, the session records or the
   repository show, say what is missing, rebuild it marked as rebuilt, and save
   only after the person confirms.

## 4. Improving or refactoring a project

When the project already exists and the person wants to change it, read
[references/change.md](references/change.md) and follow it. In short:

1. **Read before you ask,** with the `blueprint-survey` skill: what the project
   is, each document as matching the code, outdated or missing, and the size of
   the change.
2. **One first message:** what you read, what you concluded and what you
   propose to write. Nothing is written before the person answers it.
3. **A small change** becomes one task with its spec, and nothing else.
4. **Improving** writes the change as a difference: what enters, what changes
   and what leaves. **Refactoring** leaves the requirements as they are, and
   writes the affected part as it is and as it will be, the decision, and how
   to check that nothing broke.
5. **Nothing is rewritten in silence.** A document that matches the code is
   left alone; an outdated one is corrected only where the change touches it,
   and the rest is reported.

The same path serves a project that went through Blueprint and now gets a
change: its state is kept, and the steps the change touches open again.
