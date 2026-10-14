#!/usr/bin/env node
// The comprehension layer's engine. It answers the questions a developer asks
// while working — why is this line here, where does this requirement live, what
// is anchored nowhere, is this delivery reviewable — from the code and the
// documents, so that nobody has to read a document to get an answer.
//
// It only reads. Run it from the project folder, or name the folder:
//
//     node explain.js why <file[:line]> [folder] [--json]
//     node explain.js trace <ID> [folder] [--json]
//     node explain.js map [folder] [--json]
//     node explain.js budget [folder] [--base <ref>] [--json]
//
// Exit code 0 when it answered, 1 when there was nothing to answer with, or the
// delivery is over budget, 2 when it could not run at all.
//
// The project check lives in the blueprint-status skill and this engine lives
// here: each is a single source for something that must always give the same
// answer (ARD-05). A skill is copied on its own, so the few lines the two share
// are copied here, not imported.

import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, extname, isAbsolute, join, relative, resolve, sep } from "node:path";

/** The identifiers the documents number: the anchors. references/anchors.md has the convention. */
const ID = /\b(FR|NFR|UC|D|ARD)-(\d{1,4})\b/g;

const SKIP = new Set([
  "node_modules", ".git", ".hg", ".svn", "dist", "build", "out", "target", "coverage",
  ".next", ".nuxt", ".cache", ".venv", "venv", "__pycache__", "vendor", ".blueprint", ".worktrees",
]);
const BINARY = new Set([
  ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg", ".pdf", ".zip", ".gz", ".tar",
  ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".mp4", ".mov", ".wav", ".exe", ".dll",
  ".so", ".dylib", ".class", ".jar", ".wasm", ".db", ".sqlite", ".lock", ".bin",
]);
const TOO_BIG = 512 * 1024;
const MOST_FILES = 5000;
const DEEPEST = 12;

/** What one person reviews in one sitting. A delivery over this is split, not read. */
export const BUDGET = { lines: 400, files: 10 };

/** The project folder: the one given, or the nearest one above with `.blueprint/state.md`. */
export function findProject(from) {
  let at = resolve(from);
  for (;;) {
    if (existsSync(join(at, ".blueprint", "state.md"))) return at;
    const up = dirname(at);
    if (up === at) return null;
    at = up;
  }
}

const posix = (path) => path.split(sep).join("/");

/** A test file, by the names every language uses for them. */
export function isTest(path) {
  const name = (path.split("/").pop() || "").replace(/\.[^.]+$/, "");
  return /(^|\/)(tests?|specs?|__tests__)\//i.test(path) || /(^|[._-])(test|spec)([._-]|$)/i.test(name);
}

/** The state file's header and the rows of its Documents table. Null when there is no state. */
export function readState(project) {
  const path = join(project, ".blueprint", "state.md");
  if (!existsSync(path)) return null;
  const lines = readFileSync(path, "utf8").split(/\r?\n/);
  const header = {};
  const closes = lines[0]?.trim() === "---" ? lines.findIndex((line, i) => i > 0 && line.trim() === "---") : -1;
  if (closes > 0) {
    for (const line of lines.slice(1, closes)) {
      const match = /^([a-z_]+):\s*(.*)$/.exec(line);
      if (match) header[match[1]] = match[2].trim();
    }
  }
  const rows = [];
  let inside = false;
  for (const line of lines.slice(closes + 1)) {
    if (line.startsWith("## ")) inside = line.slice(3).trim() === "Documents";
    if (!inside || !line.trim().startsWith("|")) continue;
    const cells = line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
    if (cells.length < 3 || cells.every((cell) => /^:?-+:?$/.test(cell)) || cells[0] === "Document") continue;
    rows.push({ document: cells[0], situation: cells[1], where: cells[2] });
  }
  return { header, rows, documentsAt: header.documents_at || "docs/" };
}

/** The documents folder, or null when the documents live in a tool and not in this repository. */
export function documentsFolder(state) {
  const at = state.documentsAt;
  if (/^[a-z]+$/i.test(at) && !at.includes("/")) return null;
  return at.endsWith("/") ? at : `${at}/`;
}

function idsIn(line) {
  return [...new Set(line.match(ID) || [])];
}

