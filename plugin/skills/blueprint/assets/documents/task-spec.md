# {{Task name}}

<!-- Template. Write the spec in the project's document language, headings and
labels included. Replace every {{placeholder}} and remove these comments. One
file per task, in the specs folder beside the plan, named with the phase and the
task number: 01-01-task-name.md. A bug fix adds, at the end of the line
below: · **Bug:** {{blocks / has a way around / cosmetic}}, breaks {{FR-03}}. -->

**Phase:** {{1 · Name}} · **Situation:** {{not started / in progress / to test / done}} · **Needs:** {{the tasks that must be done first, by number: 01-01. "Nothing" when it can start now.}}

## What it does

{{What exists when the task is finished.}}

## What it does not do

{{What is left out on purpose, and where it belongs.}}

## Done when

- [ ] {{Something that can be checked.}}

## Tests

<!-- Only the levels the plan's "How it is built and checked" names. Drop a
level the task adds nothing to. -->

- **Unit:** {{The rules this task's functions hold, one test each.}}
- **Integration:** {{What it does with the data or an outside service: the database, an API, a queue, the model.}}
- **End to end:** {{The journey a person goes through that this task makes or changes.}}
- **Rows of the test plan:** {{The rows this task's tests cover, by number. "None" when none.}}

## How it is built

<!-- Only when the task is not obvious from what it does: drop this section
for a task one commit settles with no choice to make. -->

- **Approach:** {{How it will be done, in two or three lines, and the option set aside when there was one.}}
- **What it touches that others use:** {{An interface, a table, a command or a shared module this task creates or changes, and who depends on it. "Nothing" when nothing.}}
- **Risk:** {{What could go wrong, and how the task finds out early: a test, a trial on real data, a question to the person.}}

## Where in the code

{{The areas of the code roadmap this task touches, by name, so the agent reads
only those. For code that does not exist yet, the planned area it will create.}}

## Comes from

{{The requirements and decisions this task serves: FR-01, D-002.}} These are the
identifiers the code will carry as anchors, so that anyone can ask why that code
exists and get the answer from the code itself.

## Result of the delivery

{{Written when the task is delivered, from the review brief: what changed, which
requirement it serves, which decision it depended on, what was assumed, what
could not be verified, and where to look first — the two or three riskiest
places, hardest first. For a bug fix, the run of its test that failed before
the fix. Until then: "To be written on delivery."}}

## How to test

{{Written when the task is delivered: what to run or open, and what should be seen. Until then: "To be written on delivery."}}
