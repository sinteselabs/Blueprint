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

### {{Name of the flow}}

1. {{Step.}}

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

## Decisions behind it

- {{Number and title of each decision in the decisions record that shaped this architecture.}}

## Open points

| Nº | Point | Depends on |
|---|---|---|
| 1 | {{What is not settled}} | {{Who or what}} |