/**
 * Whether this line declares the id rather than merely mentioning it: the id opens
 * the line, the heading or the row's first cell. A requirement mentioned inside
 * another requirement's row must not win over the row that defines it.
 */
function declares(line, id) {
  const trimmed = line.trim();
  if (trimmed.startsWith("|")) {
    return trimmed.replace(/^\|/, "").split("|")[0].includes(id);
  }
  return new RegExp(`^[#>\\s]*[-*\\s]*\\*{0,2}${id}\\b`).test(trimmed);
}

function textBeside(line, id) {
  if (line.trim().startsWith("|")) {
    const cells = line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
    const at = cells.findIndex((cell) => cell.includes(id));
    const next = at >= 0 ? cells.slice(at + 1).find((cell) => cell && !/^:?-+:?$/.test(cell)) : null;
    if (next) return next;
  }
  const after = line.slice(line.indexOf(id) + id.length).replace(/^[\s·—–:;,.*)\]|-]+/, "").trim();
  return after || line.trim();
}

/** Every identifier the documents declare: id -> where it is said, and what it says there. */
export function catalogue(project, state) {
  const found = new Map();
  for (const { where } of state.rows) {
    if (!where || where === "-") continue;
    const full = join(project, where);
    if (!existsSync(full) || !statSync(full).isFile()) continue;
    readFileSync(full, "utf8").split(/\r?\n/).forEach((line, i) => {
      const here = idsIn(line);
      for (const id of here) {
        const declared = declares(line, id);
        const already = found.get(id);
        if (already && (already.declared || !declared)) continue;
        found.set(id, {
          id,
          document: where,
          line: i + 1,
          says: textBeside(line, id),
          with: here.filter((other) => other !== id),
          declared,
        });
      }
    });
  }
  return found;
}

/** Every anchor in the code: the id, the file, the line and whether it is in a test. */
export function anchors(project, state) {
  const folder = documentsFolder(state);
  const found = [];
  let seen = 0;
  const walk = (at, depth) => {
    if (depth > DEEPEST || seen > MOST_FILES) return;
    let entries;
    try {
      entries = readdirSync(at, { withFileTypes: true });
    } catch {
      return; // a folder we may not read is not an answer we can give: say nothing about it
    }
    for (const entry of entries.sort((a, b) => a.name.localeCompare(b.name))) {
      const here = join(at, entry.name);
      const rel = posix(relative(project, here));
      if (entry.isDirectory()) {
        if (SKIP.has(entry.name) || (folder && `${rel}/` === folder)) continue;
        walk(here, depth + 1);
        continue;
      }
      if (!entry.isFile() || BINARY.has(extname(entry.name).toLowerCase())) continue;
      if (folder && rel.startsWith(folder)) continue; // a document is not code
      seen += 1;
      let text;
      try {
        if (statSync(here).size > TOO_BIG) continue;
        text = readFileSync(here, "utf8");
      } catch {
        continue;
      }
      text.split(/\r?\n/).forEach((line, i) => {
        for (const id of idsIn(line)) found.push({ id, path: rel, line: i + 1, test: isTest(rel) });
      });
    }
  };
  walk(project, 1);
  return found;
}

/** The task specs: which ids each one comes from, and whether its "done when" list is complete. */
export function taskSpecs(project, state) {
  const folder = documentsFolder(state);
  if (!folder) return [];
  const at = join(project, folder, "specs");
  if (!existsSync(at)) return [];
  const found = [];
  for (const name of readdirSync(at).sort()) {
    if (!name.endsWith(".md")) continue;
    const text = readFileSync(join(at, name), "utf8");
    const boxes = [...text.matchAll(/^[ \t]*- \[([ xX])\]/gm)].map(([, mark]) => mark.toLowerCase());
    found.push({
      path: `${folder}specs/${name}`,
      ids: [...new Set(text.match(ID) || [])],
      boxes: boxes.length,
      done: boxes.length > 0 && boxes.every((mark) => mark === "x"),
    });
  }
  return found;
}

/** Everything the views read, gathered once. */
export function gather(project) {
  const state = readState(project);
  if (!state) return null;
  return {
    project,
    state,
    says: catalogue(project, state),
    found: anchors(project, state),
    specs: taskSpecs(project, state),
  };
}

const PREFIXES = ["FR", "NFR", "UC", "D", "ARD"];

