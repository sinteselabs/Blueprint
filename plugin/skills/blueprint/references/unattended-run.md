# An unattended run

An unattended run is a stretch of work, often overnight, in which one agent or
several take the plan's tasks one after another without stopping to ask the
person. It is the person who starts one, by asking for it. Everything the
person would have been asked is either settled before the run, taken and
written down for them to review, or left for them as a to-do.

When several agents run at once, the entry file's rules for more than one agent
apply as well: one worktree and one branch each, the work declared before it
starts, one branch integrated at a time.

## Before it starts: three questions

Say what you understood the run to be. Then ask what the person has not already
said, once, in one message:

1. **May it merge and deploy?** Merge into the main branch, and deploy what was
   merged. Without a yes to each, a finished task stops at a pushed branch, and
   the merge or the deploy is a to-do for the person.
2. **Which tasks?** Every task of the plan not done, a phase, or a list.
3. **When does it stop?** When those tasks are done, at a time, or at the first
   task that cannot be finished.

Save the answers as a criterion in the state, with the `blueprint-record`
skill, so every agent of the run and the next session read the same limits.
After this, ask nothing until the run ends.

## During the run

- **Tasks in the plan's order,** each one delivered as the entry file says: its
  spec, its tests, its "Done when". A task whose dependencies are not done waits.
- **A decision that is costly to undo** is not left waiting, and it is not taken
  silently. Prepare it as the `blueprint-decide` skill says, with research and a
  recommendation, take the recommended option, and record it as `provisional`:
  who took it, during which run, and how to reverse it. Go on from it.
- **A provisional decision stays inside the repository.** Nothing is bought, no
  account is created, no key is asked for, nothing is published outside the
  project, and no stored data is deleted or moved in place. Those wait for the
  person, as to-dos, and the tasks that need them wait too.
- **What only a person can do** becomes a to-do: what to do, why, and which task
  waits for it. Write it under `## Open points` in the state, then go on with a
  task that does not depend on it.
- **A task that cannot be finished,** because a test fails and the cause is not
  found, or the spec is not clear enough to decide: leave it on its branch,
  write what was tried, and take the next task that does not depend on it. A
  spec that would need the person to say what the system should do is a to-do,
  not a provisional decision.
- **A merged change you disagree with** is not overwritten: push the
  alternative on a branch, and leave the choice to the person as a to-do.

## The end: a summary

Each agent writes its summary in its session record, and the one who ends the
run gives the person one summary in reply, in this order:

1. **What was done:** the tasks finished, each with its branch or commit, and
   what was merged or deployed.
2. **What is provisional:** each decision taken in the person's absence, by its
   number, with the option taken and what reversing it would mean.
3. **What waits for the person:** the to-dos, each with what it blocks, and the
   tasks left unfinished, with why.

The state's `## Next question` becomes the first provisional decision to
confirm, or the first to-do when there is none.

## After the run

The person goes through the provisional decisions:

- **Confirmed:** its situation becomes `decided`, in the decisions record and
  in the state.
- **Reversed:** it is replaced, as "Replacing a decision" in the
  `blueprint-record` skill says: a new decision, what depends on the old one
  listed, and the change to the code made as a change to the project
  ([change.md](change.md)).
