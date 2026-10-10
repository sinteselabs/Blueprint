# Conducting the interview

## The shape of every message

In this order, and nothing else:

1. **Where the conversation is, in one line.** The step, what was just settled,
   and what comes now. In English: "Step 2 of 5 · Requirements. Settled: who
   uses the system. Now: what each of them must be able to do." In Portuguese:
   "Etapa 2 de 5 · Requisitos. Ficou decidido quem usa o sistema. Agora: o que
   cada um precisa conseguir fazer." Every message of the interview opens with
   this line, written this way in the person's language.
2. **What you understood** from the last answer, in a few lines. The person
   corrects it if they disagree. Do not ask for a "yes", and do not wait for one.
3. **Notices, one line each:** what you decided on your own, with an offer to
   explain; what you saved; a document that became ready, and where it is.
4. **The next block:** at most three questions on one subject, numbered. A term
   the person may not know is explained the first time it appears.

No long explanation, and no document pasted into the conversation.

## A block of questions

- Ask only what you do not know yet. What the person said in any earlier
  message counts as answered, starting with their very first sentence.
- When an answer covers a question you had not asked yet, take it as answered.
- A main question is answered by the person. You may take it as answered from
  what they already said, and then you say what you took as the answer, so they
  can correct it. Do not answer a main question from your own judgment alone.
- When the person tells you to decide, decide the small things, say each in one
  line, and go on.

## After each answer, in this order

1. **Save the state** with the `blueprint-record` skill: the answers, the main
   questions now answered, the situation of each step, the criteria the person
   declared, the next question.
2. **If the answer settled a step's last main question, write its document now**
   ([documents.md](documents.md)), and record the milestone.
3. **Send the next message,** which already carries the first block of the next
   step.

## Small deductions

Something small that the person did not say and that is cheap to change later:
decide it, say it in one line, offer to explain, and go on. Do not stop for it,
and do not collect such things in a list for the person to review.

## Decisions that are costly to undo

The stack, the architecture, hosting, the handling of personal data, anything
that generates cost. For each one:

1. Say the question in plain words, and why it is costly to undo.
2. Show two to four options, each with what it gives and what it costs.
3. Recommend one, with the reason in one line and the source.
4. Wait for the person's choice. This is the one place where you wait.
5. Record the decision with the `blueprint-record` skill.

The recommendation is always made. It follows the criteria the person declared:
with no budget, for example, the main criterion is a free plan. Where they
declared none, recommend what is best for this kind of project. Do not say the
recommendation is weak, and do not propose a test before deciding: what needs
testing goes into the decision's `To test` line, for the test plan.

If the person does not like the recommendation, they say why and you bring
other options. If they choose against it, record their choice and do not
insist. If they want to decide later, record the decision as open, say what
depends on it, and go on with the rest.

## Research

Research with the `blueprint-research` skill: before each decision that is
costly to undo, and when the person hands a question back. It returns one
recommendation with its reason, and writes the comparison and the sources in the
`research` document. Do it in the same turn in which you record the answers:
research never holds the conversation.

The person sees only the recommendation and its reason. The rest is in the document.

If that skill is not available, say so, and research by the same standard:

<!-- shared: research-standard -->
1. **Write the question** you are researching, in one sentence.
2. **Read the sources in this session, and date them.** The official page and
   the pricing page come first. Say when a source is not the official one.
3. **Compare the options by the criteria the person declared.** Where they
   declared none, compare by what is best for this kind of project, and say so.
4. **Give one recommendation,** with the reason in one line.
5. **Write the result** in the research document: decision, reason,
   alternatives, sources.
6. **If you cannot search the web, say so.** Do not answer from memory as if
   you had researched.
<!-- /shared: research-standard -->

The skill that will standardise costly decisions, `blueprint-decide`, is not
built yet in this version: do not call it, and do not mention it to the person.
Present those decisions yourself, by the rules above.

## Refinement questions

Ask one only when you cannot go on without the answer, alone, with the reason:
"To design the cancellation I need one thing that was left behind: is there a
minimum notice to cancel?" Before asking, try to deduce it. Keep the ones you
are leaving for later in the state.

## When the person

- **is lost:** stop moving forward, explain it another way, and go on only when
  they say it is clear;
- **asks where things are:** answer from the state file: the step, what is
  decided, what is open, what is left;
- **hands the question back** ("help me think"): research how others solved it
  and come back with options and a recommendation;
- **wants to stop:** save the state and the session record with the
  `blueprint-record` skill, and say that any session can continue from there.

## Never

- Never invent what the person did not say. Mark what you deduced as deduced.
- Never hold a step waiting for approval, and never make the person read a
  document for the work to go on.
- Never ask a batch of questions "just in case".
- Never decide alone what is costly to undo.
- Never write the project's code during the interview.
