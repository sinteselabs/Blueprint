// Reading, copying and recording the files the CLI puts in a project.
// Nothing here prints, and nothing here decides: `init.js` does both.

import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

/** The root of the installed package, which holds `cli/` and `skills/`. */
export const PACKAGE = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export const MARKS = { start: "<!-- blueprint:start -->", end: "<!-- blueprint:end -->" };

/** Every file under `folder`, as paths relative to it, in a stable order. */
export function filesUnder(folder) {
  const found = [];
  const walk = (at) => {
    for (const entry of readdirSync(at, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const here = join(at, entry.name);
      if (entry.isDirectory()) walk(here);
      else if (entry.isFile()) found.push(relative(folder, here).split(sep).join("/"));
    }
  };
  if (existsSync(folder)) walk(folder);
  return found;
}

export function hashOf(text) {
  return createHash("sha256").update(text).digest("hex");
}

/**
 * Writes `text` at `path` unless something is already there.
 * Returns "created", or "skipped" when the file exists, which is never overwritten (FR-39).
 */
export function writeNew(path, text, { pretend = false } = {}) {
  if (existsSync(path)) return "skipped";
  if (!pretend) {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, text, "utf8");
  }
  return "created";
}

/** The skills this package carries, as paths relative to `skills/`. */
export function skillFiles() {
  return filesUnder(join(PACKAGE, "skills"));
}

/**
 * Copies the skills into `into`, one by one, and returns what happened to each.
 * The paths that come back are relative to `relativeTo`, which is the project folder.
 */
export function copySkills(into, { relativeTo, pretend = false }) {
  const done = [];
  for (const path of skillFiles()) {
    const text = readFileSync(join(PACKAGE, "skills", path), "utf8");
    const target = join(into, ...path.split("/"));
    done.push({ path: relative(relativeTo, target).split(sep).join("/"), hash: hashOf(text), what: writeNew(target, text, { pretend }) });
  }
  return done;
}

/**
 * Walks up from `folder` looking for a Blueprint installation or project above it.
 * Returns the folder that holds it, or null. The folder itself does not count.
 */
export function installationAbove(folder) {
  let at = resolve(folder);
  for (;;) {
    const up = dirname(at);
    if (up === at) return null;
    at = up;
    if (existsSync(join(at, ".blueprint", "installed.json")) || existsSync(join(at, ".blueprint", "state.md"))) return at;
  }
}

/** The record of what was installed: the version, when, and every file with its hash. */
export function writeRecord(folder, files, { pretend = false } = {}) {
  const { version } = JSON.parse(readFileSync(join(PACKAGE, "package.json"), "utf8"));
  const record = {
    blueprint: version,
    installed_at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    files: Object.fromEntries(files.filter((f) => f.what === "created").map((f) => [f.path, f.hash])),
  };
  const path = join(folder, ".blueprint", "installed.json");
  const text = `${JSON.stringify(record, null, 2)}\n`;
  if (!pretend) {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, text, "utf8");
  }
  return { path, version };
}

export function readPackageFile(...parts) {
  return readFileSync(join(PACKAGE, ...parts), "utf8");
}

export function isFile(path) {
  return existsSync(path) && statSync(path).isFile();
}
