<!-- Template for the review brief, which is what an agent hands over when it
finishes a task. Write it in the project's document language, headings and
labels included. Replace every {{placeholder}}, drop a line that does not apply,
and remove these comments. Seven fields, no more: a brief longer than the diff is
the problem it was meant to solve.

Where it goes: said whole in the conversation, and written into the task's own
spec — the first six fields under "Result of the delivery", and the seventh in
the "How to test" section the spec already has. It never gets a file of its own. -->

## Result of the delivery · {{task number and name}}

**What changed:** {{The files, grouped by what they do, not listed one by one. Numbers: how many files, how many lines.}}

**Which requirement it serves:** {{FR-01, FR-02. The ids the code now carries as anchors.}}

**Which decision it depended on:** {{D-004, and in one line what it settled. "None" when nothing was decided.}}

**What I assumed:** {{Every gap filled without asking. "Nothing" when there was none — and say it, because silence here reads as nothing to check.}}

**What I could not verify:** {{What was not run, not tested, or tested only in part, and why. Never left empty to look finished.}}

**Where to look first:** {{Two or three places, hardest first. Each one: the file and line, and what makes it risky.}}

**How to test:** {{What to run or to open, and what should be seen. The exact command.}}

<!-- How to order "Where to look first". Risk is not size. Hardest first, by
this order:
1. What touches money, personal data, permissions or anything that deletes.
2. What has no test covering it, and the brief says so above.
3. What I assumed instead of asking.
4. What changed shape rather than gaining a line: a signature, a schema, a
   contract between parts.
5. What is merely long. Length is last: a 300-line file of one more of the same
   is cheaper to review than six lines that change a rule. -->