function order(a, b) {
  const [prefixA, numberA] = a.split("-");
  const [prefixB, numberB] = b.split("-");
  return PREFIXES.indexOf(prefixA) - PREFIXES.indexOf(prefixB) || Number(numberA) - Number(numberB);
}

const short = (text, most = 72) => (text && text.length > most ? `${text.slice(0, most - 1)}…` : text);

// ---------------------------------------------------------------- the four views

/** Why the code at this place is there: the anchors it carries, the nearest one first. */
export function why(all, target) {
  const match = /^(.*?)(?::(\d+))?$/.exec(target);
  const given = match[1];
  const line = match[2] ? Number(match[2]) : null;
  const full = isAbsolute(given) ? given : join(all.project, given);
  if (!existsSync(full)) return { what: "why", error: `I cannot find ${given} in this project` };
  const path = posix(relative(all.project, full));
  const here = all.found.filter((anchor) => anchor.path === path);
  const above = (anchor) => (line === null || anchor.line <= line ? 0 : 1);
  const sorted = [...here].sort((a, b) => {
    if (line === null) return a.line - b.line;
    return above(a) - above(b) || (above(a) === 0 ? b.line - a.line : a.line - b.line);
  });
  const seen = new Set();
  const answers = [];
  for (const anchor of sorted) {
    if (seen.has(anchor.id)) continue;
    seen.add(anchor.id);
    const said = all.says.get(anchor.id);
    answers.push({
      id: anchor.id,
      at: `${path}:${anchor.line}`,
      says: said ? said.says : null,
      document: said ? `${said.document}:${said.line}` : null,
      because: said ? said.with : [],
      orphan: !said,
      tasks: all.specs.filter((spec) => spec.ids.includes(anchor.id)).map((spec) => spec.path),
    });
  }
  const neighbours = answers.length
    ? []
    : [...new Set(all.found.filter((anchor) => dirname(anchor.path) === dirname(path)).map((anchor) => anchor.id))].sort(order);
  return { what: "why", path, line, answers, neighbours };
}

/** Where one identifier lives: the document that says it, the code, the tests, the tasks. */
export function trace(all, id) {
  const wanted = id.toUpperCase();
  const said = all.says.get(wanted);
  const here = all.found.filter((anchor) => anchor.id === wanted);
  return {
    what: "trace",
    id: wanted,
    says: said ? said.says : null,
    document: said ? `${said.document}:${said.line}` : null,
    because: said ? said.with : [],
    code: here.filter((anchor) => !anchor.test).map((anchor) => `${anchor.path}:${anchor.line}`),
    tests: here.filter((anchor) => anchor.test).map((anchor) => `${anchor.path}:${anchor.line}`),
    tasks: all.specs.filter((spec) => spec.ids.includes(wanted)).map((spec) => spec.path),
    orphan: !said && here.length > 0,
  };
}

/** Which of the things the documents promise are anchored in the code, and which are not. */
export function map(all) {
  const rows = [...all.says.values()].sort((a, b) => order(a.id, b.id)).map((said) => {
    const here = all.found.filter((anchor) => anchor.id === said.id);
    return {
      id: said.id,
      says: said.says,
      document: said.document,
      places: here.filter((anchor) => !anchor.test).length,
      tests: here.filter((anchor) => anchor.test).length,
    };
  });
  const orphans = [...new Set(all.found.map((anchor) => anchor.id))].filter((id) => !all.says.has(id)).sort(order);
  // A decision with no anchor is ordinary: it explains a shape, it is not a thing
  // to build. The ratio is over what the documents promise will exist.
  const promised = rows.filter((row) => ["FR", "NFR", "UC"].includes(row.id.split("-")[0]));
  return {
    what: "map",
    rows,
    orphans,
    anchored: promised.filter((row) => row.places + row.tests > 0).length,
    total: promised.length,
  };
}

