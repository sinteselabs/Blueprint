# Interface contract

<!-- Template. Write the document in the project's document language, headings
and labels included. Replace every {{placeholder}} and remove these comments.
This document exists when the product is used by command or by code: a command
line, a library, an endpoint, a plugin, a skill. It says what is offered, what
comes back, and what breaking it would cost. Names of commands, options, fields
and codes are written exactly as they are, in their own language. -->

**Project:** {{PROJECT_NAME}} · **Version:** {{0.1}} · **Date:** {{YYYY-MM-DD}}

> **In short:** {{Up to five lines: what this offers to whoever calls it, and the promise that must not break.}}

## Who calls it

| Who | How they call it | What they expect |
|---|---|---|
| {{A person at a terminal, another program, an agent}} | {{command, call, request}} | {{in one line}} |

## What is offered

| What | What it does | What it needs | What comes back |
|---|---|---|---|
| {{`name`}} | {{in one line}} | {{arguments or fields, and which are required}} | {{what the caller gets}} |

## {{`name` of the command or the call}}

```
{{How it is called, exactly, with one example that works.}}
```

| Input | What it is | Required | Default |
|---|---|---|---|
| {{`name`}} | {{what it holds}} | {{yes or no}} | {{value, or "-"}} |

**Comes back:** {{the shape of the answer, with one example.}}
**When it fails:** {{what the caller gets, and how they tell one failure from another: a code, a name.}}

## What never changes without warning

- {{The names, the shapes and the codes that others rely on. Changing one of these is a decision that is costly to undo.}}

## What is left out

- {{What this does not offer, and what to use instead.}}
