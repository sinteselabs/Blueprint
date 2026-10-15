// `blueprint why`, `blueprint trace`, `blueprint map` and `blueprint budget`:
// the same engine the blueprint-explain skill carries, called from the CLI.
// There is one source for it, so the CLI and an agent that runs it by
// hand always get the same answer.

import { join } from "node:path";

import { PACKAGE } from "./files.js";

export const usage = `Usage: blueprint why <file[:line]> [folder] [--json]
       blueprint trace <ID> [folder] [--json]
       blueprint map [folder] [--json]
       blueprint budget [folder] [--base <ref>] [--json]

  why         what the code at that place is there for, the nearest anchor first
  trace       where one identifier lives: document, code, tests, tasks
  map         which of the documents' identifiers are anchored, and which are not
  budget      whether what is about to be handed over is reviewable in one sitting

  --json      the same answer, for an agent to read
  Exit code   0 answered, 1 nothing to answer with or over budget, 2 could not run`;

export async function explain(view, argv, folder, write) {
  const { main } = await import(`file:///${join(PACKAGE, "skills", "blueprint-explain", "explain.js").replace(/\\/g, "/")}`);
  return main([view, ...argv], folder, write);
}
