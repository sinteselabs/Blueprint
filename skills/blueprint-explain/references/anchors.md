# Anchors: the identifier lives in the code

The documents of a Blueprint project number what they say: `FR-01` for a
functional requirement, `NFR-02` for a non-functional one, `UC-03` for a use
case, `D-004` for a decision, `ARD-05` for an architecture decision. Those
numbers are what turn a pile of documents into a map.

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

## Why there is no index

An index would be a second thing to maintain, and the first thing to rot. The
whole point of this layer is that the developer does not have to trust a
document to be current. A grep over the code is always current.

## What reads them

- `explain.js why <file:line>` answers "why is this the way it is" from the
  anchors of that file.
- `explain.js trace <ID>` answers "where does this live" from the id.
- `explain.js map` says which requirements are anchored and which are not.
- The project check reports an anchor that names an id no document has, and a
  task whose "done when" list is complete while its requirement is anchored
  nowhere.

## Writing one when you deliver

When a task's code is written, the id of what it serves goes in the code, at the
place where the behaviour begins — one line, in the language of the project's
documents. The task's spec already says which ids the task comes from: those are
the ones the code carries.

Never scatter the same id over a dozen places to look thorough. One anchor where
the behaviour begins, plus the test, is what makes `why` answer in one line.
