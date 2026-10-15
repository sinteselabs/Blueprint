// `blueprint update`: brings the new version of Blueprint's own files, and
// touches nothing the person wrote. What was installed is in
// `.blueprint/installed.json`, with a hash per file, so a file the person
// edited can be told from one that is still Blueprint's.

import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative, sep } from "node:path";

import { PACKAGE, hashOf, readPackageFile, skillFiles } from "./files.js";

export const usage = `Usage: blueprint update [--dry-run] [--yes]

  Brings the new version of Blueprint's own files: the skills, and nothing else.
  A file of Blueprint that you edited is kept, and the new version is written
  beside it, as <name>.new.

  --dry-run   say what would change, write nothing
  --yes       apply without asking (what an agent or a script uses)`;

const RECORD = join(".blueprint", "installed.json");
const LICENCE = "BLUEPRINT-LICENSE.md";

/** The folders the skills were installed into, taken from what the record says. */
function installedFolders(files) {
  const folders = new Set();
  for (const path of Object.keys(files)) {
    const parts = path.split("/");
    const at = parts.findIndex((part) => part.startsWith("blueprint"));
    if (at > 0) folders.add(parts.slice(0, at).join("/"));
  }
  return [...folders];
}

/**
 * What would change, one entry per file: new, changed, yours, gone, removed or same.
 * `yours` is a file of Blueprint that the person edited: it is never overwritten.
 */
export function compare(project, record) {
  const wanted = new Map(); // where the file goes in the project -> where it comes from in the package
  for (const folder of installedFolders(record.files)) {
    for (const source of skillFiles()) wanted.set(`${folder}/${source}`, source);
  }
  const on = (path) => join(project, ...path.split("/"));
  const diskHash = (path) => (existsSync(on(path)) ? hashOf(readFileSync(on(path), "utf8")) : null);

  const changes = [];
  for (const [path, source] of wanted) {
    const want = hashOf(readPackageFile("skills", source));
    const recorded = record.files[path];
    const disk = diskHash(path);
    const change = { path, source, want };
    if (!recorded) change.what = disk === null ? "new" : disk === want ? "same" : "yours";
    else if (disk === null) change.what = "gone";
    else if (disk !== recorded) {
      change.what = "yours";
      change.same = disk === want;
    } else change.what = want === recorded ? "same" : "changed";
    changes.push(change);
  }
  for (const [path, recorded] of Object.entries(record.files)) {
    if (wanted.has(path) || path.endsWith(LICENCE)) continue;
    const disk = diskHash(path);
    if (disk === null) continue;
    changes.push({ path, source: null, want: null, what: disk === recorded ? "removed" : "yours" });
  }
  return changes;
}

function apply(project, changes, record) {
  const files = { ...record.files };
  for (const { path, source, want, what, same } of changes) {
    const target = join(project, ...path.split("/"));
    if (["changed", "new", "gone"].includes(what)) {
      mkdirSync(dirname(target), { recursive: true });
      writeFileSync(target, readPackageFile("skills", source), "utf8");
      files[path] = want;
    } else if (what === "removed") {
      rmSync(target, { force: true });
      delete files[path];
    } else if (what === "yours" && source && !same) {
      writeFileSync(`${target}.new`, readPackageFile("skills", source), "utf8");
    }
  }
  return files;
}

export function update(argv, project, write, { ask = null } = {}) {
  const pretend = argv.includes("--dry-run");
  const yes = argv.includes("--yes");
  const unknown = argv.find((argument) => !["--dry-run", "--yes"].includes(argument));
  if (unknown) {
    write(`I do not know the option ${unknown}\n\n${usage}`);
    return 2;
  }
  const recordPath = join(project, RECORD);
  if (!existsSync(recordPath)) {
    write("I found no Blueprint installation in this folder: there is no .blueprint/installed.json.");
    write("`blueprint init` installs it. If Blueprint came as a plugin, the agent updates it, not this command.");
    return 1;
  }
  let record;
  try {
    record = JSON.parse(readFileSync(recordPath, "utf8"));
    if (!record.files || typeof record.files !== "object") throw new Error("it has no list of files");
  } catch (error) {
    write(`I could not read ${RECORD}: ${error.message}.`);
    return 2;
  }

  const { version } = JSON.parse(readPackageFile("package.json"));
  const changes = compare(project, record);
  const counted = (what) => changes.filter((change) => change.what === what);
  const [created, changed, yours, gone, removed] = ["new", "changed", "yours", "gone", "removed"].map(counted);
  const todo = created.length + changed.length + gone.length + removed.length + yours.filter((c) => c.want && !c.same).length;

  write(record.blueprint === version ? `Blueprint ${version}, the version that is installed.` : `Blueprint ${record.blueprint} -> ${version}`);
  for (const [label, list] of [["change", changed], ["add", created], ["put back", gone], ["remove", removed]]) {
    if (list.length) write(`  ${label.padEnd(9)} ${list.length} file${list.length === 1 ? "" : "s"}`);
  }
  for (const change of yours) {
    write(`  keep      ${change.path}, which you edited${change.want && !change.same ? ` (the new version goes beside it, as ${change.path.split("/").pop()}.new)` : ""}`);
  }
  if (!todo) {
    write("Nothing to do: what is installed is what this version carries.");
    return 0;
  }
  write("Your documents, your state, your journal and your AGENTS.md are not touched.");
  if (changed.length || created.length) write("The Blueprint block of AGENTS.md is the blueprint-setup skill's to refresh: ask your agent after this.");

  if (pretend) {
    write("\nNothing was written. Run it without --dry-run to apply.");
    return 0;
  }
  if (!yes) {
    const answer = ask ? ask("Apply? [y/N] ") : null;
    if (!answer || !/^y(es)?$/i.test(answer.trim())) {
      write("\nNothing was written. Run it again with --yes to apply.");
      return 0;
    }
  }

  const files = apply(project, changes, record);
  writeFileSync(recordPath, `${JSON.stringify({ ...record, blueprint: version, installed_at: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"), files }, null, 2)}\n`, "utf8");
  write(`\nBlueprint ${version} is installed. ${relative(project, recordPath).split(sep).join("/")} says what it carries now.`);
  return 0;
}

export async function run(argv, folder, write, options) {
  const code = update(argv, folder, write, options);
  if (code !== 0 || argv.includes("--dry-run")) return code;
  write("");
  const { main } = await import(`file:///${join(PACKAGE, "skills", "blueprint-status", "check.js").replace(/\\/g, "/")}`);
  const checked = await main([], folder, write);
  return checked === 2 ? 0 : checked; // no project yet is not a problem of the update
}
