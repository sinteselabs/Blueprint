# The personal memory

What Blueprint learns about the person follows them from one project to the
next: how they like to work, what they already use, and what went wrong before.
What it learns about a project stays in that project.

This is the only thing Blueprint writes outside the project folder, and only
with the person's permission.

## Where it lives

`~/.blueprint/`, in the person's home folder, with two files:

| File | What it holds | Template |
|---|---|---|
| `preferences.md` | How the person likes to work, what they already use, and the lessons: what went wrong and why | [personal-preferences.md](../assets/personal-preferences.md) |
| `projects.md` | One line per project that went through Blueprint: the name, the path, the date and one line about it | [personal-projects.md](../assets/personal-projects.md) |

If the person names another place, use it for this session and tell them, in one
line, that the next session will look in `~/.blueprint/` again unless they say
it. Never guess another place on your own.

**Never write in the coding agent's own memory,** such as `~/.claude/CLAUDE.md`,
a file in `~/.codex/` or an `AGENTS.md` in the home folder. Those belong to the
agent and to the person, they are read in every project they open, and Blueprint
does not touch them. When the agent you are running in has a memory of its own,
you may offer the person the text to paste there, in a block they can copy, and
say that it is theirs to do. What Blueprint records goes to `~/.blueprint/`.

When the state's `memory` names a tool, the same records go to that tool's
personal space, following its own instructions, and the folder is not needed.
If the tool does not answer, say so in one line and keep the learning in the
project journal until it is back.

## Asking, once

Ask the first time there is something worth saving, never at the start of a
conversation. In two lines: what you learned, and that it would go to a folder
of theirs outside the project, which is theirs to read, correct or delete.

- **They say yes:** create the folder and the file, write it, and say in one
  line what you saved and where.
- **They say no:** write nothing outside the project. Keep the learning in the
  project (the next rule says where) and go on. Everything works, it only does
  not carry over. Do not ask again in this project.
- **They do not answer:** treat it as no.

**Whatever happens to the folder, the learning is saved in this project.** A
preference that will guide choices here is a criterion: it goes under
`## Criteria the person declared` in the state file, in the person's own words.
A lesson goes in the session record. So a refused permission, or a write that
was blocked, never costs what the person said. When the write was blocked, say
so and say where you kept it.

A refusal cannot be remembered, because remembering it would need the folder.
In another project, ask once again, and say that you are asking because there is
nothing saved on their side.

## What goes up, and what never does

**Up:** what is true of the person in any project.

- How they like to work: the size of a block of questions, how much detail they
  want, that they take recommendations.
- What they already use: a stack, a hosting service, tools.
- A lesson: something that went wrong, and why.
- The project line: the name, the path, the date, and one line about it.

**Never:** anything that belongs to one project.

- What the system does, its requirements, its decisions, its data.
- A name, an address, a telephone or anything else about the people it serves.
- A key, a token or a password, in any form.
- A path inside a project, beyond the project's own folder.

When in doubt, it does not go up. The project journal already keeps it.

## Writing it

1. **Say it in one line, as you save it:** "I saved in your folder that you take
   the recommendations on architecture." The person corrects it if it is wrong.
2. **One entry per thing,** short, written as a fact about the person.
3. **Never rewrite what is there** because of one project. Add a line, or
   correct the one that is now wrong and say which.
4. **The project line is written once:** when the project's state file is first
   created, or, in a project that already had one, the first time you read the
   list and this project is not in it. It is corrected only if the project
   moves.

## Reading it

At the start of a project, when the folder exists: read both files, use what is
there, and say in one line what you are using. For example: "I am using what is
in your folder: you take the recommendations on architecture, and you use
Cloudflare."

The project list is what lets the entry find a project that lives somewhere
else on the machine. Searching it is part of finding the starting point, in the
`blueprint` skill.

Never let what is in the folder override what the person says now. What they say
in this conversation wins, and then you correct the folder.
