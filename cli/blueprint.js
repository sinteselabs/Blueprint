#!/usr/bin/env node
// The Blueprint CLI. It does only what does not need a model and always gives
// the same answer: install, check, update. What takes judgment is in the skills.

import { realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { init, usage as initUsage } from "./init.js";
import { readPackageFile } from "./files.js";

const { version } = JSON.parse(readPackageFile("package.json"));

const usage = `blueprint ${version}

Usage: blueprint <command> [options]

  init      put Blueprint in this folder
  check     say whether the project is whole, and how to fix what is not
  update    bring the new version of Blueprint's own files

  --help    this text
  --version the version

${initUsage}`;

const NOT_BUILT = {
  check: "`blueprint check` is not built yet. Until it is, ask your coding agent: the `blueprint-status` skill goes through the same list by reading.",
  update: "`blueprint update` is not built yet. Until it is, install the new version in a copy of the folder and compare, or ask your coding agent to.",
};

export function run(argv, folder, write) {
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
  if (command in NOT_BUILT) {
    write(NOT_BUILT[command]);
    return 2;
  }
  write(`I do not know the command ${command}.\n\n${usage}`);
  return 2;
}

// Run only when this file is what was called, not when a test imports it.
if (process.argv[1] && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url))) {
  process.exitCode = run(process.argv.slice(2), process.cwd(), (line) => process.stdout.write(`${line}\n`));
}
