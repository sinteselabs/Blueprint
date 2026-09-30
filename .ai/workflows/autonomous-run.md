# Autonomous Runs (optional)

<!--
  OPTIONAL. Enabled at project kickoff (Step 0, "Autonomous runs"). If the user
  declined, this file, its row in `.ai/ai.md` and the "Autonomous runs" hard rule
  are deleted. If enabled, fill the {{PLACEHOLDERS}} below and delete this comment.
  Requires project memory (lore): see project-memory.md.
-->

An **autonomous run** is a stretch of work, often overnight, in which one or more
agents take the project's pending tasks one after another **without stopping to ask
the user**. They coordinate through lore, so every agent picks a different task and
everything merges cleanly. Each decision the user would normally make is taken by the
agent (the most recommended option) and written down for review. Anything only a
person can do becomes a to-do. The user reviews afterwards and anything they disagree
with gets fixed.

**When it applies:** whenever the user says we are doing an autonomous run. For the
length of the run this page adds to the agent-work rule in
[project-memory.md](project-memory.md) and, where they differ, wins.

## Kickoff: settle three things, then ask nothing else

Confirm to the user that you understood. **If they have not already said so, ask these
once, together:**

1. **Merge and deploy:** may agents merge to `{{MAIN_BRANCH}}` and deploy? Without a
   yes, stop at a pushed branch plus a to-do.
2. **Scope:** all pending tasks, or a named set (an epic, a phase, a list)?
3. **End:** until the scope is done, or until a time?

After kickoff, do not ask the user anything until the run ends. Decide, record, and
continue. This suspends the "specification is collaborative" rule for the length of
the run. The recorded decisions are what makes that safe.

## The board

The first agent writes a pinned lore page `work/<YYYY-MM-DD>-run-board.md` with the
kickoff answers and the scope as an ordered catalogue: each task with its PM-tool
link and what it depends on. The board is **a catalogue, not the claims**: claims are
`work/` pages. Nobody claims by editing the board or another agent's page.

## Claiming a task — in this order

1. Run `memory_query` with query `agentwork` and `pin_first=true`. Read every
   `work/` page that is `in-progress`, `paused` or `waiting-response`.
2. A task is **taken** when any of these holds:
   - a `work/` page names it;
   - its PM-tool status is `In progress` and was updated in the last few hours;
   - **a git branch or worktree exists whose name matches it** (check
     `git worktree list` and `git branch -a`).

   A branch with no page is still somebody's claim: stop and look.
3. Pick the first untaken task whose dependencies are done.
4. **Write your pinned `work/` page first.** It names the task, your worktree and
   branch, and its **Areas** (files, migration numbers, production). Then set the
   task `In progress` in the PM tool. **Only then** create the branch or worktree.
5. **Right before your first code edit, re-run the step 1 query.** If someone
   claimed the same task meanwhile, the earlier `work/` page keeps it. The later
   agent sets its own page to `abandoned` and picks again. It does not finish in
   parallel.

**Handing a task to another agent:** write the handoff on a `work/` page, with status
`waiting-response`, naming the agent. Do not rely on lore messages alone: agents read
work pages, not the inbox.

## Areas that collide

- **Database migrations:** `{{MIGRATIONS_DIR — or "none"}}`. Claim the next number on
  a pinned lore page, `notes/migration-numbers.md`, **before** writing the file. The
  first claim to reach `{{MAIN_BRANCH}}` keeps the number; a later branch renumbers
  on rebase.
- **Shared files** everyone touches: `{{e.g. the router, CHANGELOG, the UI entry
  file}}`.
  - Keep changes small and local.
  - Resolve conflicts on rebase, keeping both sides.
  - Never revert another agent's lines.
- **A merged change you disagree with:** don't overwrite it. Push your alternative
  as a branch and write a to-do for the user to choose.

## Finishing a task

1. Rebase on the latest `{{MAIN_BRANCH}}` and resolve conflicts.
2. The gates pass: `{{GATES — e.g. format check, lint, full test suite}}`.
3. If merging is approved: fast-forward `{{MAIN_BRANCH}}`. If that is rejected,
   someone merged first: rebase and repeat. Never force-push.
4. If deploying is approved: `{{DEPLOY PROCEDURE, or "not applicable"}}`.
   - Take the production lock first: a pinned lore page `_rules/production-deploy-lock.md`
     set to HELD, plus `{{a lock file on the host, if any}}`. Never overwrite a
     lock someone else holds; wait for it.
   - Back up before switching.
   - Verify on the live system.
   - Record what runs and how to roll back.
   - Release the lock.
5. Set the task to `To test` in the PM tool; `Done` stays the user's word. Close
   your `work/` page as `done`, with the commit, the deploy, and where the decisions
   are.
6. Delete your worktree once its branch is merged and nothing more is planned
   there (Hard Rule 12): `git worktree remove`, delete the branch, `git worktree
   prune`. Check "merged" against the remote `{{MAIN_BRANCH}}`, not a stale local one.

## Decisions

For each decision taken for the user, write one lore page
`decisions/autonomous/<YYYY-MM-DD>-<slug>.md` with:
- the question;
- the options;
- **what you chose and why**;
- how to undo it.

Link it from your work page and the task.

## To-dos for the user

Anything only a person can do gets one pinned lore page `todo/<YYYY-MM-DD>-<slug>.md`.
Examples:
- credentials, a DNS or dashboard change, a purchase;
- legal sign-off, a real-device check, talking to people;
- spending money, posting outside the project;
- choosing between two merged approaches.

Each page says exactly what to do, why, and what is blocked until it is done. Then
move on.

## Ending the run

Each agent writes a pinned lore page `notes/<YYYY-MM-DD>-<agent>-run-summary.md`
covering:
- what shipped (commits, deploys);
- what was decided without code;
- its to-dos for the user;
- what went wrong.

The last agent to finish updates the board.
