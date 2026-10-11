# The project check, by reading

What to verify in a Blueprint project. Each item is something that can be
looked at, and each problem is reported with how to fix it. Nothing is changed.

**The script in this skill, `check.js`, does all of this.** Run it, and this
list is what it goes through. Read the list yourself only when there is no Node
on the machine or the script cannot run, and then say that you checked by
reading.

Two items no script can settle, which it reports as skipped: whether a memory or
observability tool is answering, and whether two documents with different names
serve the same purpose. Those are for you to look at.

Report the result as one line per problem. When there is none, one line says so.

## The state file

1. **It can be read.** `.blueprint/state.md` opens with a header between two
   `---` lines and has its ten sections: Project kind, Criteria the person
   declared, Steps, Documents, Main questions, Refinement questions left for
   later, Answers, Decisions, Open points, Next question.
2. **The counts agree.** For each step, the count in the `Steps` table, written
   like `2 of 4`, equals the ticked and total questions under that step in
   `Main questions`.
3. **The situations agree with the counts.** A step that is `not-started` has
   no question answered. One that is `open` has at least one unanswered. One
   that is `advanced` or `closed` has all of them answered.
4. **No template placeholder is left:** no `{{...}}` anywhere in the file.

## The documents

5. **Every document marked `ready` exists** at the place the state gives in
   `Where`. A ready document that is missing is a problem: either it was never
   written, or it was moved. Do not look for it outside the project folder: the
   person says where it went.
6. **No ready document carries a leftover of its template:** no `{{...}}` and
   no template comment.
7. **Links between documents lead somewhere.** A relative link in a document
   points at a file that exists.
8. **The plan's tasks have their specs.** Each task in the plan names a spec
   file, and the file exists.

## The decisions

9. **Every decision listed in the state is in the decisions record,** under the
   same number. A decision the state calls `open` is `open` there too.

## The journal and the tools

10. **When `memory` or `observability` is `journal`,** the folder
    `.blueprint/journal/` exists and has at least one session record, unless
    the project was created in this very session.
11. **When one of them names a tool,** say which tool, and whether you could
    see that it answers. If you have no way to check it, say that it was not
    checked. Do not report it as working.

## The prepared repository

Only when the plan is closed. Before that, none of this is missing: it is not
written yet.

14. **The entry file has the Blueprint block.** `AGENTS.md` at the project root,
    with `<!-- blueprint:start -->` and `<!-- blueprint:end -->`. Without it, an
    agent that opens the project does not know its rules: the fix is the
    `blueprint-setup` skill.
15. **What the block names exists:** the documents folder, the plan, the state
    file and the journal, at the paths the block gives.
16. **`CLAUDE.md` and `GEMINI.md` name `AGENTS.md`,** so an agent that reads
    only its own file reads the same rules. Claude Code reads `CLAUDE.md` first;
    the Antigravity CLI reads `GEMINI.md` and does not read `AGENTS.md`.
17. **A playbook per role,** only when the state's `developers` is more than 1.

## Nothing twice

12. **One state file.** No second `.blueprint/state.md` in a folder inside the
    project.
13. **One of each document.** No two files with the same purpose, such as two
    requirements documents under different names.
