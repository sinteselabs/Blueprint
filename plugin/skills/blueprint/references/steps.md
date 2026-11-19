# The five steps

A step produces a document. Each has a few main questions, and it moves on when
they are answered. The steps, in order: system description, requirements,
modeling, architecture, plan.

## How a step moves

| Situation | Meaning |
|---|---|
| `not-started` | No main question of the step was asked yet |
| `open` | A main question still has no answer |
| `advanced` | Every main question is answered. The next step starts now, and this step's document is written |
| `closed` | The step's document is ready |

- A step never waits for approval. When its last main question is answered,
  write its document and go to the next step in the same message.
- More than one step can be under way. An answer that settles a question of a
  later step counts for that step.
- A detail that was not needed to move on is a refinement question: it is asked
  later, alone, only when you cannot go on without it.

## Before the first step

Two questions, asked together with the first block of the system description:

1. **The language of the documents.** Propose the language the person is writing in.
2. **Whether more than one person will develop the project.** It decides whether
   the project gets playbooks by role.

Then work out the kind of project from five facts: it has screens, it stores
data, it holds personal data, it is used by command or by code, it calls a
model. Take them from what the person said; deduce what they did not say, and
leave `unknown` what you cannot tell yet. Say in one line what you deduced and
which documents the project will have because of it
([documents.md](documents.md) has the table). The person corrects it if it is wrong.

## 1. System description

Step name in the state: `system-description`.

Main questions:

1. What problem the system solves, and for whom
2. What the person wants to achieve with it
3. How it reaches the people who use it: website, app, command line, library
4. What stays out of the first version

Document: `system-description`. It closes when it says who uses the system, the
goal, how it is delivered and the scope.

## 2. Requirements

Step name in the state: `requirements`.

Main questions:

1. What each kind of user must be able to do, and what only some of them may
   do or see
2. What limits the project: budget, deadline, law, what the person already uses
3. How to know it worked

Who may do what is part of the first question as soon as there is more than one
kind of user: an action that only one role may take, data that one role must
not see. Each rule becomes a requirement like any other, and a row of the "Who
may do what" table of the requirements document.

The non-functional requirements are rarely said unprompted, and the ones below
are costly to add once the code exists. For each, deduce what you can from what
the person said, write it as a deduced requirement with a number or a level,
and say it in one line, so they can correct it:

- **Languages and places:** which languages the product speaks, and whether
  currencies, time zones or date formats vary. One language is the default when
  nothing points at more.
- **Accessibility,** when it has screens: the level the screens meet. WCAG 2.2
  level AA is the default for anything the public uses; a law of the person's
  country may require it.
- **Devices:** the telephones, computers and browsers that must work.
- **Speed and availability:** how long the main action may take, and when the
  system may be down. A number from the person, or one deduced from how it is
  used.

Ask one of these as a refinement question only when you cannot deduce it and
the answer changes the architecture: more than one language from the start, or
a system that must never stop.

Document: `requirements`. It closes when every requirement can be tested and
says where it comes from, every non-functional one has a number or a level, and
the limits the person declared are in the state as criteria.

## 3. Modeling

Step name in the state: `modeling`.

Main questions, by the kind of project:

- always: the journeys that cannot go wrong;
- when it stores data: what the system stores, whether there is personal data,
  and whether data that already exists (a spreadsheet, an old system) has to
  come in;
- when it has screens: which are the main screens, and whether a visual
  identity already exists, and where;
- when it is used by command or by code: which commands or calls it offers;
- when it calls a model: what the model does in the product, and what the
  product does when it gets it wrong.

Documents: the ones the kind of project brings
([documents.md](documents.md) has the table and the templates). One question of
this step usually brings one document: the journeys bring `use-cases`, what is
stored brings `data-model` and, when there is personal data,
`data-classification`, the screens bring `wireframes` and `design` (the
visual identity, or where the existing one lives), the commands bring
`interface-contract`, and the model brings `ai-features`.

Write each one from what the person answered, and no more: a field nobody asked
for is a field to maintain. What they did not say is left as an open point of
the document, not invented. The step closes when the documents the project's
kind asks for are ready.

