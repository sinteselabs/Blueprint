---
name: blueprint-explain
description: Explains a project from its code instead of from its documents. Use when the user asks why a line, a function or a file is the way it is, where a requirement lives, what a change would break, what to look at first in a delivery or a diff, whether a delivery is small enough to review, or asks to be walked through a codebase. Also use when handing over finished work, to produce the review brief. Answers from the anchors in the code, and never asks the user to read a document.
---

# Blueprint: explain

A project's documents are worth nothing if reading them is the price of
understanding. This skill is the other side: it answers the questions a
developer actually asks, from the code, in seconds, without opening a document.

What someone asks while working, and what answers it:

| The question | The answer |
|---|---|
| Why is this line the way it is? | `why` |
| Where does this requirement live? What would I break? | `trace` |
| What did we promise that nothing implements? | `map` |
| Is this delivery small enough for me to actually review? | `budget` |
| In this diff, where do I look first? | The review brief |
| How does this whole thing work? | The tour |

The rule this skill exists for: **a developer asking "why is this the way it
is?" gets the answer without opening a `.md` file.** If your answer begins with
"let me read the requirements document", the layer has failed.

## How to talk

- Answer in the person's language, in plain words.
- Answer the question asked, then stop. A brief longer than the diff is the
  problem it was meant to solve.
- Say the file and the line, so the person can open it. Never paste a whole file
  into the conversation.
- When the code does not say, say that it does not say. Never invent a reason a
  requirement does not give.

## 1. The engine

The four views are a script, because they must always give the same answer:

```
node <this skill's folder>/explain.js why <file[:line]> [folder] [--json]
node <this skill's folder>/explain.js trace <ID> [folder] [--json]
node <this skill's folder>/explain.js map [folder] [--json]
node <this skill's folder>/explain.js budget [folder] [--base <ref>] [--json]
```

It only reads. Exit code 0 when it answered, 1 when there was nothing to answer
with or the delivery is over budget, 2 when it could not run. `--json` gives
the same answer for you to read. Whoever installed Blueprint as a CLI has the
same four as `blueprint why`, `blueprint trace`, `blueprint map` and
`blueprint budget`.

If there is no Node on the machine, do by hand what the script does: search the
code for the identifier, and read the row that declares it in the documents. Say
that you answered without the script.

## 2. Answering "why is this the way it is"

1. **Run `why` on the place the person named.** A line number makes the answer
   precise: the nearest anchor at or above that line is the one that explains it.
2. **Say it in one or two lines:** what the code serves, what the requirement
   says, and the decision it depended on, when there is one.
3. **When the file carries no anchor,** say so plainly — a file with no anchor is
   normal, not a defect. Then offer the next best thing: the anchors beside it,
   which the script lists, and what the task spec that touched the file says.
4. **When the anchor is orphaned** — an id in the code that no document has —
   say it, because it is a real finding: either the document lost the
   requirement, or the anchor is wrong. Do not guess which. Ask.

Never answer this question from the conversation's memory. Another session wrote
that code; the anchor is the only thing that survived.

## 3. The review brief, when you hand work over

Whenever you finish a task, a change or anything you are giving back to a
person, the delivery is not the code and not a document: it is the brief.
[assets/review-brief.md](assets/review-brief.md) is the template, with its seven
fields and how to order the riskiest first.

- **Say it in the conversation,** and append it to the task's own spec, under
  "Result of the delivery". It does not get a file of its own: one more file per
  delivery is one more thing to rot.
- **"Where to look first" is the field that earns the brief.** Two or three
  places, hardest first, each with the file, the line and what makes it risky.
  Risk is not size: what touches money, personal data, permissions or deletion
  comes before what is merely long.
- **"What I assumed" and "what I could not verify" are never left empty to look
  finished.** When there was nothing, write that there was nothing — silence in
  those two fields reads as "nothing to check", which is a lie if it is not true.
- **Anchor the code you wrote** before you write the brief, so that `why` answers
  for it from now on. [references/anchors.md](references/anchors.md) has the
  convention.

## 4. The reviewable increment

Understanding is not lost for want of a document. It is lost to the size of the
delivery: nobody reviews 1,800 lines, so nobody understands them.

- **Run `budget` before handing over.** It measures the diff against `HEAD`, new
  files included, and says whether one person can review it in one sitting. The
  default is 400 changed lines and 10 files, and the output always names the
  number it measured against.
- **Over budget: split it, do not apologise for it.** One commit per
  requirement, each one reviewable on its own. Say which commits you propose.
- It is a warning, never a block. The person may want the big delivery anyway,
  and that is their call — but they make it knowing.

## 5. The tour

When someone wants to understand a project rather than a line, do not write them
a document. Walk them through the code.

**Build the tour from `map` and the architecture document**, never from a
description you invent. Five to eight stops, in the order the system actually
executes, and each stop says three things: the file and line, what to notice
there, and which requirement it serves.

The stops worth having, when the project has them:

1. Where execution begins: the entry point, the command, the server.
2. The first boundary it crosses: the route, the handler, the event.
3. Where the main journey's rule is decided — the requirement the project exists
   for. This is the one stop no tour skips.
4. Where data is stored or fetched.
5. Where the costliest decision shows in the code, by its `D-` anchor.
6. Where a test proves the main requirement.
7. Where it is configured, built or deployed.

Rules for a tour:

- **Name files, do not paste them.** The person opens them; that is the point.
- **Fewer stops than five is a fine answer** for a small project. Say that it is
  small and give what there is. Padding a tour to look thorough is the failure
  this whole layer exists to undo.
- **A stop with no anchor and no architecture behind it does not go in.** Say
  "this part says nothing about why it exists" instead of inventing a reason.
- The tour is made on the spot and thrown away. It is never written to a file:
  a saved tour is a document that rots.

## 6. When the project has no anchors yet

`map` saying "0 of N anchored" is the normal state of a project whose code came
before this layer. Say it in one line, without blame, and offer the one cheap
move: as each task is delivered from now on, its code carries the id of what it
serves. Offer to anchor what already exists only for the requirements the person
names — a sweep that puts ids over a whole codebase at once produces anchors
nobody checked, which is worse than none.

## Never

- Never tell the person to read a document to get an answer. That is the failure
  this skill exists to prevent.
- Never invent the reason a piece of code exists. No anchor, no architecture, no
  spec: say that nothing records it.
- Never write or change a file to answer a question. The four views only read;
  the brief is written as part of a delivery, not of an explanation.
- Never paste a document or a whole file into the conversation. Say where it is.
- Never report a requirement as implemented because a task says it is done. The
  anchor in the code is the evidence; the task's checkbox is a claim.
