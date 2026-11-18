# Data model

<!-- Template. Write the document in the project's document language, headings
and labels included. Replace every {{placeholder}} and remove these comments.
One section per thing the system stores. Write only what the project needs: a
field nobody asked for is a field to maintain. -->

**Project:** {{PROJECT_NAME}} · **Version:** {{0.1}} · **Date:** {{YYYY-MM-DD}}

> **In short:** {{Up to five lines: what the system stores, and the one rule that must never break.}}

## What is stored

| What | What it holds | How many, roughly |
|---|---|---|
| {{Name}} | {{In one line}} | {{a few, thousands, one per order}} |

## How they relate

```
{{A plain-text diagram: each thing, and which belongs to which.}}
```

## {{Name of the thing stored}}

| Field | What it is | Required | Rule |
|---|---|---|---|
| {{field}} | {{what it holds, and in what unit}} | {{yes or no}} | {{what makes it valid, or "-"}} |

**Situations,** when it has them: {{the situations it passes through, and what moves it from one to the next.}}
**When one is deleted:** {{it is removed, it is hidden, or it cannot be deleted because something points at it. And how long it is kept, when not forever.}}
**Personal data:** {{which fields, or "none". The detail is in the data classification.}}

## Rules that hold across them

- {{Something that must always be true: what is unique, what cannot be deleted while something else points at it, what is counted where.}}

## Data that already exists

<!-- Only when something has to come in from before the system. -->

| Where it is today | What comes in | Once or continuously | Who checks it came in right |
|---|---|---|---|
| {{a spreadsheet, the old system}} | {{which things, roughly how many}} | {{once, at launch / every night}} | {{who, and how}} |

## What is not stored

- {{Something the project deliberately does not keep, and why.}}
