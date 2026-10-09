---
name: blueprint
description: Guided path from an idea to a repository ready for agentic development. Use when the user wants to start a new software project, continue a project that went through Blueprint, improve or refactor an existing project, or asks to plan, specify or document a project. Finds the starting point from the state of the folder, then interviews one block of questions at a time and writes the project documents.
---

# Blueprint

Blueprint takes a software project from an idea in plain language to
requirements and a repository ready for agentic development. This skill is the
way in. There is only one, whatever the person wants to do.

> **Under construction.** This skill finds the starting point and conducts the
> interview of a new project, up to the plan. Continuing, improving and
> refactoring are not built yet: see [The other starting points](#3-the-other-starting-points).

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
or refactoring. Work it out from the folder, then confirm it with them.

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
4. **The folders beside it,** the ones with the same parent: their names, and
   whether each has `.blueprint/state.md`.

Outside the project folder, read folder names and Blueprint state files only.
Open nothing else.

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
| `.blueprint/state.md` in this folder | continue | Say where the project stopped, from the state file, and ask to confirm |
| `.blueprint/state.md` in a folder above | continue | The project is that one, and this folder is part of it. Use that state. Never create another |
| `.blueprint/state.md` in one or more folders inside | to be asked | List the projects found, with their paths, and ask which one, or whether this is a new project |
| An empty folder, and nothing like the project nearby | start | Say so and ask to confirm |
| An empty folder, and a project like the one described in a folder beside | to be asked | Name that folder and ask whether it is that project or a new one |
| Code or documents, and no state file anywhere | improve or refactor | Ask which: to change or add something, or to reorganise it inside, which includes documenting what exists |

When what the person asked for does not match what you found, say both and ask:

- They ask to continue and there is no state file here or nearby: say that you
  found no Blueprint project, and ask where it is. Do not start a new one.
- They ask to start and this folder already holds a Blueprint project: say that
  there is a project here and where it stopped, and ask whether they mean to
  continue it or whether the new project should live in another folder.

### Say it and confirm

In one or two lines: what you found, what you conclude, and a question. For example:

- "This folder is empty and I found no project like it in the folders around.
  We start a new project here. Is that right?"
- "There is a Blueprint project here, stopped at the requirements. Shall we
  continue from there?"
- "This folder is empty, but there is a project like this one in
  `../bakery-orders`. Is it that one, or a new project?"
- "This folder has code and has not been through Blueprint yet. Do you want to
  change or add something, or to reorganise it inside?"

**Create nothing before the person confirms:** no folder, no file. Until then
you have only read.

## 2. Starting a new project

Once the person confirms that this is a new project, conduct the interview.
Read these three references before the first question, and follow them:

- [references/steps.md](references/steps.md): the five steps, the main
  questions of each, and when a step moves on;
- [references/conduct.md](references/conduct.md): the shape of every message,
  what to do after each answer, decisions, research;
- [references/documents.md](references/documents.md): which documents the
  project has, where they go and how to write them.

The interview in short:

1. **The first message** asks the language of the documents, whether more than
   one person will develop, and the first block of the system description. Ask
   only what the person's first sentence did not already answer.
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
5. **After the plan,** say what the person has, and that preparing the
   repository for development is not built yet in this version of Blueprint.

The state file and the journal are kept by the `blueprint-record` skill. If it
is not available, tell the person, and keep the same information in
`.blueprint/state.md` yourself.

## 3. The other starting points

Continuing a project, improving one and refactoring one are not built yet.
When the confirmed starting point is one of them, tell the person plainly that
Blueprint is still being built and does not conduct that path yet. Do not
improvise it.

When the starting point is to continue, you may read out the state file's
`## Next question`, so the person sees where the project stands.
