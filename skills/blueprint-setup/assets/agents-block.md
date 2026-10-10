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
| The journal: one record per session, and the milestones | `.blueprint/journal/` |

### How to work here

1. **Read `.blueprint/state.md` before you answer.** It says where the project
   is. Never act as if you remembered a conversation: it may have been another
   session, another day or another agent.
2. **One task at a time, from the plan, in order.** The task's spec says what it
   does, what it does not do, and when it is done.
3. **Every delivery says how to test it:** what to run or open, and what should
   be seen. It goes in the spec's "How to test" and in what you tell the person.
4. **Record what happened.** At the end of a session, one record in
   `.blueprint/journal/sessions/`. A decision that is costly to undo goes to
   {{docs/decisions.md}} with its reason, who decided and the date. A phase
   delivered goes to the milestones. {{When a tool keeps the memory: and to
   NAME, following its own instructions.}}
5. **A change the plan does not cover.** If it is small, do it and say in one
   line what you did. Small means: it touches one part of the code, it brings no
   decision that is costly to undo, it brings no new fact about the project (the
   first screen, the first stored data, the first personal data, the first
   command, the first call to a model), and it fits in one task. If it is not
   small, write its spec with the person before you write code.
6. **A decision that is costly to undo is the person's:** the stack, hosting,
   how personal data is handled, anything that generates cost. Bring options and
   a recommendation, and wait.
7. **Never write a key, a token or a password** in a file of this project.

### The method

The documents and the plan of this project were written with Blueprint, and the
rules above come from it. {{How to get the Blueprint skills, when they are not
installed in the agent being used. When you do not know how this project got
them, say instead: this file, the documents and the plan are enough to go on.}}
<!-- blueprint:end -->
