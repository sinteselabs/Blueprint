<!-- Template for the block that Blueprint keeps in the project's AGENTS.md.
Write it in the project's document language, headings and labels included.
Replace every {{placeholder}} with what the state and the documents say, drop a
row or a rule that does not apply to this project, and remove these comments.
The two marks stay exactly as they are: they are what the next session finds. -->

<!-- blueprint:start -->
## Blueprint

{{One line: what this project is, from the system description.}}

| What | Where |
|---|---|
| The documents | {{docs/}} |
| The plan, and one spec per task | {{docs/plan.md}}, {{docs/specs/}} |
| Where the project is, for any session | `.blueprint/state.md` |
| The decisions, each with its reason | {{docs/decisions.md}} |
| What is left to verify | {{docs/test-plan.md}} |
| Where things are in the code | {{docs/code-roadmap.md}} |
| Why a line of code is the way it is | Ask it: the `blueprint-explain` skill answers from the code |
| The journal: one record per session, and the milestones | `.blueprint/journal/` |

<!-- The commands: from the project's own files (package.json scripts, a
Makefile, pyproject.toml) where the code exists, and from the plan's "How it is
built and checked" where it does not, with the task that creates each one. Drop
a row the project does not have. -->

| To | Run |
|---|---|
| Run it | {{`npm run dev`, or "created by task 01-01"}} |
| Test it | {{`npm test`}} |
| Build it | {{`npm run build`}} |
| Check what runs on every change | {{`npm run lint`}} |

### Decisions not to go against

<!-- From the decisions record: the 3 to 7 decided ones that a task is most
likely to run into, such as the stack, where data lives, how personal data is
handled, what is left out on purpose. One line each, with its id, as the record
words it. Drop this section when the record has no decided decision. -->

Each has its reason in {{docs/decisions.md}}. Do not work against one or argue it
again: changing one is a decision that is costly to undo (rule 9). The session
that replaces one changes its line here.

- {{D-001}} · {{The decision, in one line}}

### How to work here

1. **Read `.blueprint/state.md` before you answer.** It says where the project
   is. Never act as if you remembered a conversation: it may have been another
   session, another day or another agent.
2. **One task at a time, from the plan, in order.** The task's spec says what it
   does, what it does not do, and when it is done. **Say which task you are on,
   by its number and its name, before you start it** — the person has to be able
   to tell which one you chose without reading the plan again.
   It is done when its spec's "Done when" and the plan's "Every task is done
   when" both hold. Run the tests before you say so: a check you could not run
   is said, never counted as passed. A task that adds or changes a command
   above changes its row in the same commit. When it is delivered, its spec's
   situation becomes done, and any document the task made untrue (a command,
   a field, a flow, a path) is corrected in the same delivery, and you say
   which.
3. **Do not read the whole codebase to find where to work.** Open
   {{docs/code-roadmap.md}}, find the area the task touches, and read only the
   paths on its row and the ones it lists under "Also read", with the area's
   gotchas. The row also says how to run only that area's tests, and the
   roadmap's "How code is written here" says how to name, format, handle
   errors, migrate data, branch and commit. Open another file only when the
   task needs it, and add it to the roadmap when you do. A commit that creates,
   moves, renames or deletes a folder or an important file updates the roadmap
   in the same commit.
4. **Every delivery says how to test it, and where to look first:** what to run
   or open, what should be seen, and the two or three riskiest places in what
   changed, hardest first. It goes in the spec's "Result of the delivery" and
   "How to test", and in what you tell the person. Risk is not size: what touches
   money, personal data, permissions or deletion comes before what is long.
5. **The code carries the id of what it serves.** A requirement that became code
   gets its id — {{FR-01}} — in a comment where that behaviour begins, and in the
   name of the test that proves it. That one line is what lets anyone ask "why is
   this the way it is?" and be answered from the code, without reading a
   document. Not every file needs one, and an id that no document has is a
   mistake to report, not to keep.
6. **Deliver in increments someone can review.** One commit per requirement.
   About 400 changed lines or 10 files is what one person reviews in one sitting,
   new files included; past that, split the delivery and say how you split it. A
   change nobody can review is not understood, however well it is documented.
7. **Record what happened.** At the end of a session, one record in
   `.blueprint/journal/sessions/`; when agents work at the same time, it is
   opened at the start (see "When more than one agent works, or no one is
   watching" below). A decision that is costly to undo goes to
   {{docs/decisions.md}} with its reason, who decided and the date. A phase
   delivered goes to the milestones. {{When a tool keeps the memory: and to
   NAME, following its own instructions.}}
8. **A change the plan does not cover.** If it is small, do it and say in one
   line what you did. Small means: it touches one part of the code, it brings no
   decision that is costly to undo, it brings no new fact about the project (the
   first screen, the first stored data, the first personal data, the first
   command, the first call to a model), and it fits in one task. If it is not
   small, write its spec with the person before you write code. A bug is code
   that breaks a requirement: its spec comes from that requirement, by its id.
   When no requirement covers the behaviour, it is not a bug but a change to
   what the system does.
9. **A decision that is costly to undo is the person's:** the stack, hosting,
   how personal data is handled, anything that generates cost. Bring options and
   a recommendation, and wait. In a run no one watches, take the recommended
   option and record it as `provisional`, for the person to confirm or reverse
   (same section below).
10. **Never write a key, a token or a password** in a file of this project.
11. **A change to behaviour comes with its tests,** in the same delivery, at
    the levels the plan's "How it is built and checked" names: unit tests for
    every function with a rule in it, integration tests for what it does with
    the data and with outside services (database, APIs, queues, the model), end
    to end for what a person does with it, in the journeys that cannot go
    wrong. The spec's "Tests" says which. A bug fix starts with a test, named
    with the id of the requirement the bug breaks, that fails before the fix:
    keep that failing run and give it with the delivery, beside the passing one
    after. A bug no automated test can reproduce is said to be one, with what
    was checked instead. A test does not depend on the clock, the time zone,
    the locale, the network or the order the tests run in.
12. **Measure before you assert.** "Faster", "fixed" or "the cause is X" is said
    with the number or the run that shows it, not from reading the code. When
    a measurement contradicts something you already said, say that first.
13. **Fail loudly.** Code that meets a state it did not expect stops with a
    message that names what is missing. It does not fall back to a default,
    skip or swallow the error, and a guard against bad data also reports it.

### The method

The documents and the plan of this project were written with Blueprint, and the
rules above come from it. {{How to get the Blueprint skills, when they are not
installed in the agent being used. When you do not know how this project got
them, say instead: this file, the documents and the plan are enough to go on.}}
<!-- blueprint:end -->
