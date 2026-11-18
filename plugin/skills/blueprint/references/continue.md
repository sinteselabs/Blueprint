# Continuing a project

A project that went through Blueprint and stopped is continued from its files:
the state, the journal and the documents. The conversation that produced them is
gone, and it may have happened with another agent. Never act as if you remembered it.

## Read before you answer

1. `.blueprint/state.md`, whole.
2. The newest session record in `.blueprint/journal/sessions/`, when there is
   one: what was left open, and the next step it names. When other agents work
   on the project, also every record whose status is `in-progress`, `paused` or
   `waiting`: what they take is not yours to start.
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

When every step is closed, the interview is over. What comes next depends on
one thing: whether the repository was prepared, which is told by the block
between `<!-- blueprint:start -->` and `<!-- blueprint:end -->` in the entry
file, `AGENTS.md` at the project root.

- **The block is not there:** preparing the repository is what comes first, with
  the `blueprint-setup` skill, even when the person asked to go on with the
  work. Say why in one line: without it, an agent that opens this project does
  not know its rules, its plan or where to record. Then prepare it, and say
  which task is first.
- **The block is there:** the next thing is the first task of the plan that is
  not done. Name it, with its spec. When every task is done, say so, and that
  what comes next is a change: [change.md](change.md).

## An unattended run

When the person asks for work to go on without them, such as overnight, read
[unattended-run.md](unattended-run.md) and follow it. In short: three questions
before it starts (may it merge and deploy, which tasks, when it stops); during
it, a costly decision is taken with the recommended option and recorded as
`provisional`; at the end, a summary of what was done, what is provisional and
what waits for the person.

When the state has `provisional` decisions from an earlier run, say so in the
first message, one line each, and ask the person to confirm or reverse them.

## Keeping the documents true

Once the repository is prepared, the work is tasks, and every delivered task
can leave a document saying something the code no longer does. The project
check does not see that: it follows paths and ids, not what a document says.

- **When a task is delivered,** its spec gets its result and how to test it,
  and its situation becomes `done`. If the task changed something a document
  states, such as a command, a field, a flow or a path, correct that part of
  that document in the same delivery, and say which. If the change was
  meant to change what the system does, it was not a task of the plan: it is a
  change, and [change.md](change.md) says how it goes.
- **When a phase is delivered,** before recording the milestone, compare the
  documents the phase touched with the code, with the `blueprint-survey`
  skill. Report each difference, one line each, and correct only with the
  person's go-ahead.
- **When the history has commits that no task explains,** newer than the state's
  `updated`, read what they touched the same way, and say what they changed
  before naming the next task.

## Someone new on the project

A person or an agent who joins mid-project starts from the files, as any
session does: where the project is, with the `blueprint-status` skill, and a
walk through the code, with the `blueprint-explain` skill's tour. Do not hand
them the documents to read first.

When the newcomer develops too and the state's `developers` was `1`, that
changes the project's kind: update it with the `blueprint-record` skill,
add the `playbooks` document to the state as `not-started`, and say that the
`blueprint-setup` skill writes the playbooks and the role each person takes.

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
