# Continuing a project

A project that went through Blueprint and stopped is continued from its files:
the state, the journal and the documents. The conversation that produced them is
gone, and it may have happened with another agent. Never act as if you remembered it.

## Read before you answer

1. `.blueprint/state.md`, whole.
2. The newest session record in `.blueprint/journal/sessions/`, when there is
   one: what was left open, and the next step it names.
3. The project check, with the `blueprint-status` skill. If it is not available,
   check at least that every document the state calls `ready` exists, and that
   each step's count agrees with its checklist.

All of this is inside the project folder. A document the state names and that
is not there is reported as missing. Do not go looking for it in the folders
around: ask the person whether it was moved.

## The first message

One message, in this order:

1. **Where the project is,** in the line that opens every message of the
   interview: the step and what comes now.
2. **What you found, in a few lines:** where it stopped, what is already
   decided, what is left.
3. **A problem the check found,** one line each, with how to fix it. Nothing
   when there is none.
4. **The next question,** from the state's `## Next question`, with the rest of
   its block if there is one. The person corrects the summary if they disagree;
   do not wait for a "yes".

If the person asked to continue and the state file is in this folder, do not
ask again whether they want to continue. The first message is this one.

## Going on

From there the interview follows the same rules as a new project
([conduct.md](conduct.md), [steps.md](steps.md), [documents.md](documents.md)):

- What is under `## Answers` is answered. Do not ask it again, even in other words.
- A step whose main questions are all answered and whose document is not
  written gets its document now.
- The questions under `## Refinement questions left for later` wait until you
  need them.

When the state's `starting_point` is `improve` or `refactor`, the steps ask
only about the change, and [change.md](change.md) says what each one asks and
writes. A step with `0 of 0` main questions is one the change does not touch:
it is not left to do.

When every step is closed, the interview is over. Say so, and that the next
thing is the first task of the plan that is not done.

## When the state is behind

The last session may have stopped without saving. Signs: a document exists
that the state calls `not-started`; a session record tells of an answer or a
decision the state does not have; the repository's history is newer than the
state's `updated`.

1. **Say what is missing,** plainly: the state stops at this point, and the
   files show more than that.
2. **Rebuild what the files allow,** from the documents, the session records,
   the repository's history and the code. Take only what is written there.
3. **Show it marked as rebuilt,** naming where each piece came from: "Rebuilt
   from `docs/system-description.md`: the first version leaves online payment out."
4. **Ask the person to confirm it.** Save the state, with the
   `blueprint-record` skill, only after they do. Until then, change nothing.

What the files do not tell is asked again, and you say why: it was not saved.

## When something changed outside

A document or the code changed after the state's `updated`, and it disagrees
with what the state says. Point at the difference, in one or two lines, and ask
which one holds. Do not choose in silence.

## When the state cannot be read

Say so, and say what you could still read of it. Rebuild as above, and propose
to write the state again once the person confirms.
