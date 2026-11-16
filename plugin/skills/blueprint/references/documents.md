# Writing the documents

## Which documents a project has

Six are in every project: `system-description`, `requirements`, `research`,
`architecture`, `decisions`, `plan`. Which of the others a project gets follows
from its kind:

<!-- shared: documents-by-kind -->
| Document | In the project when |
|---|---|
| `use-cases` | People use the product through journeys, step by step |
| `data-model` | `stores-data` is `yes` |
| `data-classification` | `holds-personal-data` is `yes` |
| `wireframes` | `has-screens` is `yes` |
| `design` | `has-screens` is `yes` and the visual identity is still to be decided |
| `interface-contract` | `used-by-command-or-code` is `yes` |
| `ai-features` | `calls-a-model` is `yes` |
| `test-plan` | Something must be validated beyond acceptance, the project is a refactor, or a decision left something to test |
| `playbooks` | `developers` is more than 1 |
<!-- /shared: documents-by-kind -->

Templates are in `assets/documents/`, one per document: `system-description`,
`requirements`, `architecture`, `plan`, a task's spec, and the ones the kind of
project brings: `use-cases`, `data-model`, `data-classification`, `wireframes`,
`design`, `interface-contract`, `ai-features`.

Four documents are written by other skills, each with its own template: the
decisions record and the test plan by `blueprint-record`, the research document
by `blueprint-research`, and a playbook per role by `blueprint-setup`. If the
research skill is not available, write the research document yourself: one
section per question, with the decision, the reason, the alternatives and the
sources, and a last section for what was not verified.

## Where they go

In the documents folder, which the state names in `documents_at`: `docs/` for a
new project. One file per document, named after the document:
`system-description.md`, `requirements.md`, `research.md`, `architecture.md`,
`decisions.md`, `plan.md`. A task's spec goes in `specs/` inside that folder,
named with the phase and the task number: `01-01-task-name.md`.

Before creating a document, check that the project does not already have one
with the same purpose under another name or in another place. If it does, use
that one.

## How to write one

1. **In the document language,** headings and labels included. The templates
   are in English; translate them. File names, the names of documents in the
   state, and identifiers such as `FR-01` and `D-001` stay as they are.
2. **Start from the template.** Replace every `{{placeholder}}`, remove the
   template's comments, and drop a section that does not apply to this project.
   When the project already has the document, add to it in its own shape: do
   not rewrite it to fit the template.
3. **Open with the summary.** The "In short" block has five lines at most, so
   whoever opens the document knows what it says without reading the rest.
4. **Write only what is known.** What the person said, and what was decided and
   told to them. Mark what you deduced as deduced. Never fill a gap by inventing.
5. **Keep it short.** Tables and lists before prose.

## The identifiers are anchors

A document that numbers what it says — `FR-01`, `NFR-02`, `UC-03`, `D-004` —
gives the code something to point back at. That is what later lets anyone ask
why a line exists and be answered from the code, instead of being sent to read
this document.

<!-- shared: anchors-convention -->
An **anchor** is one of those identifiers written in the code: in a comment, or
in the name of a test. It says that this code exists because of that
requirement, that use case or that decision.

There is no index file to keep in step with anything. The anchor is the
identifier itself, so it works in any language and it cannot go stale on its
own:

    // FR-12: only the receptionist cancels an appointment.
    export function cancelAppointment(id, by) {

    def test_only_reception_cancels():  # FR-12

What carries an anchor, and what does not:

- A requirement that became code carries its id where that code begins: the
  function, the route, the component, the migration.
- A test that proves a requirement carries the id in its name or beside it.
- A decision that explains why the code is shaped the way it is carries its `D-`
  id at that spot, and only there. The reason stays in the decisions record.
- **Not every file has an anchor, and that is normal.** A file with no anchor is
  not a problem. An anchor naming an id that no document has is.
<!-- /shared: anchors-convention -->

So: number every requirement, every use case and every decision, and keep the
numbers stable. A renumbered requirement breaks every anchor that named it.

## When a document is ready

- Set it to `ready` in the state, with its path, through the `blueprint-record` skill.
- Tell the person in one line that it is ready and where it is. Reading it is
  their choice: do not ask for approval, and do not wait.
- If the person disagrees with something in it, change that part only and say
  what changed.
- When a later answer changes what a document says, update the document.
