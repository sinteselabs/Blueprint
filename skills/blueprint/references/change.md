# Improving and refactoring a project

The project already exists. Three rules hold from the first message to the last:

- **Read before you ask.** The code and the documents answer most questions.
  Ask only what they do not.
- **Write only what the change needs.** A project is not documented again
  because one thing in it changes.
- **Touch nothing in silence.** Before you change a file that already exists,
  say which file and which part. After, say in one line what changed.

## Which of the two

| | What changes | In the state |
|---|---|---|
| **Improving** | What the system does: something is added, changed or removed | `starting_point: improve` |
| **Refactoring** | How it is built inside. What it does stays the same | `starting_point: refactor` |

When the request already says which one it is, take it and say what you took.
Ask only when it does not. A request that holds both is two changes: the
reorganisation first, then the addition, and you say so.

Asking to document what exists belongs with refactoring:
[The whole picture](#the-whole-picture).

## 1. Read

Use the `blueprint-survey` skill, with the change the person named. It reads
and changes nothing, and gives back what the project is, each document in one
of three states, the size of the change, what it did not read and the questions
the files do not answer.

If that skill is not available, say so, and read in the same order: the README
and the manifest, the documents, then the files the change touches. Check each
document against the code before you say that it matches.

If the person has not said what they want to change, read the project all the
same, and ask that in the message below.

## 2. The first message

One message. Nothing is written before the person answers it. The person
knows their project: say only what shows that you read it and what they must
decide, one line for each thing. The detail is in the files.

**For a small change, under ten lines:**

1. **What you concluded,** in one line: that the change is small, and why.
2. **The task:** what it does, what it does not, when it is done. One line each.
3. **Where the spec will be written,** in one line.
4. **What the files do not answer,** two questions at most, and then the one
   that lets you write: "May I write the spec?"

**For any other change, about fifteen lines:**

1. **What you concluded,** in one line: improving or refactoring, and why the
   change is not small.
2. **What the project is,** in one line, said as read from the code.
3. **The documents:** one line for each that exists, saying that it matches
   the code, or that it is outdated and in what; then one line naming the ones
   that do not exist.
4. **What you propose to write,** one line each: the files you will create, and
   the existing files you will change, with the part.
5. **What you did not read,** in one line, only when something was left out.
6. **What the files do not answer,** three questions at most, and then the one
   that lets you write: "May I write this?"

For example, in Portuguese, the whole message:

> **Melhoria · li o projeto, e nada foi escrito.** Não é pequena: traz o
> primeiro dado pessoal do projeto, o telefone do paciente.
> O projeto, lido do código: um site em Django que mostra a agenda da clínica.
> - `README.md`: bate com o código.
> - `docs/acesso.md`: desatualizado. Diz que a entrada é por senha (o código
>   manda um link por e-mail) e que há três perfis (o código tem dois).
> - Não existem: requisitos, decisões, plano, plano de testes.
>
> Proponho:
> - criar `docs/plan.md`, com o que entra, o que muda e o que sai, e uma spec
>   por tarefa em `docs/specs/`;
> - criar `.blueprint/state.md`, para qualquer sessão continuar daqui;
> - em `docs/acesso.md`, corrigir só a parte dos perfis, que a mudança toca. A
>   da senha fica anotada.
>
> 1. Quem pode ver o telefone: só a recepção, ou o médico também?
> 2. Posso escrever isso?

Keep it to that. What you took as given and the small things you decided are
said after the go-ahead, with what you wrote: not in this message.

This is one of the two places where you wait: you are about to write in a
project that is not yours. The other is a decision that is costly to undo.

## 3. A small change

It becomes one task with its spec, and nothing else: no state file where there
is none, and no document.

With the person's go-ahead:

1. Write the spec from `assets/documents/task-spec.md`, in the project's
   document language, in `specs/` inside the folder where the project keeps its
   documents; `docs/specs/` when it keeps none.
2. If the project has a plan or a task list, add the task to it, in one line,
   and say that you did.
3. If the project has a Blueprint state, save it with the `blueprint-record`
   skill, so `## Next question` names the task.
4. Say where the spec is, and that the task starts when the person says so.
   Doing it is ordinary work, outside this interview.

## 4. Any other change

### The state

After the person's go-ahead, create the state with the `blueprint-record`
skill. Take from the files what they tell, and say each thing you took in one
line, so the person corrects it:

- `document_language`: the language the project's documents are in; the
  person's language when it has none;
- `developers`: how many people write in the history; `1` when it does not tell;
- `documents_at` and `tasks_at`: where the project already keeps its documents
  and its tasks; `docs/` and `docs/plan.md` when it keeps none;
- the five facts of the kind of project, as `deduced`;
- each document: `ready` with its place when it matches the code,
  `in-progress` with its place when it is outdated, `not-started` when it does
  not exist. What is outdated goes under `## Open points`, one line per
  difference.

A project that already has a Blueprint state keeps it. Add the main questions
of this change to the steps it touches, which open again, and keep everything
that is answered.

### The steps, for a change

The five steps are the same. Each one asks only about the change:

| Step | Improving | Refactoring | What it writes |
|---|---|---|---|
| 1 `system-description` | What changes, and why | What is reorganised, and why | Nothing |
| 2 `requirements` | The difference: what enters, what changes and what leaves | What must keep working | Improving: the difference, in the plan. Refactoring: the test plan |
| 3 `modeling` | Only when the change brings a new fact about the project: the main questions that fact brings | Nothing | As in a new project |
| 4 `architecture` | One question for each decision that is costly to undo. Nothing when the change brings none | How the affected part will be | The decisions. Refactoring: the affected part as it is and as it will be, in the architecture |
| 5 `plan` | What comes first | What comes first | The tasks, one spec each |

- A step the change does not touch stays `not-started`, with `0 of 0` main
  questions. Say once which steps those are.
- A step is `closed` when what it writes is written. Step 1 writes nothing: it
  closes with its answer.
- Take as answered what the request and the code already say, and say what you
  took. For the difference, write your reading of it and let the person correct.
- Everything else goes as in a new project: [conduct.md](conduct.md) for the
  shape of every message and what to do after each answer,
  [steps.md](steps.md) for the main questions a new fact brings,
  [documents.md](documents.md) for how a document is written.

### What is written, and what is left alone

| The document | What you do |
|---|---|
| Matches the code | Leave it. When the change is delivered, update only the parts the change affected |
| Outdated | Correct only the part the change touches, and say which. Tell the person the other differences, and keep them in the state. Do not correct them unless asked |
| Does not exist | Do not write it whole. Create only what this path writes: the plan with its specs, the decisions record when there is a decision, and for a refactor the test plan and the affected part of the architecture |

When the change brings a new fact, such as the first personal data or the
first screen, the document that fact brings enters the project: list it in the
state ([documents.md](documents.md) has the table). The modeling documents are
not written yet in this version of Blueprint ([steps.md](steps.md)): keep the
answers in the state, and do not propose to write them.

The file an agent reads first (`AGENTS.md`) is prepared by the
`blueprint-setup` skill, which is not built yet in this version of Blueprint.
Say so when the project has none.

## Improving: the difference

Write the change as a difference from what exists, in the plan, under
`## What changes`:

- **Enters:** what will exist that does not exist today.
- **Changes:** what exists and will behave differently, and how.
- **Leaves:** what stops existing. "Nothing" when nothing does.

Each line names what it touches: the requirement, when the project has
requirements, or the file. If the project has a plan, add the change to it.
Never start a second plan.

## Refactoring: nothing may break

- **The requirements are not rewritten.** They are the list of what must keep
  working. Where the project has none, list from the code what the affected
  part does today.
- **What must keep working goes into the test plan,** one row per behaviour,
  with the `blueprint-record` skill. `Comes from` names the requirement, or
  says that it is how the code behaves today. `How` names the test that already
  covers it, or the steps to check it by hand.
- **A behaviour that no test covers** is said to the person, and the first task
  of the plan writes that test, before any code moves.
- **The affected part as it is and as it will be** goes into the architecture
  document, under a heading with the name of the reorganisation. Only that
  part: the rest of the architecture is not written.
- **How it will be is a decision that is costly to undo.** Bring it with the
  `blueprint-decide` skill, with the recommendation first, even when the
  person named the parts or told you to decide the details. Write the test
  plan while you wait: it does not depend on the answer.
- **Each task leaves the project working.** Its spec says which rows of the
  test plan must pass.

## The whole picture

Written only when the person asks for it: "document this project".

1. Say how much there is to read before you start, when the repository is large.
2. Read all of it with the `blueprint-survey` skill.
3. Write the documents of the project's kind one at a time, from the code,
   each from its template. The summary of each says that it was written from
   the code, and when.
4. What the code does not tell is not invented. Ask it, three questions at a
   time, or leave it as an open point of the document.
5. After each document, tell the person in one line where it is.

## When the change is delivered

When the tasks of the change are done:

1. Update the parts the change affected in the documents that already existed,
   and say each one.
2. Write the result in each row of the test plan.
3. Record the milestone with the `blueprint-record` skill.

## Never

- Never ask what the code or the documents answer.
- Never rewrite a document because it is outdated. Correct the part the change
  touches, and report the rest.
- Never write a whole document that the change does not need.
- Never change what the system does in a refactor. If the reorganisation asks
  for it, stop and say so: that is another change.
- Never write the project's code during the interview.
