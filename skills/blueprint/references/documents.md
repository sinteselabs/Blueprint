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

Templates for the system description, the requirements, the architecture, the
plan and a task's spec are in `assets/documents/`. Three documents are written
by other skills, each with its own template: the decisions record and the test
plan by `blueprint-record`, and the research document by `blueprint-research`. If the
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

## When a document is ready

- Set it to `ready` in the state, with its path, through the `blueprint-record` skill.
- Tell the person in one line that it is ready and where it is. Reading it is
  their choice: do not ask for approval, and do not wait.
- If the person disagrees with something in it, change that part only and say
  what changed.
- When a later answer changes what a document says, update the document.
