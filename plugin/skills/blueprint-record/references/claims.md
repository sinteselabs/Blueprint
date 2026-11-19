# Claims: what each agent is taking

When more than one agent works on a project at the same time, each says what it
takes before it starts, in a place every other agent reads. That statement is
its claim. Where it goes depends on where the agents run:

| The agents run | The claim goes | Who sees it |
|---|---|---|
| On one machine | The session record, opened at the start, in the main checkout's `.blueprint/journal/sessions/` | Every worktree of that clone |
| On more than one machine | One file per session in `.blueprint/work/`, on the branch `blueprint-work` of the shared remote | Every clone that can fetch from that remote |
| On more than one machine, with no shared remote | Nowhere they all read | Nobody: say so, and the person splits the tasks among them |

Say which route the project uses when you claim. The branch route works on one
machine too, so a project whose agents sometimes run elsewhere can use it
always. A memory tool the state names may carry the claim as well; it is never
required, and the branch or the folder is what counts.

## The session record and the claim

The session record is the history of the session: what was asked, done,
decided and left open. On the branch route, the work file is only the live
claim, and it is closed or removed when the session stops; the session record's
`Taking` line keeps what was taken, for history.

## The work file

`.blueprint/work/<session>.md`, where `<session>` is the session record's name
without `.md`, such as `2026-11-18-0930-codex`. From
[claim.md](../assets/claim.md): the task, the files or areas, the numbers
reserved (a migration number, a `D-` or `T-` number), the status, the machine or
session, and when it was last updated, in UTC.

| Status | Meaning |
|---|---|
| `in-progress` | Being worked on now. What the file names is held |
| `paused` | Stopped mid-way, to be resumed. Still holds what it names |
| `waiting` | Blocked on the person or on another claim: the file says on whom, and for what. It holds nothing yet |
| `done` | Finished or dropped, with the commit or the reason. It holds nothing, and may be deleted |

## The branch, through a worktree of its own

The claims live on their own branch so they never enter the main branch's
history or a task's pull request. Each clone checks that branch out once, in a
worktree of its own, outside the project folder or in a folder git ignores,
such as `../<project>-work`. Every agent of that clone uses the same one, and
`git worktree list` shows where it is: below, `<work>` is its absolute path. A
worktree is the simplest safe way: the agent's own worktree and branch stay
untouched, and git refuses to check one branch out twice in one clone. The
commands run from any worktree of the clone.

**Once per clone,** when the branch is on the remote:

```
git fetch origin blueprint-work
git worktree add <work> blueprint-work
```

**The first time anyone claims,** when the branch does not exist yet, make it
with no history from the main branch:

```
git worktree add --detach <work>
git -C <work> switch --orphan blueprint-work
mkdir -p <work>/.blueprint/work
```

Then write the first claim and push it as below, with `git -C <work> push -u
origin blueprint-work`.

**To claim:**

```
git -C <work> pull --rebase --autostash origin blueprint-work
```

`--autostash` is needed because the worktree is shared: without it, git refuses
to pull while another agent of this clone has a claim written and not yet
committed, and puts that claim back untouched once the pull is done.

Read every file in `<work>/.blueprint/work/`. On an overlap, do not start: see below.
Otherwise write your file, and commit only that file, because another agent of
this clone may have staged its own:

```
git -C <work> add .blueprint/work/<session>.md
git -C <work> commit -m "claim: <task>" -- .blueprint/work/<session>.md
git -C <work> push origin blueprint-work
```

**A rejected push means someone claimed first.** Run `git -C <work> pull
--rebase --autostash origin blueprint-work`, read the files again, and decide again: the claim already on
the remote keeps what it took, and you take another task or wait. Then push.
Never force-push this branch: it would delete other agents' claims. A commit
refused because git's index is locked means another agent of this clone is
committing: try again a moment later.

**To update or release,** change or delete your file, and commit and push it
the same way. Update it when what you take changes, and at least once an hour
while you work, so the time in it shows it is alive. Release it every time you
stop: `done` or deleted when finished or dropped, `paused` or `waiting`
otherwise.

## Overlaps and stale claims

A claim overlaps yours when it takes the same task, the same files, the same
number or the deploy, and its status is `in-progress` or `paused`. Take another
task whose files are free, or claim as `waiting`, naming the claim you wait on,
and read again every few minutes.

A claim whose last update is more than two hours old may be stale: its session
may have ended without releasing it. Report it to the person or the coordinator,
with the file and its time, and keep waiting. Never take it over, edit it or
delete it yourself: only the person, or the coordinator they named, does that.
