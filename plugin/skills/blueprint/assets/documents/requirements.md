# Requirements

<!-- Template. Write the document in the project's document language, headings
and labels included. Replace every {{placeholder}}, drop a section that does not
apply, and remove these comments. Every requirement can be tested and says where
it comes from. -->

**Project:** {{PROJECT_NAME}} · **Version:** {{0.1}} · **Date:** {{YYYY-MM-DD}}

> **In short:** {{Up to five lines: what the system must do, for whom, and the limits that shape it.}}

## What the system is

{{One paragraph: the product, who uses it and the main value.}}

## Functional requirements

What each kind of user must be able to do.

| Nº | Requirement | Priority | Comes from |
|---|---|---|---|
| FR-01 | {{One thing the system does, written so it can be tested}} | {{First version / Later}} | {{What the person said, or "deduced"}} |

## Who may do what

<!-- Only when there is more than one kind of user with different rights. -->

| Kind of user | May | May not | Requirement |
|---|---|---|---|
| {{Role}} | {{What only this role does or sees}} | {{What it must not do or see}} | {{FR-02}} |

## Non-functional requirements

How the system must behave: languages, accessibility, devices, speed,
availability, privacy. Each one has a number or a level, never "fast" or "easy".
An accessibility level gets a row in the test plan, which names its NFR.

| Nº | Requirement | Priority | Comes from |
|---|---|---|---|
| NFR-01 | {{One behaviour with its number or level: "the screens meet WCAG 2.2 AA", "the order is saved in under 2 seconds on a 4G telephone"}} | {{First version / Later}} | {{What the person said, or "deduced"}} |

## Limits

- {{What limits the project: budget, deadline, law, what the person already uses.}}

## Out of the first version

- {{What is explicitly not being built yet.}}

## How we will know it worked

{{The acceptance, in the person's words. A number when they gave one.}}

## Removed

<!-- Only once a requirement has left. Its row moves here from the tables above,
with the same id, which is never given to anything else: old commits, specs and
anchors in the code still name it. The two marks stay exactly as they are:
`blueprint map` does not count what is between them as something to build, and
says where the code still names it. -->

<!-- blueprint:removed -->
| Nº | Requirement | Removed by | Why |
|---|---|---|---|
| {{FR-07}} | {{What it said}} | {{The task that removed it: 03-02}} | {{One line}} |
<!-- /blueprint:removed -->

## Open points

| Nº | Point | Depends on |
|---|---|---|
| 1 | {{What is not settled}} | {{Who or what}} |
