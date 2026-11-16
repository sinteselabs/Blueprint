---
name: blueprint-research
description: Standard research process for a project decision. Use when something needs researching before deciding, such as similar tools, a tech stack, hosting, pricing or known limits, or when the user asks for help thinking through a choice. Reads dated sources, compares the options against the criteria the user declared, and returns one recommendation with a one-line reason.
---

# Blueprint: research

One way to research, whatever the question: a stack, a hosting service, a price,
a limit, how others solved a problem. It works inside the Blueprint interview
and on its own, in any folder.

Research informs a choice. It does not make it: a decision that is costly to
undo belongs to the person.

## How to talk

- Answer in the person's language, in plain words.
- The person sees the recommendation and its reason. The comparison and the
  sources go into the research document.
- Say what you read and what you could not read. Nothing happens in silence.

## The standard

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

The sections below say how to do each one.

## 1. The question

One sentence whose answer is a choice: "Where can the site and its database be
hosted at no cost?" A request that holds several choices becomes several
questions, researched one at a time.

If you cannot tell what is being chosen, ask the person that, and only that,
before you research.

## 2. The criteria

Look for them in this order, and stop at the first that has any:

1. **The project's state.** If this folder has `.blueprint/state.md`, read the
   sections `Criteria the person declared` and `Project kind`.
2. **This conversation.** What the person said they need, cannot spend or
   cannot accept.
3. **The kind of project.** With no criterion declared, compare by what suits a
   project like this one, and tell the person in one line which criteria you
   used: "You declared no criterion, so I compared by what suits a small site
   kept by one person: cost first, then how little there is to maintain."

Do not stop to ask for criteria. When the person declares one while asking and
there is a Blueprint project, save it in the state with the `blueprint-record`
skill.

## 3. The sources

- Use whatever the coding agent has for searching the web and reading pages.
- Open the page and read it. A line in a list of search results is not a reading.
- The official documentation and the official pricing page come first. A blog
  post, a forum answer, a comparison site or a listing is a third-party source,
  and you say so beside it.
- Write each source with its address and the date you read it. Take the date
  from the system, not from memory.
- A source read on another day is read again before a new recommendation
  depends on it. Prices, limits and product names change.
- Compare two to four options. Where there are more, keep the ones that meet
  the criteria.
- Stop when the criteria single out one option, or when reading more would not
  change the recommendation.

## 4. The recommendation

Always one, with the reason in one line. The reason names the criterion that
decided it: "Cloudflare: the site and the database fit in one free plan that
does not pause."

When the research does not single out one option, recommend the one that best
meets the criteria, in the order the person gave them. Report facts, not doubts
about your own advice:

- Say what you could not read or confirm: "I could not open the pricing page."
- Do not say the recommendation is weak or uncertain.
- Do not propose a test before the person decides. What is left to verify goes
  under `Not verified` in the research document, for the test plan.

## 5. The record

**Inside a Blueprint project,** the result goes into the research document:
`research.md` in the folder the state names in `documents_at`, which is `docs/`
when the state does not say.

1. If the file does not exist, create it from [assets/research.md](assets/research.md),
   in the project's document language, headings and labels included. Replace
   every `{{placeholder}}` and remove the template's comments.
2. Add one section for the question, after the ones already there. Fill
   `Decision`, `Reason`, `Alternatives` and `Sources`. While the person has not
   chosen, `Decision` says what you recommend and that the choice is open.
3. Update the summary at the top and the `Not verified` section.
4. Set the document `research` to `ready` in the state, with its place, through
   the `blueprint-record` skill. It is `ready` whenever every question
   researched so far is in it.

**Outside a Blueprint project,** create no file. Give the result in the
conversation: the recommendation and its reason first, then the alternatives in
one line each, then the sources with their dates. Offer to save it where the
person says.

## 6. Without the web

When there is no tool to search or read pages, or the coding agent refuses it:

1. Say so before the recommendation: "I could not read the pages in this
   session." If a tool was refused, do not insist and do not go around it.
2. Recommend all the same, from what you know, by the same criteria.
3. Mark it. In the document, `Sources` says that none was read in this session
   and lists the pages to check. A number given from memory, such as a price or
   a quota, says "from memory" beside it.
4. Put what must be checked under `Not verified`.

## What you give back

In the conversation, and nothing more:

- the recommendation, with its reason in one line;
- what you could not read or confirm, in one line, when there is something;
- where the detail is.

When the choice is costly to undo, say that it is the person's, and ask. When
the `blueprint` skill called you during the interview, the shape of its
messages applies, and it presents the choice to the person.

## Never

- Never decide in the person's place what is costly to undo.
- Never recommend without a reason, and never give as the reason something
  that is not one of the criteria you used.
- Never present as a finding what the research did not find.
- Never answer from memory without saying so.
- Never say the recommendation is weak, and never propose a test before deciding.
- Never paste the whole comparison into the conversation when the project has a
  research document.
- Never create a file outside a Blueprint project without being asked.
