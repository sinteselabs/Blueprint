# Design

<!-- Template. Write the document in the project's document language, headings
and labels included. Replace every {{placeholder}} and remove these comments.
This document exists when the project has screens. When the visual identity
is still to be decided, it records what was decided. When the person already
has one (a brand guide, a design file, a component library, tokens in the
code), it records where that lives and the rules a task must follow: fill
"What already exists" and keep, of the other sections, only what is not in
those sources. Never copy a source whole: point at it. -->

**Project:** {{PROJECT_NAME}} · **Version:** {{0.1}} · **Date:** {{YYYY-MM-DD}}

> **In short:** {{Up to five lines: how this should look and feel, and the one thing that must not be lost.}}

## What already exists

<!-- Only when the person already has a visual identity: drop this section
otherwise. One row per source. "Agent can read" says whether an agent working
in the repository can open it: a design file behind a login cannot, and what
a task needs from it is then written in the sections below. -->

| Source | Where it is | What it holds | Agent can read |
|---|---|---|---|
| {{Tokens}} | {{`src/styles/tokens.css`}} | {{Colours, type, spacing}} | {{Yes}} |
| {{Component library}} | {{A package name, or a folder}} | {{Buttons, fields, dialogs}} | {{Yes}} |
| {{Design file or brand guide}} | {{A link}} | {{Screens and logo}} | {{No: login needed}} |

**Rules for a task:** {{What must not be done: a colour or size written by hand instead of a token; a new component when the library has one. And who changes the sources.}}

## What it should feel like

- {{Three words at most, chosen by the person, and one line each on what they mean here.}}

## Colours

| Where it is used | Colour | Reads well on |
|---|---|---|
| {{Text, background, the main button, a warning}} | {{#RRGGBB}} | {{what it sits on}} |

Dark text on a light background, or the other way round, with enough contrast
to be read outdoors on a telephone: {{say which pair was checked, and how.}}

## Type

| Where | Font | Size |
|---|---|---|
| {{Titles, body, small print}} | {{name, and where it comes from}} | {{in pixels or points}} |

## Spacing and size

- {{The unit that repeats, the width of a column, how big a tappable thing is.}}

## What is reused

| Piece | Where it appears | What it looks like |
|---|---|---|
| {{Button, card, field}} | {{which screens}} | {{in one line}} |

## What was decided and what was not

- **Decided:** {{what is settled, and which decision in the record it is.}}
- **Not decided:** {{what is still open, and who it depends on.}}
