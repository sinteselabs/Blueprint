# When more than one agent works

This page is for you, the agent preparing the repository. It says when the
entry file gets the section for parallel and unattended work, what goes in it,
and why each rule is there, so you can answer the person when they ask.

Two agents writing in the same folder at the same time produce half-applied
edits, a `git status` that mixes unrelated changes, and commits that carry
another agent's unfinished work. The rules below prevent that. One agent
working alone, one task after another, needs none of them.

## When the section is written

Write it when either holds:

- more than one agent will write to the repository at the same time: the
  state's `developers` is more than 1, or the person runs several agents at
  once;
- the person will let an agent work without watching, such as overnight.

The state says how many people develop, not how many agents. When it does not
settle the question, ask once, in one line, with the reason: "Will agents work
on this project at the same time, or without you watching? If so, the entry
file gets the rules that keep them from overwriting each other." A no, or no
answer, means the section is left out.

## One agent, one worktree, one branch

- **Every agent that writes gets its own worktree and its own branch,** made
  from the up-to-date main branch, never from another agent's branch: that would
  tie two tasks that were meant to be independent. An agent that only reads,
  such as a review or a search, needs no worktree.
- **Tasks that share a file, a migration or an order are not parallel.** They
  are done one after another, in the plan's order.
- **The worktrees live outside the project folder, or in a folder that git
  ignores.** If the project keeps them inside and its `.gitignore` does not name
  that folder, add the line and say so.
- **Each agent commits only on its own branch,** and never works in the main
  checkout or another agent's worktree.

## What a worktree does not isolate

A worktree isolates the tracked files and the branch. Everything outside git is
shared, or missing:

| Shared | What goes wrong | What to do |
|---|---|---|
| `.env` and local secrets | Not tracked, so a new worktree does not have them | Copy them into each worktree when it is made. Never commit them |
| Installed dependencies (`node_modules`, `.venv`) | Not copied into a new worktree | Install them in each worktree, or share a cache on purpose |
| Ports of the running app and of a local database | Two agents bind the same port | A different port per agent, or only one agent runs the app |
| Local database and migrations | Two migrations at once corrupt it, and two branches take the same migration number | One database per worktree, or one migration task at a time. The migration number is declared before the file is written |
| `.blueprint/state.md`, the decisions record and the test plan | Each worktree has its own copy, and two agents take the same `D-` or `T-` number | Only the coordinator writes them, in the main checkout |
| Deploys and remote records (a tracker, a hosting dashboard) | Two agents change the same thing | The coordinator does it, one at a time |

If two tasks need the same item of this table and it cannot be split, they are
not independent: do them one after another.

## Declaring the work

Agents in different worktrees do not see each other's files. What they see is
one folder: the main checkout's `.blueprint/journal/sessions/`. Before an agent
starts, it opens its session record there, with what it is taking: the task,
the files or areas it touches, the migration number it will use. It reads the
other open records first and, on an overlap, waits or takes another task. It
closes the record every time it stops. The `blueprint-record` skill has the
format and the statuses.

Agents on another machine do not see that folder. When agents work from more
than one machine, the declaration goes where all of them read, such as the
memory tool the state names. Without one, say so: they cannot see each other's
work, and the person splits the tasks among them.

## The coordinator

The coordinator is the agent or the person that starts the others and
integrates their branches. When people each start their own agent, whoever
merges a branch into the main branch is the coordinator for that merge.

1. **Integrate one branch at a time,** after its agent has finished and
   reported. Conflicts are resolved in the main checkout, keeping both sides,
   and never by reverting another agent's lines.
2. **Run the tests the work mode says** before merging, or before pushing or
   deploying.
3. **Record for everyone:** the state, the decisions and the test plan, from
   what each agent reported in its session record. Commit the session records
   written in the main checkout.
4. **Remove the worktree once its branch is merged,** in the same session.
   Check "merged" against the remote main branch, because a local one is often
   behind: `git merge-base --is-ancestor <branch> origin/main`. Then
   `git worktree remove`, delete the branch, and `git worktree prune`. A worktree
   with uncommitted changes or unmerged commits is not finished: keep it, or ask
   the person before discarding anything. A worktree whose session record is
   still open belongs to an agent that is working: never remove it. Each
   worktree holds its own dependencies and build output, and left behind they
   fill the disk.

## The work mode

Parallel work spends most of its tokens on agents rereading the code and
rerunning tests their change does not touch. The work mode says how much of that
the project pays for. Ask the person once which one, with the recommendation:
token-saving for the everyday flow of features and fixes, full for risky work.
They change it later by saying so.

| | Full | Token-saving |
|---|---|---|
| Model and effort of each worker | The strongest the person uses, for every worker | A cheaper model or a lower effort for small, clear tasks; the strongest for hard or cross-cutting ones. The coordinator picks per task |
| Tests a worker runs before reporting | Every check the entry file lists | The fast checks (format, lint, types), its new tests, and the tests of what its change touches |
| Tests the coordinator runs | Every check again, on each branch, before merging it | Every check once, on all the finished branches merged together, before pushing or deploying. A failure is traced to its branch by the area of the failing test |
| What a worker reports | Complete | Short: what changed, the tests added, what ran and its result |

Full suits a data migration, security, a release, or a first pass in an area
nobody has worked in. In both modes every change is proven by tests, and a
check that could not be run is said, never counted as passed.

## Unattended runs

The entry file says, in a few lines, what an agent does when the person starts a
run and leaves: three questions before it starts, a costly decision taken as
provisional, and a summary at the end. The `blueprint` skill has the whole of it.