## 4. Architecture

Step name in the state: `architecture`.

Main questions: one for each decision that is costly to undo in this project.
List them when the step opens:

- the stack;
- where it is hosted;
- how personal data is handled, when the project holds personal data;
- anything else that generates cost.

Each one is asked as a costly decision ([conduct.md](conduct.md)): options, a
recommendation, and the person chooses. Each option is weighed against the
non-functional requirements and the limits the person declared: one that
cannot meet one of them says so.

Documents: `architecture`, with `research` for what was researched and
`decisions` for each decision.

The architecture is more than the stack. From the decisions, the requirements
and the modeling documents, write what a task will need and should not have to
guess, each part only when the project has it:

- the modules, what each owns and what it offers the others, when a task could
  cross a boundary between them;
- each journey that cannot go wrong as a flow: a sequence when it crosses
  parts, its states when something in it has a lifecycle;
- what happens when something fails halfway: a service that does not answer, a
  write in two places, two people changing the same thing at once, one row
  each, numbered F-01;
- how each non-functional requirement is met and checked, one row each,
  numbered Q-01;
- what it costs to run, when something generates cost or the person declared a
  budget.

This is deduced, not asked. Only two kinds of question come out of it: what the
user sees when something fails, asked as a refinement question when the person
did not say it, and a new costly decision, asked as one.

**Check it against the requirements before the step closes.** Go through every
requirement and every limit in the state: each one has a part that serves it,
each non-functional one has a target and a way to check it, the running cost
fits the budget. A gap is fixed in the architecture when it is small, brought
as a costly decision when it is costly, or left as an open point with what
depends on it. Write the result in the architecture, gaps included. A check
that could not be done, because the requirements are not numbered or a
document is missing, is said, not skipped.

The step closes when every costly decision is in the decisions record, decided
or left open with what depends on it, and the architecture is written and
checked against the requirements.

## 5. Plan

Step name in the state: `plan`.

Main questions:

1. What comes first
2. How the work is checked and released: which tests run on their own, and how
   a version reaches the people who use it
3. Who does what, only when more than one person develops

Most of the second question is deduced from the architecture and the
decisions: the stack brings its test runner, the hosting brings its
environments and its way to release. Say what you deduced, and ask only what is
left: whether a change waits for the tests to pass on its own, and who lets a
version out. A choice here that generates cost, such as a paid service to run
the checks, is a costly decision ([conduct.md](conduct.md)).

When there is no code yet, the first phase lays the ground: the project runs, a
test runs and passes, and when the project is hosted, a first version reaches
that place. Every later task is delivered on top of it, so the "How to test" of
the first feature already has something to run.

When the step opens, before the tasks, write the test plan with the
`blueprint-record` skill, when the project has one: a row for each quality and
failure row of the architecture, each AI feature's examples and the
accessibility level, each at its level. Every task that implements a row lists
it in its spec's Tests line, and the row names the task.

Each task names the tasks it needs, and fits in one delivery someone can review
in one sitting. A task that will not fit is split while planning, not during
delivery. A task with a choice in it gets the spec's "How it is built".

Documents: `plan`, one spec per task, and `test-plan` when the project has
one. The step closes when
there are phases, tasks, a spec for every task, every row of the test plan that
comes from the architecture or the AI features names its task, and the plan
says how the project is run, tested and, when it reaches people, released.

## After the plan

Prepare the repository for development with the `blueprint-setup` skill: the
Blueprint block of the entry file, with the commands that run, test and build
the project, memory and observability, a roadmap of the code, a playbook per
role when a team develops, and the project check. It is
the last thing the interview does, and it comes before the first task, so that
an agent opening the project finds the rules, the plan, where to look in the
code and where to record.

Then tell the person what they have, in a few lines: the documents, the plan
with a spec per task, the state file that lets any session continue, and the
first task, by its number. Development starts when they say so.

If that skill is not available, say so, and say what is missing: without the
entry file, an agent that opens the project does not know its rules.
