#!/usr/bin/env node
// The Blueprint CLI. It does only what does not need a model and always gives
// the same answer: install, check, update. What takes judgment is in the skills.

import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { check, usage as checkUsage } from "./check.js";
import { explain, usage as explainUsage } from "./explain.js";
import { init, usage as initUsage } from "./init.js";
import { readPackageFile } from "./files.js";
import { run as updateRun, usage as updateUsage } from "./update.js";

const { version } = JSON.parse(readPackageFile("package.json"));

const usage = `blueprint ${version}

Usage: blueprint <command> [options]

  init      put Blueprint in this folder
  check     say whether the project is whole, and how to fix what is not
  update    bring the new version of Blueprint's own files

  why       what the code at this place is there for
  trace     where one identifier lives: document, code, tests, tasks
  map       which of the documents' identifiers are anchored in the code
  budget    whether this delivery is reviewable in one sitting

  --help    this text
  --version the version

${initUsage}

${checkUsage}

${explainUsage}

${updateUsage}`;

export async function run(argv, folder, write, options = {}) {
  const [command, ...rest] = argv;
  if (!command || command === "--help" || command === "-h" || command === "help") {
    write(usage);
    return command ? 0 : 2;
  }
  if (command === "--version" || command === "-v") {
    write(version);
    return 0;
  }
  if (command === "init") return init(rest, folder, write);
  if (command === "check") return check(rest, folder, write);
  if (command === "update") return updateRun(rest, folder, write, options);
  if (["why", "trace", "map", "budget"].includes(command)) return explain(command, rest, folder, write);
  write(`I do not know the command ${command}.\n\n${usage}`);
  return 2;
}

// Run only when this file is what was called, not when a test imports it.
if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) {
  process.exitCode = await run(process.argv.slice(2), process.cwd(), (line) => process.stdout.write(`${line}\n`));
}
