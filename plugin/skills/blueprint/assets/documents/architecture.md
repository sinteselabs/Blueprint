# Architecture

<!-- Template. Write the document in the project's document language, headings
and labels included. Replace every {{placeholder}}, drop a section that does not
apply, and remove these comments. Keep the prose short: diagrams and tables first. -->

**Project:** {{PROJECT_NAME}} · **Version:** {{0.1}} · **Date:** {{YYYY-MM-DD}}

> **In short:** {{Up to five lines: what the system is made of, where it runs, and the one thing someone must know before changing it.}}

## Overview

```
{{A plain-text diagram: the parts and how data moves between them.}}
```

{{One paragraph: the most important fact about how the system is built.}}

## The parts

| Part | Where it runs | What it does |
|---|---|---|
| {{Part}} | {{Platform or service}} | {{Its job}} |

## Inside the parts

<!-- Only when the system has more than one module or service whose
boundary a task could cross: drop this section otherwise. One row per module.
"Offers" is the internal interface other modules call; nothing else of the
module is called from outside it. -->

| Module | Owns | Offers to the others | Uses |
|---|---|---|---|
| {{Name, as in the code roadmap}} | {{The data and the rules only it changes}} | {{The functions, routes or events others call, with what goes in and comes out}} | {{The modules and services it calls}} |

## How the code is organised

```
{{The folder tree, one line of explanation per folder.}}
```

{{One paragraph: the rule that organises it.}}

## Data

| What is stored | What it holds | Personal data |
|---|---|---|
| {{Table, collection or file}} | {{What it is}} | {{Yes or no, and which}} |

## Main flows

<!-- One flow per journey that cannot go wrong, and per flow that crosses
more than two parts. Steps are enough for a simple flow. A flow that crosses
parts gets a sequence: who calls whom, in order. Something with a lifecycle (an
order, a booking, a payment) gets its states and what moves it between them. -->

### {{Name of the flow}}

```
{{Sequence, when the flow crosses parts:
Browser -> API: POST /bookings
API -> Database: reserve the slot
API -> Payments: charge
Payments --> API: paid}}
```

1. {{Step, when the flow is simple.}}

**States:** {{Only for something with a lifecycle: pending -> paid -> confirmed; pending -> expired after 15 minutes.}}

## When something fails

<!-- Only for what can fail halfway: a call to another service, a write in
two places, a job that runs later, two people changing the same thing at once.
Drop this section when nothing can. What the user sees is the person's choice:
ask it as a refinement question when they did not say it. Each row gets a row
in the test plan, which names its F-NN. -->

| Nº | What fails | What the system does | What the user sees | Comes from |
|---|---|---|---|---|
| F-01 | {{The payment service does not answer}} | {{Retries twice, 2 and 8 seconds apart, with the same key so nothing is charged twice; then releases the slot}} | {{"Payment failed, nothing was charged"}} | {{UC-02, NFR-03}} |
| F-02 | {{Two people book the same slot}} | {{The database accepts the first write; the second gets a conflict}} | {{"This time was just taken"}} | {{FR-07}} |

## Qualities

<!-- One row per non-functional requirement and per limit the person declared
that the architecture has to meet: response time, load, availability, how
long data is kept, how problems are noticed. Only those: drop the section
when there are none. Each row gets a row in the test plan, which names its
Q-NN. -->

| Nº | Quality | Target | How the architecture meets it | How it is checked | Comes from |
|---|---|---|---|---|---|
| Q-01 | {{Response time}} | {{The booking page answers in under 1 second on a telephone}} | {{Static pages served from the edge; one database query}} | {{An end-to-end test, or a measurement after launch}} | {{NFR-01}} |
| Q-02 | {{Noticing problems}} | {{An error reaches the person within an hour}} | {{Errors go to the error tracker, which emails them}} | {{By a person: a test error sent before launch, seen arriving}} | {{NFR-04}} |

## What it costs to run

<!-- Only when something in the architecture generates cost, or the person
declared a budget: drop this section otherwise. -->

| Service | Plan | Per month, at the expected use | Where the cost jumps |
|---|---|---|---|
| {{Hosting}} | {{Free}} | {{0}} | {{Above 100,000 requests a day, the paid plan}} |

**Expected use:** {{how many people, requests or stored items the numbers assume, and where that number comes from.}}

## Security and privacy

- {{Who can see and do what, where secrets live, how personal data is handled.}}

## Reorganisation: {{name}}

<!-- Only when the project is being reorganised inside: drop this section
otherwise. It covers the affected part and nothing else. In a project that had
no architecture document, this section may be the whole document. -->

### As it is

{{The affected part today: its pieces, what depends on what, and what makes it hard to change.}}

### As it will be

{{The same part after the change: what moves where, and what stays.}}

**Decision:** {{D-NNN, in the decisions record.}} **What must keep working:** {{the rows of the test plan, T-NNN to T-NNN.}}

## Checked against the requirements

{{One line: which requirements this architecture was checked against, and when.}}

| Requirement | What is missing | What was done |
|---|---|---|
| {{FR-09}} | {{No part sends the reminder}} | {{Added to the API as a scheduled job / brought as decision D-005 / left as open point 2}} |

<!-- When nothing is missing, keep the line and drop the table. -->

## Decisions behind it

- {{Number and title of each decision in the decisions record that shaped this architecture.}}

## Open points

| Nº | Point | Depends on |
|---|---|---|
| 1 | {{What is not settled}} | {{Who or what}} |
