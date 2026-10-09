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

1. What each kind of user must be able to do
2. What limits the project: budget, deadline, law, what the person already uses
3. How to know it worked

Document: `requirements`. It closes when every requirement can be tested and
says where it comes from, and the limits the person declared are in the state as
criteria.

## 3. Modeling

Step name in the state: `modeling`.

Main questions, by the kind of project:

- always: the journeys that cannot go wrong;
- when it stores data: what the system stores, and whether there is personal data;
- when it has screens: which are the main screens;
- when it is used by command or by code: which commands or calls it offers.

Documents: the ones the kind of project brings. **They are not written yet in
this version of Blueprint.** Ask the main questions, keep the answers in the
state, and when the step advances tell the person in one line that the modeling
documents will be written when Blueprint knows how. The step stays `advanced`.

## 4. Architecture

Step name in the state: `architecture`.

Main questions: one for each decision that is costly to undo in this project.
List them when the step opens:

- the stack;
- where it is hosted;
- how personal data is handled, when the project holds personal data;
- anything else that generates cost.

Each one is asked as a costly decision ([conduct.md](conduct.md)): options, a
recommendation, and the person chooses.

Documents: `architecture`, with `research` for what was researched and
`decisions` for each decision. The step closes when every costly decision is in
the decisions record, decided or left open with what depends on it, and the
architecture is written.

## 5. Plan

Step name in the state: `plan`.

Main questions:

1. What comes first
2. Who does what, only when more than one person develops

Documents: `plan`, and one spec per task. The step closes when there are phases,
tasks and a spec for every task.

## After the plan

Preparing the repository for development (the entry file, memory and
observability, the project check) is not built yet in this version of
Blueprint. Tell the person so, and tell them what they have: the documents, the
plan with a spec per task, and the state file that lets any session continue.
