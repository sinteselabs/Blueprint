# Test plan

<!-- Template. Write the document in the project's document language, headings
and labels included. Replace every {{placeholder}} and remove these comments.
One row per thing to verify, newest last. Rows are deduced from what is
written, never asked:
- each row of the architecture's Qualities (Q-01) and "When something fails" (F-01);
- each AI feature (AI-01): its "Good enough when" examples, and how many must pass;
- the accessibility level in the non-functional requirements (NFR-NN);
- what a decision left to verify (D-NNN), and in a refactor what must keep working.
Level is one of: unit, integration, end to end, measurement after launch, by a
person. Task is the plan's task whose spec implements the row, and lists it in
its Tests line: every row from the architecture or the AI features has one. A
row from a decision checked by a person outside any task has "-". Keep the
seven columns in this order: the project check finds Task by its place.
Nothing here is tested before a decision is taken: this is where what a
decision left open waits. -->

**Project:** {{PROJECT_NAME}} · **Version:** {{0.1}} · **Date:** {{YYYY-MM-DD}}

> **In short:** {{Up to five lines: what is left to verify, and how much of it is done.}}

## To verify

| # | What is checked | Level | Comes from | Task | How | Situation |
|---|---|---|---|---|---|---|
| T-{{NNN}} | {{The fact or the behaviour to confirm: "the booking page answers in under 1 second"}} | {{end to end}} | {{Q-01, or F-01, AI-01, NFR-NN, D-NNN}} | {{01-03, or "-"}} | {{What to open, run or measure.}} | {{to do, or done with the result.}} |
