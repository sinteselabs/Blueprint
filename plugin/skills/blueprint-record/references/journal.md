# The project journal

The journal is how a project keeps its own history when no memory or
observability tool is connected: what each agent session did, what was decided
and which milestones were reached. It is plain Markdown, committed with the
project, so another person, another machine or another agent reads the same
history.

When a tool is connected, the same records go to the tool and the journal is not
needed for that part: the state file's `memory` and `observability` fields say
which is in use.

## The three records

| Record | Where it lives in the project | Template | Written |
|---|---|---|---|
| Session record | `.blueprint/journal/sessions/`, one file per session, named `YYYY-MM-DD-HHMM-agent.md` | [session.md](../assets/session.md) | At the end of every agent session |
| Milestones | `.blueprint/journal/milestones.md`, one file | [milestones.md](../assets/milestones.md) | When a step closes, a document becomes ready, a phase of the plan is delivered, or a version is released |
| Decisions record | `decisions.md` in the documents folder, one file | [decisions.md](../assets/decisions.md) | Every time a decision is taken, and when one is left open |

Times are in UTC. The agent's name in a file name is lowercase with hyphens:
`claude-code`, `codex`, `antigravity-cli`.

## A session record as a declaration

When more than one agent works on the project at once, a session record is
opened when the session starts, not when it ends, and its `Status` and `Taking`
lines tell the other agents what is taken. It lives in the main checkout, which
every worktree on the machine can read.

| Status | Meaning |
|---|---|
| `in-progress` | Being worked on now. What `Taking` names is held |
| `paused` | Stopped mid-way, to be resumed. Still holds what it names |
| `waiting` | Blocked on the person or on another record: the record says on whom, and for what |
| `done` | Finished: the record names the commit, the branch or the deploy |
| `abandoned` | Dropped: the record says why |

A record of a session that worked alone has `Status: done` and `Taking: -`.
A record written before these lines existed is read as `done`.

## Rules

1. A record is never rewritten. A decision that changes gets a new entry, which
   says which entry it replaces. A session record is filled in while its
   session lasts, and not touched once it is closed.
2. Never write a key, a token or a password in a record.
3. A decision that left something to verify says so in its `To test` line, and
   that item goes into the test plan. It is not tested before deciding.
4. Say in one line what was recorded.
