---
name: blueprint-decide
description: Handles a project decision that is costly to undo, such as the stack, the architecture, hosting, the handling of personal data, or anything that generates cost. Use when such a decision comes up. Presents the question in plain words with two to four options and a recommendation, waits for the user's choice, and records the decision with its reason.
---

# Blueprint: decide

A decision that is costly to undo belongs to the person. This skill is the one
way to bring it to them: the question in plain words, a recommendation, a few
options, and the choice recorded where the next session will find it. It works
inside the Blueprint interview and on its own.

## What is costly to undo

The stack, the architecture, hosting, the handling of personal data, anything
that generates cost. And anything else where changing later means rewriting
what was built, moving data that is already stored, or breaking what others
rely on.

A small thing that is cheap to change later is not for this skill. Decide it,
say it in one line, and go on.

## Before you present

1. **The options come from research.** If the project's research document has
   no section for this question, research it first with the
   `blueprint-research` skill.
2. **The criteria are the person's.** Read `Criteria the person declared` in
   `.blueprint/state.md`, then what they said in this conversation. Where they
   declared none, use what is best for this kind of project, and say so.

## The shape of a decision

<!-- shared: decision-shape -->
1. **The question in plain words,** with why it is costly to undo, in one line.
2. **The recommendation first,** with the reason in one line: the criterion
   that decided it.
3. **The other options, one line each:** what it gives and what it costs. Two
   to four options in all, the recommended one included.
4. **Wait for the person's choice.** This is the one place where you wait.
5. **Record the decision** with the `blueprint-record` skill, whatever the
   choice, including "later".
<!-- /shared: decision-shape -->

For example, in Portuguese:

> **1. Onde o site fica hospedado, junto com o banco de dados.** Trocar depois
> é mover o site e as encomendas já guardadas.
> Recomendo a **Cloudflare**: site e banco cabem num plano gratuito que não pausa.
> - **Supabase:** banco mais completo, mas o plano gratuito pausa depois de uma
>   semana sem uso.
> - **Firebase:** também não pausa, mas o código de servidor exige o plano pago.

Keep it to that. The comparison, the numbers and the sources are in the research
document: say where it is, in one line, and do not paste it.

A term the person may not know is explained the first time it appears, in half
a line.

## More than one decision at a time

- Put them in one message, **three at most**, numbered. If more are due, the
  first three now and the others in the next message.
- The decision that others depend on comes first. Present the dependent ones as
  they follow from your recommendation, and say so: "If you choose another
  option in 1, I will bring new options for 2."
- End with one question that covers them: which option in each.

## When the person is not technical

You know it from the state, or from their words. Then:

- say what each option means for them, not how it works inside;
- tell them plainly that they can take the recommendations: "You can answer
  'I take your recommendations', or name the ones you want to see in detail."

Taking the recommendations is their choice, and it is recorded as theirs.

## After the answer

| The person | What you do |
|---|---|
| chooses an option | Record it as `decided`. Say in one line what was recorded and where |
| chooses against the recommendation | Record their choice, with their reason. Do not insist and do not ask whether they are sure. If their choice changes a decision that depends on it, bring new options for that one |
| says "you decide", or takes the recommendations | Record the recommended option, decided by the person accepting the recommendation |
| likes none of the options | Ask what is missing, take the answer as a criterion, research again, and bring other options |
| wants to decide later | Record the decision as `open`, with what depends on it. Tell them what waits for it, and go on with everything that does not |
| accepts in advance every decision of a kind, on a condition | Save the condition as a criterion in the state. From then on, tell them each such decision in one line as you take it. If the condition does not hold, bring the decision back to them |

Recording is done by the `blueprint-record` skill: the decision, the reason,
the alternatives, who decided, the date, the sources and the situation. If it is
not available, say so, and write the entry yourself in the project's decisions
record, with those same parts.

Outside a Blueprint project, create no file: give the decision back in the
conversation, with those parts, and offer to save it where the person says.

## What is left to verify

A decision is often taken with something still unconfirmed: a limit read from
memory, a page that could not be opened, a behaviour that only shows when the
thing runs. That is not a reason to hold the decision.

- Say the fact in one line: what was not confirmed.
- Put it in the decision's `To test` line when you record it. The record skill
  turns it into an item of the project's test plan.
- If a later test shows that the decision does not hold, it comes back to the
  person as a new decision.

## Never

- Never decide in the person's place what is costly to undo.
- Never say the recommendation is weak, and never recommend without a reason.
- Never propose a test before deciding, and never make a test a condition for
  deciding.
- Never hold the rest of the work for a decision the person left for later.
- Never insist after the person chose.
- Never rewrite a decision that is recorded. A change is a new decision that
  replaces the old one.
