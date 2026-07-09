# Use Cases & User Flows

<!--
  How users interact with the system: actors, use cases (with diagrams), and the
  step-by-step workflows for the key journeys. First document of the modeling
  phase (Step 3a). Depends on the SRS. Local summary; link the source at the top.
  See workflows/project-kickoff.md → Step 3a for the interview questions.
-->

> **Primary source:** {{LINK to authoritative copy}}
>
> Always consult the source for the authoritative version. This file is a quick-reference summary.

**Project:** {{PROJECT_NAME}}
**Version:** {{0.1 — Draft}}
**Date:** {{YYYY-MM-DD}}
**Status:** {{Draft / Under review}}

---

## Actors

| Actor | Type | Description |
|---|---|---|
| {{name}} | {{human / external system}} | {{role and what they do}} |

---

## Use Cases

| UC | Actor | Goal | Related FR | Priority |
|---|---|---|---|---|
| UC-01 | {{actor}} | {{what they want to accomplish}} | {{FR-0X}} | MVP |
| UC-02 | {{actor}} | {{goal}} | {{FR-0X}} | Post-MVP |

---

## Use-Case Diagram

<!-- Keep diagrams as text (Mermaid / PlantUML) so they render and version cleanly. -->

```mermaid
flowchart LR
  actor([{{Actor}}])
  actor --> UC1([UC-01: {{goal}}])
  actor --> UC2([UC-02: {{goal}}])
```

---

## User Flows

<!-- One subsection per critical journey. Main path + the alternate/error paths. -->

### {{Flow name}} (UC-0X)

**Trigger:** {{what starts it}}
**Actor:** {{who}}
**Precondition:** {{state before}}

**Main path:**
1. {{step}}
2. {{step}}

**Alternate / error paths:**
- {{condition}} → {{what happens}}

**Postcondition:** {{state after success}}

---

## Open Questions

| # | Question | Owner | Status |
|---|---|---|---|
| 1 | {{unresolved flow question}} | {{who}} | Open |
