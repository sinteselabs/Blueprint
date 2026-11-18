---
name: blueprint-record
description: Keeps a Blueprint project's state and journal in files, and the personal memory that follows the user from one project to the next. Use at the end of a block of questions, when a decision is taken or left open, when a step closes or a document becomes ready, when a session is ending, when the user asks to save where the project is, and whenever they say something about themselves that holds in any project, such as a tool they always use, how they like to work, or a lesson, including when they ask for it to be remembered for next time. Saves the state, the journal and, with the user's permission, their own folder outside the project, and says in one line what it saved.
---

# Blueprint: record

A project's memory lives in files, not in the conversation. A conversation has a
limit and ends. What is written here is what the next session, another agent or
another person resumes from.

This skill writes inside the project folder. The one exception is the person's
own folder, outside every project, and only with their permission: see
[The personal memory](#the-personal-memory).

## When to record

| What just happened | What to write |
|---|---|
| The person answered a block of questions | The state file |
| A decision was taken, or left open | The decisions record, then the state file |
| A step closed, a document became ready, a phase of the plan was delivered, or a version was released | The milestones file, then the state file |
| The session is ending, or the person says they are stopping | The session record, then the state file |
| You are about to start a task while other agents work on the project | The session record, opened with what you take: [Declaring the work](#declaring-the-work) |
| The conversation is getting long | The state file, before anything is lost |
| You learned something about the person that is true in any project | The personal memory, with their permission |

Do not wait for the end of the session to save the state. Save at the end of
every block.

## Where things are

| What | Where in the project | Format |
|---|---|---|
| State file | `.blueprint/state.md` | [references/state-format.md](references/state-format.md) |
| Session records | `.blueprint/journal/sessions/`, one file per session | [references/journal.md](references/journal.md) |
| Claims, when agents run on more than one machine | `.blueprint/work/` on the branch `blueprint-work`, one file per session | [references/claims.md](references/claims.md) |
| Milestones | `.blueprint/journal/milestones.md` | [references/journal.md](references/journal.md) |
| Decisions record | `decisions.md` in the documents folder (the state's `documents_at`) | [references/journal.md](references/journal.md) |
| Test plan | `test-plan.md` in the documents folder | The template, [assets/test-plan.md](assets/test-plan.md) |
| The personal memory | `~/.blueprint/`, outside every project | [references/personal-memory.md](references/personal-memory.md) |

Templates are in `assets/`: `state.md`, `session.md`, `milestones.md`,
`decisions.md`, `test-plan.md` and `claim.md`. `assets/state.example.md` is a filled state
to compare against.

Read the format reference before writing a file for the first time in a session.

## Saving the state

1. **Find the file.** Look for `.blueprint/state.md` in the project root. If you
   are in a subfolder, look in the folders above before concluding there is none.
   Never create a second state file inside a project that already has one.
2. **If there is none,** create `.blueprint/state.md` from `assets/state.md`.
   Leave no `{{placeholder}}`: where something is not known yet, write `unknown`
   and `-` in the facts table, and in an empty section one line saying there is
   nothing yet, in the document language. The main
   questions of each step come from whoever is conducting the interview; if you
   were not given them, ask, do not invent them.
3. **If there is one, read it first.** Start from what the file says, not from
   what you remember of the conversation. Change only what changed.
4. **Update what the block brought:**
   - under `## Answers`, what the person answered, in a few lines, under a
     heading `### <step> · <block title>`;
   - under `## Main questions`, tick the questions that are now answered;
   - in `## Steps`, the count (`2 of 4`) and the situation of each step;
   - in `## Documents`, the situation and the place of each document, and a
     new row when a fact of the project kind brings a document (the table in the
     format reference says which);
   - `## Criteria the person declared`, whenever they state a limit or a
     preference that will guide choices: budget, deadline, what they already use;
   - `## Decisions`, `## Open points` and `## Refinement questions left for later`;
   - `## Next question`, in the words it will be asked.
5. **Set `updated` and `updated_by`.** Take the time from the system, in UTC, for
   example with `date -u +%Y-%m-%dT%H:%M:%SZ`, or in PowerShell with
   `(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")`. Do not guess
   the time. If you cannot get it, ask the person.
6. **Check your own work** before saying it is saved:
   - for each step, the count in `## Steps` equals the ticked and total
     questions under `## Main questions`;
   - `not-started` has no question answered; `open` has at least one unanswered;
     `advanced` and `closed` have all of them answered;
   - a step becomes `advanced` when its last main question is answered, and
     `closed` only when its document is ready;
   - no `{{placeholder}}` is left.
7. **Say what you saved, in one line,** in the person's language. For example:
   "Saved the state: requirements, two of three main questions answered."

In the state file, keys, headings and the values listed in the format stay in
English, exactly as written there. What the person said and what you write
about it are in the project's document language.

The decisions record, the milestones and the session records are for people to
read: write them in the document language, headings and labels included. Their
templates are in English; translate them. Keep the shape that others rely on:
a decision's heading is `## D-001 · Title`, and file names do not change.

## Recording a decision

1. Open `decisions.md` in the documents folder. If it does not exist, create it
   from `assets/decisions.md`.
2. Add an entry at the end, numbered after the last one: `D-001`, `D-002`.
   Fill every line of the entry. `Reason` names the criterion that decided it.
3. A decision that is left for later is recorded too, with the situation `open`
   and what depends on it.
4. A decision an agent took during an unattended run, in the person's absence,
   is recorded with the situation `provisional`, `Decided by` naming the agent
   and the run, and `Alternatives` saying what reversing it would take. When the person confirms it, its
   situation becomes `decided`, in the record and in the state. When they
   reverse it, it is replaced, as the next section says.
5. Never rewrite an entry, except its situation. When a decision changes, add
   a new entry and set the old one's situation to `replaced by D-NNN`. See
   [Replacing a decision](#replacing-a-decision) for what else changes.
6. If the decision left something to verify, write it in `To test`. It is not
   tested before deciding: it goes into the test plan, as the next section says.
7. Add the decision to `## Decisions` in the state file, set the document
   `decisions` to `ready` with its place, and save the state. The record is
   `ready` whenever every decision so far is in it, the open ones included.

## Replacing a decision

A decision that no longer holds leaves behind what was built on it: specs that
come from it, code that carries its id, rows of the test plan, parts of the
architecture. Replacing it in the record is not enough.

1. **Find what depends on it** before you record the new one:
   `blueprint trace D-NNN` lists the documents, the specs and the code that
   name it. Without the command, search the documents and the code for the id,
   and say that you searched by hand.
2. **Record the new entry.** Its `Alternatives` names the old decision and why
   it no longer holds.
3. **In the state,** the old decision's line ends with `replaced`, and the new
   one is added after it. The record says by which decision; the state does not.
4. **Tell the person what depends on the old one,** one line each. Changing it
   is a change to the project, made by the `blueprint` skill: the specs and the
   code are not rewritten as part of recording.
5. **Rows of the test plan that came from the old decision** stay, with a
   result that says the decision was replaced. What the new one leaves to
   verify gets rows of its own.

Until that change is delivered, the project check reports the code and the open
specs that still name the replaced decision.

## Recording what is left to test

What a decision left to verify becomes an item of the project's test plan, so
it is not lost and nobody has to test it before deciding.

1. Open `test-plan.md` in the documents folder. If it does not exist, create it
   from `assets/test-plan.md`, in the document language.
2. Add one row per thing to verify, numbered after the last one: `T-001`,
   `T-002`. `Comes from` names the decision, such as `D-001`.
3. In the state file, set the document `test-plan` to `ready`, with its place.
   It is `ready` whenever every item so far is in it: the row says whether the
   item was verified.
4. When an item is verified, write the result in its row. If the result shows
   that a decision does not hold, say so to the person: it comes back to them
   as a new decision.

## Recording a milestone

Add one line at the end of the table in `.blueprint/journal/milestones.md`
(create the file from `assets/milestones.md` if it does not exist): the date,
what was reached, and what is possible now that was not before.

A version of the project released to the people who use it is a milestone too.
Its line names the version, the tag or commit it was released from, and the
phases or changes it carries, so anyone can tell which requirements were in
the hands of users from which day. How the project numbers its versions is the
project's: when it has no rule yet, ask, and save the answer as a criterion.

## Recording the session

When the session is ending:

1. Create `.blueprint/journal/sessions/YYYY-MM-DD-HHMM-agent.md` from
   `assets/session.md`, with the time the session started, in UTC, and your name
   in lowercase with hyphens: `claude-code`, `codex`, `antigravity-cli`. If you
   did not note when the session started, use the earliest time you read from
   the system and say so.
2. Fill the four parts: what was asked, what was done, what was decided, and
   what was left open with the next step.
3. Save the state file last, so `## Next question` says where the next session
   starts.

When other agents work on the project, the record was opened when the session
started, as the next section says: fill it, and close it.

## Declaring the work

When more than one agent works on the project at the same time, each one says
what it is taking before it starts, where the others look. That is its claim.
One agent working alone skips this. Read
[references/claims.md](references/claims.md) before you claim for the first
time in a session: it has the commands and the format.

**Where the claim goes:**

- **Agents on one machine:** your session record, opened at the start instead
  of the end, in the main checkout's `.blueprint/journal/sessions/`. The main
  checkout is the first folder `git worktree list` prints: a worktree has its
  own copy of the journal, and the others do not see it.
- **Agents on more than one machine:** a file of your own in `.blueprint/work/`,
  on the branch `blueprint-work` of the shared remote, never on the main branch
  or a task's branch. It needs only git. Without a shared remote, say that agents
  on other machines cannot see each other's work.

Say which of the two you use. A memory tool the state names may carry the claim
too; it is never what the others rely on.

1. **Look first.** Read the open claims: `in-progress`, `paused` or `waiting`.
2. **Claim:** the task, the files or areas it touches, the numbers you reserve
   (a migration number, a `D-` or `T-` number), and your branch. A number
   another open claim reserves is not yours: take the next one. On the branch, a
   rejected push means someone claimed first: fetch, read again, decide again.
   Never force-push it.
3. **On an overlap, do not start.** A claim overlaps yours when it takes the
   same task, the same files, the same number or the deploy. Take another task
   whose files are free, or claim as `waiting`, naming the claim you wait on,
   and read again every few minutes. A `paused` claim still holds what it takes.
4. **While you work,** update your own claim when what you take changes. Never
   write in another agent's claim.
5. **When you stop, every time,** release it: finished or dropped, with the
   commit or the reason; `paused`; or `waiting`, with on whom and for what. A
   claim left `in-progress` by a session that ended blocks the others.
6. **A claim nobody updated for two hours may be stale.** Report it to the
   person or the coordinator, and keep waiting. Never take it over: only the
   person closes another agent's claim.

The session record is the history of the session; on the branch, the work file
is only the live claim, and the session record's `Taking` line keeps what was
taken.

A worker in a worktree does not write the state, the decisions record or the
test plan: two copies of them diverge, and two agents take the same `D-` or
`T-` number. It writes in its session record what it decided, what it left
open and what is left to verify, and whoever integrates its branch records
them. On one machine, the session records are written in the main checkout and
not committed on the worker's branch: the one who integrates commits them.

## The personal memory

What is true of the person in any project goes to a folder of theirs, outside
every project, so a new project does not start from zero. What is true of one
project never leaves that project.

Read [references/personal-memory.md](references/personal-memory.md) before you
write there for the first time. In short:

1. **Ask once,** the first time there is something worth saving, saying what you
   learned and where it would go. No answer means no.
2. **Without permission, write nothing outside the project,** and never in the
   coding agent's own memory, such as `~/.claude/CLAUDE.md`. A preference that
   guides choices here is saved as a criterion in the state file either way, so
   nothing the person said is lost.
3. **Only what is true of the person:** how they like to work, what they
   already use, a lesson. Never a project's content, never a person's data,
   never a key.
4. **Say in one line what you saved and where,** as you save it.
5. **At the start of a project,** when the folder is there, read it and say in
   one line what you are using from it.

## When a tool keeps the memory

The state's `memory` and `observability` fields say `journal` or name a tool.
When they name a tool, write the session and the decisions there, following
that tool's own instructions, and keep the state file in the project either way.
If the tool does not answer, say so in one line and write to the journal until
it is back.

## Never

- Never write a key, a token or a password in any of these files.
- Never write outside the project folder, except the person's own folder, with
  their permission, and only what is true of them in any project. The coding
  agent's own memory files are never one of those places.
- Never carry what belongs to one project into another.
- Never drop what was already answered. Correct an answer in place and keep the rest.
- Never mark a step `advanced` or `closed` with a main question unanswered.
- Never say something was saved when it was not. If a file cannot be written,
  say which one and why, and put what would have been saved in your reply so it
  is not lost.
