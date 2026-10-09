---
name: blueprint-status
description: Answers "where are we?" for a Blueprint project from its saved state. Use when the user asks where the project stands, what is decided, what is open or what is left, or when a project is resumed. Reports the current step, the decisions, the open points and what remains, and runs the project check.
---

# Blueprint: status

The person can ask where things are at any moment, in any session, with any
agent, and get the same answer. So the answer comes from the project's files,
never from what you remember of the conversation.

This skill only reads. It changes nothing.

## 1. Find the project

A Blueprint project is marked by the file `.blueprint/state.md`. Look for it in
the folder you are in, then in the folders above, up to the root of the
repository.

If there is none, say that you found no Blueprint project here, and stop. Do
not create one.

## 2. Read the state

Read `.blueprint/state.md` whole. What it says is the answer.

If you know something from this conversation that the file does not have yet,
an answer the person just gave or a decision just taken, the file is behind.
Say so in one line, and say that it must be saved. Do not report it as if it
were saved.

## 3. Go through the project check

Go through the list in [references/check-list.md](references/check-list.md).
You do it by reading: the script that will do this is not part of this version
of Blueprint. Fix nothing. A problem is reported with how to fix it.

## 4. Answer

In the person's language, in this order, and short: about ten lines when
everything is fine.

1. **Where the project is,** in one line: the step under way, and how far it
   is. For example, in Portuguese: "Etapa 2 de 5 · Requisitos, com duas das três
   perguntas principais respondidas."
2. **The steps,** one line: which are closed, which are advanced, which are
   open, which have not started.
3. **What is decided:** the decisions in the state, by number and title, in one
   or two lines. When there are many, the last three and how many there are.
4. **What is open:** the open points, the decisions left open, and the
   questions left for later.
5. **What is left:** the main questions still unanswered, the documents that
   are not ready, and the next question, in the words the state has.
6. **The check:** one line when nothing is wrong, saying that you went through
   it by reading. When something is wrong, one line per problem, with how to fix it.
7. **When it was saved,** and by which agent: the state's `updated` and
   `updated_by`.

Do not paste a document or the state file into the conversation. Say where
they are.

## Never

- Never answer from memory when the state file says something else. The file wins.
- Never create, change or delete a file. To save something, the
  `blueprint-record` skill is the one that writes.
- Never hide a problem the check found to keep the answer short.
