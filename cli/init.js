// `blueprint init`: puts Blueprint in this folder, and only in this folder.
// It never overwrites what is already there (FR-39), and it creates no document:
// those are written by the interview.

import { readFileSync, writeFileSync } from "node:fs";
import { join, relative, sep } from "node:path";

import { MARKS, copySkills, installationAbove, isFile, readPackageFile, writeNew, writeRecord } from "./files.js";

const AGENTS = ["claude", "codex", "antigravity"];
const WHERE = { claude: ".claude/skills", codex: ".agents/skills", antigravity: ".agents/skills" };

export const usage = `Usage: blueprint init [--dry-run] [--agent claude|codex|antigravity]

  Puts Blueprint in this folder: the skills where each coding agent reads them,
  a record of what was installed, and the Blueprint block of AGENTS.md.

  --dry-run   say what would be done, write nothing
  --agent     install for one agent only (default: all of them)`;

function parse(argv) {
  const options = { pretend: false, agent: null };
  for (let i = 0; i < argv.length; i += 1) {
    const argument = argv[i];
    if (argument === "--dry-run") options.pretend = true;
    else if (argument === "--agent") {
      options.agent = (argv[i + 1] || "").toLowerCase();
      i += 1;
      if (!AGENTS.includes(options.agent)) return { error: `--agent takes one of: ${AGENTS.join(", ")}` };
    } else return { error: `I do not know the option ${argument}` };
  }
  return options;
}

/** Where the skills go: one folder per agent asked for, without repeating `.agents/skills`. */
function folders(agent) {
  const wanted = agent ? [agent] : AGENTS;
  return [...new Set(wanted.map((name) => WHERE[name]))];
}

/**
 * Adds the Blueprint block to AGENTS.md, or creates the file with it.
 * A file that already has the block is left alone: the block is the setup skill's to update.
 */
function entryFile(folder, { pretend }) {
  const path = join(folder, "AGENTS.md");
  const block = readPackageFile("skills", "blueprint-setup", "assets", "agents-starter.md")
    .split(MARKS.start)
    .slice(1)
    .join(MARKS.start);
  const text = `${MARKS.start}${block.split(MARKS.end)[0]}${MARKS.end}\n`;
  if (!isFile(path)) return { what: writeNew(path, text, { pretend }), path };
  const existing = readFileSync(path, "utf8");
  if (existing.includes(MARKS.start)) return { what: "skipped", path };
  if (!pretend) writeFileSync(path, `${existing.replace(/\s*$/, "")}\n\n${text}`, "utf8");
  return { what: "added to", path };
}

/**
 * An agent that reads a file of its own, and not AGENTS.md, gets one line pointing at it.
 * Claude Code looks at CLAUDE.md first; the Antigravity CLI reads GEMINI.md and does not
 * read AGENTS.md at all (measured on version 0.63.0, 11/10/2026: the word AGENTS.md does
 * not appear anywhere in it). Without this, those agents open a prepared project knowing
 * none of its rules.
 */
const POINTERS = ["CLAUDE.md", "GEMINI.md"];

function pointerFile(folder, name, { pretend }) {
  const path = join(folder, name);
  const line = "See @AGENTS.md for how to work on this project.\n";
  if (!isFile(path)) return { what: writeNew(path, line, { pretend }), path };
  const existing = readFileSync(path, "utf8");
  if (existing.includes("AGENTS.md")) return { what: "skipped", path };
  if (!pretend) writeFileSync(path, `${existing.replace(/\s*$/, "")}\n\n${line}`, "utf8");
  return { what: "added to", path };
}

export function init(argv, folder, write) {
  const options = parse(argv);
  if (options.error) {
    write(`${options.error}\n\n${usage}`);
    return 2;
  }
  const { pretend } = options;

  const above = installationAbove(folder);
  if (above) {
    write(`Blueprint is already installed in ${relative(folder, above).split(sep).join("/") || above}, above this folder.`);
    write("A project has one installation. Run this in the project's own folder, or work from the one that is there.");
    return 1;
  }

  const notice = `# Blueprint\n\nThe skills in this folder are part of Blueprint, and carry its licence with them.\n\n${readPackageFile("LICENSE")}`;
  const done = [];
  for (const into of folders(options.agent)) {
    done.push(...copySkills(join(folder, ...into.split("/")), { relativeTo: folder, pretend }));
    done.push({ path: `${into}/BLUEPRINT-LICENSE.md`, what: writeNew(join(folder, ...into.split("/"), "BLUEPRINT-LICENSE.md"), notice, { pretend }) });
  }

  const entry = entryFile(folder, { pretend });
  const pointers = POINTERS.map((name) => pointerFile(folder, name, { pretend }));
  const { version } = writeRecord(folder, done, { pretend });

  const created = done.filter((f) => f.what === "created").length;
  const skipped = done.filter((f) => f.what === "skipped").length;
  write(pretend ? `Blueprint ${version} would be installed in this folder:` : `Blueprint ${version} installed in this folder.`);
  write(`  ${pretend ? "would create" : "created"}   ${created} file${created === 1 ? "" : "s"}`);
  if (skipped) write(`  kept        ${skipped} file${skipped === 1 ? "" : "s"} that were already there`);
  for (const file of [entry, ...pointers]) {
    const name = relative(folder, file.path).split(sep).join("/");
    write(`  ${file.what === "skipped" ? "kept" : file.what === "created" ? (pretend ? "would create" : "created") : pretend ? "would add to" : "added to"}  ${name}`);
  }
  if (pretend) write("\nNothing was written. Run it without --dry-run to install.");
  else write("\nNext: open your coding agent in this folder and say what you want to do.");
  return 0;
}
