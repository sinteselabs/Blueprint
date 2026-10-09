---
name: blueprint-record
description: Keeps a Blueprint project's state and journal in files, so nothing depends on the conversation. Use at the end of a block of questions, when a decision is taken or left open, when a step closes or a document becomes ready, when a session is ending, or when the user asks to save where the project is. Saves the interview state, updates the project journal, and says in one line what it saved.
---

# Blueprint: record

A project's memory lives in files, not in the conversation. A conversation has a
limit and ends. What is written here is what the next session, another agent or
another person resumes from.

This skill writes inside the project folder only.

## When to record

| What just happened | What to write |
|---|---|
| The person answered a block of questions | The state file |
| A decision was taken, or left open | The decisions record, then the state file |
| A step closed, a document became ready, or a phase of the plan was delivered | The milestones file, then the state file |
| The session is ending, or the person says they are stopping | The session record, then the state file |
| The conversation is getting long | The state file, before anything is lost |

Do not wait for the end of the session to save the state. Save at the end of
every block.

## Where things are

| What | Where in the project | Format |
|---|---|---|
| State file | `.blueprint/state.md` | [references/state-format.md](references/state-format.md) |
| Session records | `.blueprint/journal/sessions/`, one file per session | [references/journal.md](references/journal.md) |
| Milestones | `.blueprint/journal/milestones.md` | [references/journal.md](references/journal.md) |
| Decisions record | `decisions.md` in the documents folder (the state's `documents_at`) | [references/journal.md](references/journal.md) |

Templates are in `assets/`: `state.md`, `session.md`, `milestones.md` and
`decisions.md`. `assets/state.example.md` is a filled state to compare against.

Read the format reference before writing a file for the first time in a session.

## Saving the state

1. **Find the file.** Look for `.blueprint/state.md` in the project root. If you
   are in a subfolder, look in the folders above before concluding there is none.
   Never create a second state file inside a project that already has one.
2. **If there is none,** create `.blueprint/state.md` from `assets/state.md`.
   Leave no `{{placeholder}}`: where something is not known yet, write `unknown`
   and `-` in the facts table, and `None yet.` in an empty section. The main
   questions of each step come from whoever is conducting the interview; if you
   were not given them, ask, do not invent them.
3. **If there is one, read it first.** Start from what the file says, not from
   what you remember of the conversation. Change only what changed.
4. **Update what the block brought:**
   - under `## Answers`, what the person answered, in a few lines, under a
     heading `### <step> · <block title>`;
   - under `## Main questions`, tick the questions that are now answered;
   - in `## Steps`, the count (`2 of 4`) and the situation of each step;
   - in `## Documents`, the situation and the place of each document;
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

Keys, headings and the values listed in the format stay in English, exactly as
written there. What the person said and what you write about it are in the
project's document language.

## Recording a decision

1. Open `decisions.md` in the documents folder. If it does not exist, create it
   from `assets/decisions.md`.
2. Add an entry at the end, numbered after the last one: `D-001`, `D-002`.
   Fill every line of the entry. `Reason` names the criterion that decided it.
3. A decision that is left for later is recorded too, with the situation `open`
   and what depends on it.
4. Never rewrite an entry. When a decision changes, add a new entry and set the
   old one's situation to `replaced by D-NNN`.
5. If the decision left something to verify, write it in `To test`. It goes into
   the test plan. It is not tested before deciding.
6. Add the decision to `## Decisions` in the state file and save the state.

## Recording a milestone

Add one line at the end of the table in `.blueprint/journal/milestones.md`
(create the file from `assets/milestones.md` if it does not exist): the date,
what was reached, and what is possible now that was not before.

## Recording the session

When the session is ending:

1. Create `.blueprint/journal/sessions/YYYY-MM-DD-HHMM-agent.md` from
   `assets/session.md`, with the time the session started, in UTC, and your name
   in lowercase with hyphens: `claude-code`, `codex`, `antigravity-cli`.
2. Fill the four parts: what was asked, what was done, what was decided, and
   what was left open with the next step.
3. Save the state file last, so `## Next question` says where the next session
   starts.

## When a tool keeps the memory

The state's `memory` and `observability` fields say `journal` or name a tool.
When they name a tool, write the session and the decisions there, following
that tool's own instructions, and keep the state file in the project either way.
If the tool does not answer, say so in one line and write to the journal until
it is back.

## Never

- Never write a key, a token or a password in any of these files.
- Never write outside the project folder.
- Never drop what was already answered. Correct an answer in place and keep the rest.
- Never mark a step `advanced` or `closed` with a main question unanswered.
- Never say something was saved when it was not. If a file cannot be written,
  say which one and why, and put what would have been saved in your reply so it
  is not lost.
