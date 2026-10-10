// `blueprint check`: the same script the skill carries, called from the CLI.
// There is one source for the check (ARD-05), so the CLI and an agent that runs
// it by hand always get the same answer.

import { join } from "node:path";

import { PACKAGE } from "./files.js";

export const usage = `Usage: blueprint check [folder] [--json]

  Says whether the project is whole, and how to fix what is not. It only reads.

  --json      the same result, for an agent to read
  Exit code   0 nothing wrong, 1 something to fix, 2 could not run`;

export async function check(argv, folder, write) {
  const { main } = await import(`file:///${join(PACKAGE, "skills", "blueprint-status", "check.js").replace(/\\/g, "/")}`);
  return main(argv, folder, write);
}
