# The project check, by reading

What to verify in a Blueprint project. Each item is something that can be
looked at, and each problem is reported with how to fix it. Nothing is changed.

Report the result as one line per problem. When there is none, one line says so.
Always say that the check was made by reading, because a script does it more
reliably and is not part of this version.

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
   written, or it was moved.
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

## Nothing twice

12. **One state file.** No second `.blueprint/state.md` in a folder inside the
    project.
13. **One of each document.** No two files with the same purpose, such as two
    requirements documents under different names.