/** The files git does not track yet: part of the delivery, invisible to a diff. */
function untracked(project) {
  try {
    const out = execFileSync("git", ["ls-files", "--others", "--exclude-standard", "-z"], {
      cwd: project,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    return out.split("\0").filter(Boolean);
  } catch {
    return [];
  }
}

/** Whether what is about to be handed over is reviewable by one person in one sitting. */
export function budget(all, base) {
  let numstat;
  try {
    numstat = execFileSync("git", ["diff", "--numstat", base || "HEAD"], {
      cwd: all.project,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    });
  } catch {
    const against = base ? ` against ${base}` : "";
    return { what: "budget", error: `I could not read a diff with git in this folder${against}, so there is nothing to measure` };
  }
  const files = [];
  for (const row of numstat.split(/\r?\n/)) {
    const match = /^(\d+|-)\t(\d+|-)\t(.*)$/.exec(row);
    if (!match) continue;
    const [, added, removed, path] = match;
    files.push({
      path,
      added: added === "-" ? 0 : Number(added),
      removed: removed === "-" ? 0 : Number(removed),
      binary: added === "-",
    });
  }
  // A diff does not see a file that was never added, and a delivery written by an
  // agent is mostly new files. Without these, the biggest deliveries measure zero.
  for (const path of untracked(all.project)) {
    const full = join(all.project, path);
    if (BINARY.has(extname(path).toLowerCase())) {
      files.push({ path, added: 0, removed: 0, binary: true, untracked: true });
      continue;
    }
    let added = 0;
    try {
      if (statSync(full).size <= TOO_BIG) added = readFileSync(full, "utf8").split(/\r?\n/).length;
    } catch {
      continue;
    }
    files.push({ path, added, removed: 0, binary: false, untracked: true });
  }
  const lines = files.reduce((sum, file) => sum + file.added + file.removed, 0);
  const touched = new Set(files.map((file) => file.path));
  const ids = [...new Set(all.found.filter((anchor) => touched.has(anchor.path)).map((anchor) => anchor.id))].sort(order);
  return {
    what: "budget",
    base: base || "HEAD",
    files: files.length,
    lines,
    ids,
    over: lines > BUDGET.lines || files.length > BUDGET.files,
    budget: BUDGET,
    biggest: [...files].sort((a, b) => b.added + b.removed - (a.added + a.removed)).slice(0, 3),
  };
}

// ---------------------------------------------------------------- saying it in words

function reportWhy(answer) {
  const where = answer.line ? `${answer.path}:${answer.line}` : answer.path;
  const lines = [];
  if (!answer.answers.length) {
    lines.push(`${where} carries no anchor, so the code does not say what it is for.`);
    if (answer.neighbours.length) lines.push(`  Anchored beside it: ${answer.neighbours.join(", ")}. Run trace on one of those.`);
    lines.push("  A file with no anchor is normal. If this code serves a requirement, one comment with its id answers this question next time.");
    return lines.join("\n");
  }
  lines.push(`${where} is there because of:`);
  for (const found of answer.answers) {
    lines.push(`  ${found.id}  ${found.says ? short(found.says) : "— no document says this id: the anchor is orphaned"}`);
    if (found.document) lines.push(`         said in ${found.document}, anchored at ${found.at}`);
    if (found.because.length) lines.push(`         depends on ${found.because.join(", ")}`);
    if (found.tasks.length) lines.push(`         delivered by ${found.tasks.join(", ")}`);
  }
  return lines.join("\n");
}

function reportTrace(answer) {
  if (!answer.says && !answer.code.length && !answer.tests.length && !answer.tasks.length) {
    return `Nothing in this project names ${answer.id}: no document says it, and no code carries it.`;
  }
  const lines = [`${answer.id}  ${answer.says ? short(answer.says, 96) : "— no document says it"}`];
  if (answer.document) lines.push(`  said in     ${answer.document}`);
  if (answer.because.length) lines.push(`  depends on  ${answer.because.join(", ")}`);
  lines.push(`  code        ${answer.code.length ? answer.code.join(", ") : "nowhere yet"}`);
  lines.push(`  tests       ${answer.tests.length ? answer.tests.join(", ") : "nothing proves it"}`);
  if (answer.tasks.length) lines.push(`  tasks       ${answer.tasks.join(", ")}`);
  if (answer.orphan) lines.push("  This id is in the code and in no document. Either the document lost it, or the anchor is wrong.");
  return lines.join("\n");
}

function reportMap(answer) {
  if (!answer.rows.length) return "The documents of this project number nothing yet, so there is no map to draw.";
  const lines = [`${answer.anchored} of ${answer.total} requirements and use cases anchored in the code`];
  for (const row of answer.rows) {
    const places = row.places ? `${row.places} place${row.places === 1 ? "" : "s"}` : "nowhere";
    const tests = row.tests ? `${row.tests} test${row.tests === 1 ? "" : "s"}` : "no test";
    lines.push(`  ${row.id.padEnd(7)} ${places.padEnd(9)} ${tests.padEnd(8)} ${short(row.says, 56)}`);
  }
  if (answer.orphans.length) lines.push(`Orphaned anchors, in the code and in no document: ${answer.orphans.join(", ")}`);
  return lines.join("\n");
}

function reportBudget(answer) {
  const lines = [
    `${answer.files} file${answer.files === 1 ? "" : "s"}, ${answer.lines} line${answer.lines === 1 ? "" : "s"} changed against ${answer.base}`,
    `The budget is ${answer.budget.lines} lines and ${answer.budget.files} files: what one person reviews in one sitting.`,
  ];
  if (answer.ids.length) lines.push(`Anchored in the files touched: ${answer.ids.join(", ")}`);
  if (answer.over) {
    lines.push("Over budget. Split it: one commit per requirement, so each one can be reviewed on its own.");
    if (answer.biggest.length) {
      lines.push(`Biggest: ${answer.biggest.map((file) => `${file.path} (${file.added + file.removed})`).join(", ")}`);
    }
  } else lines.push("Within budget: this can be handed over as one delivery.");
  return lines.join("\n");
}

export function report(answer) {
  if (answer.error) return answer.error;
  if (answer.what === "why") return reportWhy(answer);
  if (answer.what === "trace") return reportTrace(answer);
  if (answer.what === "map") return reportMap(answer);
  return reportBudget(answer);
}

const VIEWS = ["why", "trace", "map", "budget"];

export const usage = `Usage: explain.js why <file[:line]> | trace <ID> | map | budget [--base <ref>]

  why     what the code at that place is there for, the nearest anchor first
  trace   where one identifier lives: document, code, tests, tasks
  map     which of the documents' identifiers are anchored, and which are not
  budget  whether what is about to be handed over is reviewable in one sitting

  [folder]  the project folder, when it is not the one you are in
  --json    the same answer, for an agent to read`;

export function main(argv, from, write) {
  const json = argv.includes("--json");
  const baseAt = argv.indexOf("--base");
  const base = baseAt >= 0 ? argv[baseAt + 1] : null;
  // With no --base, baseAt is -1, and -1 + 1 would drop the view itself.
  const takes = baseAt >= 0 ? baseAt + 1 : -1;
  const rest = argv.filter((argument, at) => !argument.startsWith("--") && at !== takes);
  const [view, ...given] = rest;
  if (!view || !VIEWS.includes(view)) {
    write(usage);
    return 2;
  }
  const needs = view === "why" || view === "trace";
  const argument = needs ? given[0] : null;
  if (needs && !argument) {
    const what = view === "why" ? "a file, with an optional :line" : "an identifier such as FR-01";
    write(`${view} needs ${what}.\n\n${usage}`);
    return 2;
  }
  const folder = given[needs ? 1 : 0];
  const project = findProject(folder ? resolve(from, folder) : from);
  if (!project) {
    const message = "I found no Blueprint project here: there is no .blueprint/state.md in this folder or above it.";
    write(json ? JSON.stringify({ project: null, error: message }, null, 2) : message);
    return 2;
  }
  let all;
  try {
    all = gather(project);
  } catch (error) {
    const message = `I could not read this project: ${error.message}`;
    write(json ? JSON.stringify({ project, error: message }, null, 2) : message);
    return 2;
  }
  const answer = view === "why" ? why(all, argument)
    : view === "trace" ? trace(all, argument)
      : view === "map" ? map(all)
        : budget(all, base);
  write(json ? JSON.stringify({ project, ...answer }, null, 2) : report(answer));
  if (answer.error) return 2;
  if (answer.what === "budget") return answer.over ? 1 : 0;
  if (answer.what === "why") return answer.answers.length ? 0 : 1;
  if (answer.what === "trace") return answer.says || answer.code.length || answer.tests.length ? 0 : 1;
  return answer.rows.length ? 0 : 1;
}

if (process.argv[1] && import.meta.filename === process.argv[1]) {
  process.exitCode = main(process.argv.slice(2), process.cwd(), (line) => process.stdout.write(`${line}\n`));
}
