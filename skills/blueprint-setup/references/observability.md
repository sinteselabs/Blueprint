# Observability: the journal, and Langfuse

This page has two readers.

**You, the agent:** so you know when to offer a tool, when not to, and what to
say. Observability is never obligatory, and you never leave it unanswered
either: every project gets one of the two ways below.

**The person:** most people have never heard of Langfuse, so they cannot answer
"do you want it?" Read them the part they need, in their language, or point them
at this file. Never make them read the whole page: one or two lines, and the
offer.

## Why record anything

When a person writes the code, what happened is in the commits. When agents
write it, most of what happened never reaches a commit: what was asked, the
paths tried and dropped, every file read, every command run, the tokens spent.
The commit is the result; the work is gone.

That missing record is what costs later:

- **"Why did it do that?"** Three weeks on, a strange piece of code has no
  reason attached. The session that produced it is the reason.
- **"Where did the money go?"** One long session can cost more than a whole
  week of short ones, and nothing says which.
- **"Did that change help?"** You reword an instruction, or move to another
  model, and have nothing to compare against.
- **"What did the other person's agent do?"** With a team, each agent's work is
  invisible to everyone else.

So the rule: what each agent session did is recorded, and the cost too when the
tool measures it.

## The two ways

| | The project journal | Langfuse |
|---|---|---|
| What it is | Markdown files inside the project, written by the agent | A service that stores a trace per session, in the browser |
| Needs installing | Nothing | An account or a server, a key pair, and one setup per machine |
| What it records | What was asked, done, decided and left open, in the agent's words | Every turn, every model call, every tool call, with tokens, cost and timing |
| Cost | Measured by nobody | Measured per turn |
| Goes to git | Yes, with the project | No: it lives in the service |
| Honest about | Being a summary the agent chose to write | Carrying the prompts and outputs as they are |

They are not rivals. The journal always works, and it is what Blueprint writes
by default. Langfuse is added when the project earns it.

## What Langfuse is, in one paragraph

An open-source platform for watching what LLM-based software does. Something in
the path sends it a *trace*: one record of a session, with each model call and
each tool call under it, carrying the input, the output, the tokens and the
cost. In the browser you then search sessions, open one turn, see what the model
was actually given, and compare costs over time. It runs as a hosted service or
on a server of your own.

## It only reaches AI you run by command or by API

This is the first thing to check, and it rules Langfuse out more often than
anything else. A trace only exists if something in the path can send it.

- **It reaches:** coding agents in the terminal (Claude Code, Codex,
  Antigravity CLI) and your own code calling a model through an API.
- **It does not reach:** a chat in a browser, an assistant panel in an editor
  with no telemetry of its own, a desktop app.

So ask, in one line, how the person works with AI. If the answer is a web chat
or an editor panel, say plainly that Langfuse would record nothing of it, and
that the journal is the honest answer. Do not offer a tool that cannot see the
work.

## When to offer it

Offer when at least one of these is true:

- **More than one person develops.** Each person's agent is invisible to the
  others, and the journal only carries what each agent chose to write down.
- **Cost matters.** There is a budget, or the person has been surprised by a
  bill.
- **The product itself calls a model.** Then the same instrument that watches
  the development also watches the product in use, which is the harder half.
- **The project is long.** Many sessions over many weeks, and "why did it do
  that" will be asked.
- **The person already uses it.** Then it is not a new tool, it is a key pair.

## When not to

- **A short project, one person, a few sessions.** The journal is enough and
  costs nothing to set up.
- **The person does not run AI by command or by API** (above).
- **No appetite for another account,** or work that happens offline. A hosted
  service that cannot be reached buffers and then drops.
- **The data cannot leave the machine** and nobody will run a server. Say that
  self-hosting is the way out, and that without it the journal is the answer.

Say which of these applies, in one line, and move on. A person who hears
*"not worth it here, because the project is a weekend and you work alone"*
learns something; a person who hears nothing just loses the option.

## Hosted or on your own server

| | Hosted | Your own server |
|---|---|---|
| Setting up | An account and a key pair, minutes | Docker on a machine you keep running |
| Where the data sits | On their servers, in the region you choose: Europe, United States, Japan, or the one for health data | On your machine |
| Cost | A free tier, then by volume | The machine, and your time |
| Good for | Almost everyone, to start | A rule that says the data stays in-house |

Recommend hosted unless there is a rule about where the data may sit. Moving
later means pointing the setup at another address.

**Say this out loud, once:** the traces carry the prompts and the outputs as
they are, with no masking. Anything that must not reach that service must not
be pasted into an agent session.

## One Langfuse project per software project

A key pair in Langfuse belongs to a project, not to a person, and Langfuse's
own guidance is to put several projects under one organisation and keep a
separate project, with its own keys, for each environment — production,
staging, development (read 11/10/2026). The same reasoning gives one Langfuse
project per software project: traces from two of them do not mix, the cost of
each is readable on its own, and a key that leaks reaches one project only.

So say it as a step, not as a detail: **create a project in Langfuse for this
one, and use its key pair here.** A key shared between two projects is the
mistake this avoids.

The person does that part. **Never ask for a key in the conversation, and never
write a key in a file of the project.** You say what to create and where the
key goes; they paste it where only their machine can read it.

## How it is wired

**Blueprint ships no script for this, on purpose.** Langfuse distributes the
Claude Code integration itself, as a plugin, and keeps it working. A copy of it
inside Blueprint would be a second thing to keep in step, and would ask the
person to trust us for something its own author maintains. So what Blueprint
carries is this page: when it is worth it, and what to do.

For Claude Code, what the person does once:

```
claude plugin marketplace add langfuse/claude-observability-plugin
claude plugin install langfuse-observability@langfuse-observability
```

It needs Python 3.9 or newer and the Langfuse SDK
(`pip install "langfuse>=4,<5"`). On enabling, it asks for the public key, the
secret key and the address of the Langfuse that is being used; the secret goes
to the machine's keychain. Then every session in a project that has tracing
switched on is recorded, and nobody touches it again.

**The other agents.** Codex and the Antigravity CLI both have hooks of their
own now, so the same thing is possible there, but the official plugin is for
Claude Code only (read 11/10/2026). Say that plainly: with those agents,
observability by Langfuse is something the person wires by hand, and the
journal is what Blueprint writes.

## It has to say when it stops

A recorder that quietly stops is worse than none: the person believes there is a
record and there is not. The integration never blocks a session, and it does say
in the session itself when it is switched on and cannot record — the SDK
missing, a key missing, the service refusing the data.

That is what makes it a thing you set up once and forget: silence means it is
recording.

When you report on it, **never say it is connected because the state names it.**
Either you saw a trace arrive, or you say that you could not check.

## What you do with all this

1. **Offer once,** in one line, with the reason it fits this project, when one
   of the conditions above is true. If the person says no, or says nothing, the
   journal is the answer and the subject is closed.
2. **Offer the explanation, do not impose it.** "Want me to say in three lines
   what it is and what it would cost you?" is enough.
3. **Write the choice in the state** through the `blueprint-record` skill:
   `observability` holds `journal` or the name of the tool.
4. **The journal is written either way.** With Langfuse connected it is still
   where the decisions and the open points live, in the project, in git.
