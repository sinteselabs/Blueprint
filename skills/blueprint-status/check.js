#!/usr/bin/env node
// The project check. It only reads, and it always gives the same answer, which
// is why it is a script and not a list for an agent to follow.
//
// The same file is the one the CLI calls, so there is one source for the check.
// Run it from the project folder, or give the folder as an argument:
//
//     node check.js [folder] [--json]
//
// Exit code 0 when nothing is wrong, 1 when something is, 2 when it could not
// run at all. The list it goes through is in references/check-list.md.

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";

const SECTIONS = [
  "Project kind", "Criteria the person declared", "Steps", "Documents", "Main questions",
  "Refinement questions left for later", "Answers", "Decisions", "Open points", "Next question",
];
const STEPS = ["system-description", "requirements", "modeling", "architecture", "plan"];
const STEP_SITUATIONS = ["not-started", "open", "advanced", "closed"];
const DOCUMENT_SITUATIONS = ["not-started", "in-progress", "ready"];
const MARKS = { start: "<!-- blueprint:start -->", end: "<!-- blueprint:end -->" };
const LINK = /(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;

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

function rows(lines) {
  return lines
    .filter((line) => line.trim().startsWith("|"))
    .map((line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()))
    .filter((cells) => !cells.every((cell) => /^:?-+:?$/.test(cell)))
    .slice(1);
}

/** The state file, read as the parts the check needs. Throws when it cannot be read at all. */
export function readState(project) {
  const text = readFileSync(join(project, ".blueprint", "state.md"), "utf8");
  const lines = text.split(/\r?\n/);
  if (lines[0]?.trim() !== "---") throw new Error("the file does not open with a header between two --- lines");
  const end = lines.findIndex((line, i) => i > 0 && line.trim() === "---");
  if (end < 0) throw new Error("the header is never closed with ---");
  const header = {};
  for (const line of lines.slice(1, end)) {
    const match = /^([a-z_]+):\s*(.*)$/.exec(line);
    if (match) header[match[1]] = match[2].trim();
  }
  const sections = {};
  let current = null;
  let fenced = false;
  for (const line of lines.slice(end + 1)) {
    if (/^\s*(```|~~~)/.test(line)) fenced = !fenced;
    if (!fenced && line.startsWith("## ")) {
      current = line.slice(3).trim();
      sections[current] = [];
    } else if (current) sections[current].push(line);
  }
  const steps = rows(sections.Steps || []).map(([step, situation, count]) => ({ step, situation, count }));
  const documents = rows(sections.Documents || []).map(([document, situation, where]) => ({ document, situation, where }));
  const answered = {};
  let step = null;
  for (const line of sections["Main questions"] || []) {
    if (line.startsWith("### ")) {
      step = line.slice(4).trim();
      answered[step] = { done: 0, total: 0 };
    } else if (step && /^\s*- \[[ xX]\] /.test(line)) {
      answered[step].total += 1;
      if (/^\s*- \[[xX]\]/.test(line)) answered[step].done += 1;
    }
  }
  const decisions = (sections.Decisions || [])
    .map((line) => /^- (D-\d+) · (.*) · (\S+)\s*$/.exec(line.trim()))
    .filter(Boolean)
    .map(([, id, title, situation]) => ({ id, title, situation }));
  return { text, header, sections, steps, documents, answered, decisions };
}

function documentsFolder(state) {
  const at = state.header.documents_at || "docs/";
  return /^[a-z]+$/i.test(at) && !at.includes("/") ? null : at; // a tool's name, not a folder
}

/** Every check, in the order of references/check-list.md. Each one says ok, problem or skipped. */
export function check(project) {
  const found = [];
  const ok = (what) => found.push({ how: "ok", what });
  const problem = (what, fix) => found.push({ how: "problem", what, fix });
  const skipped = (what, why) => found.push({ how: "skipped", what, why });
  const read = (path) => readFileSync(join(project, path), "utf8");
  const there = (path) => existsSync(join(project, path));

  let state;
  try {
    state = readState(project);
  } catch (error) {
    problem("the state file can be read", `${error.message}. The format is in the Blueprint skill blueprint-record, references/state-format.md`);
    return found;
  }

  const missingSections = SECTIONS.filter((name) => !(name in state.sections));
  if (missingSections.length) problem("the state file has its ten sections", `missing: ${missingSections.join(", ")}`);
  else ok("the state file has its ten sections");

  const counts = [];
  for (const { step, situation, count } of state.steps) {
    if (!STEP_SITUATIONS.includes(situation)) counts.push(`${step} is '${situation}', not one of ${STEP_SITUATIONS.join(", ")}`);
    const match = /^(\d+) of (\d+)$/.exec(count);
    if (!match) {
      counts.push(`${step} has '${count}' main questions, which is not written like '2 of 4'`);
      continue;
    }
    const [done, total] = [Number(match[1]), Number(match[2])];
    const checklist = state.answered[step];
    if (checklist && (checklist.done !== done || checklist.total !== total)) {
      counts.push(`${step} says ${done} of ${total}, and the checklist has ${checklist.done} of ${checklist.total}`);
    }
    if (situation === "not-started" && done) counts.push(`${step} is not-started with ${done} answered`);
    if (situation === "open" && total && done >= total) counts.push(`${step} is open with every question answered: it is advanced`);
    if (["advanced", "closed"].includes(situation) && done !== total) counts.push(`${step} is ${situation} with ${done} of ${total} answered`);
  }
  const missingSteps = STEPS.filter((name) => !state.steps.some((row) => row.step === name));
  if (missingSteps.length) counts.push(`the steps ${missingSteps.join(", ")} are missing from the table`);
  if (counts.length) problem("the steps and their counts agree", counts.join("; "));
  else ok("the steps and their counts agree");

  if (state.text.includes("{{")) problem("no template placeholder is left in the state", "a {{...}} is still there: fill it in or take it out");
  else ok("no template placeholder is left in the state");

  const folder = documentsFolder(state);
  if (!folder) {
    skipped("the documents are where the state says", `the documents are in ${state.header.documents_at}, not in this folder`);
  } else {
    const missing = [];
    const leftovers = [];
    for (const { document, situation, where } of state.documents) {
      if (!DOCUMENT_SITUATIONS.includes(situation)) missing.push(`${document} is '${situation}', not one of ${DOCUMENT_SITUATIONS.join(", ")}`);
      if (situation === "not-started") continue;
      if (where === "-" || !where) {
        missing.push(`${document} is ${situation} and has no place in 'Where'`);
        continue;
      }
      if (!there(where)) missing.push(`${document} is ${situation} and ${where} is not there`);
      else if (situation === "ready") {
        const text = read(where);
        if (text.includes("{{") || text.includes("<!--")) leftovers.push(where);
      }
    }
    if (missing.length) problem("every document the state names is there", `${missing.join("; ")}. Either write it, or say in the state where it went`);
    else ok("every document the state names is there");
    if (leftovers.length) problem("no ready document carries a leftover of its template", `${leftovers.join(", ")}: a {{...}} or a template comment is still in it`);
    else ok("no ready document carries a leftover of its template");

    const broken = [];
    for (const { situation, where } of state.documents) {
      if (situation === "not-started" || !where || where === "-" || !there(where)) continue;
      for (const [, target] of read(where).matchAll(LINK)) {
        if (/^(https?:|mailto:|#|<)/.test(target)) continue;
        const path = join(project, dirname(where), decodeURIComponent(target.split("#")[0]));
        if (!existsSync(path)) broken.push(`${where} points at ${target}`);
      }
    }
    if (broken.length) problem("the links between documents lead somewhere", `${broken.join("; ")}. Fix the link or write the file`);
    else ok("the links between documents lead somewhere");

    const plan = state.documents.find((row) => row.document === "plan");
    if (plan && plan.situation !== "not-started" && plan.where !== "-" && there(plan.where)) {
      const named = [...read(plan.where).matchAll(/`([^`]*specs\/[^`]+\.md)`/g)].map(([, path]) => path);
      const absent = named.filter((path) => !there(join(dirname(plan.where), path)) && !there(path));
      if (!named.length) skipped("the plan's tasks have their specs", "the plan names no spec file yet");
      else if (absent.length) problem("the plan's tasks have their specs", `${absent.join(", ")}: the plan names it and it is not there`);
      else ok("the plan's tasks have their specs");
    } else skipped("the plan's tasks have their specs", "there is no plan yet");

    const record = state.documents.find((row) => row.document === "decisions");
    if (state.decisions.length && record && record.where !== "-" && there(record.where)) {
      const text = read(record.where);
      const absent = state.decisions.filter(({ id }) => !text.includes(id));
      if (absent.length) problem("every decision in the state is in the decisions record", `${absent.map((d) => d.id).join(", ")}: the state names it and the record does not`);
      else ok("every decision in the state is in the decisions record");
    } else if (state.decisions.length) problem("every decision in the state is in the decisions record", "the state names decisions and there is no decisions record");
    else ok("every decision in the state is in the decisions record");
  }

  for (const kind of ["memory", "observability"]) {
    const value = state.header[kind];
    if (value === "journal") {
      const journal = join(".blueprint", "journal");
      if (!there(journal)) problem(`the project journal is there, which is where ${kind} goes`, "create .blueprint/journal/ with the milestones and one record per session");
      else if (!readdirSync(join(project, journal), { recursive: true }).some((name) => String(name).endsWith(".md"))) {
        problem(`the project journal is there, which is where ${kind} goes`, ".blueprint/journal/ is empty: the session record and the milestones go there");
      } else ok(`the project journal is there, which is where ${kind} goes`);
    } else skipped(`${kind} answers`, `${kind} is ${value}, and a script cannot tell whether it is answering`);
  }

  const second = [];
  const walk = (at, depth) => {
    if (depth > 3) return;
    for (const entry of readdirSync(at, { withFileTypes: true })) {
      if (!entry.isDirectory() || ["node_modules", ".git", "dist", "build"].includes(entry.name)) continue;
      const here = join(at, entry.name);
      if (existsSync(join(here, ".blueprint", "state.md"))) second.push(relative(project, here).split(sep).join("/"));
      else walk(here, depth + 1);
    }
  };
  walk(project, 1);
  if (second.length) problem("there is one state file in this project", `${second.join(", ")} has another .blueprint/state.md. A project has one`);
  else ok("there is one state file in this project");

  const planClosed = state.steps.some((row) => row.step === "plan" && row.situation === "closed");
  if (!planClosed) skipped("the repository is prepared for development", "the plan is not closed yet, so it is not time");
  else {
    const entry = there("AGENTS.md") ? read("AGENTS.md") : "";
    if (!entry.includes(MARKS.start) || !entry.includes(MARKS.end)) {
      problem("the repository is prepared for development", "AGENTS.md has no Blueprint block: the blueprint-setup skill writes it, and without it an agent that opens this project does not know its rules");
    } else {
      const inside = entry.split(MARKS.start)[1].split(MARKS.end)[0];
      const absent = [...inside.matchAll(/`([^`]+\.md|[^`]+\/)`/g)].map(([, path]) => path).filter((path) => !there(path) && !path.includes("*"));
      if (absent.length) problem("what the entry file names is there", `${absent.join(", ")}: the block names it and it is not there`);
      else ok("what the entry file names is there");
      ok("the repository is prepared for development");
    }
    // An agent that reads only its own file opens a prepared project knowing none of its
    // rules. Claude Code reads CLAUDE.md; the Antigravity CLI reads GEMINI.md.
    const blind = ["CLAUDE.md", "GEMINI.md"].filter((name) => !(there(name) ? read(name) : "").includes("AGENTS.md"));
    if (blind.length) problem("the agents' own files name AGENTS.md", `${blind.join(" and ")}: an agent that reads only that file needs one line pointing at AGENTS.md, or it opens this project without its rules`);
    else ok("the agents' own files name AGENTS.md");

    const developers = Number(state.header.developers || "1");
    if (developers > 1 && folder) {
      const playbooks = join(folder, "playbooks");
      const many = there(playbooks) && readdirSync(join(project, playbooks)).filter((name) => name.endsWith(".md")).length >= 2;
      if (!many) problem("there is a playbook per role", `${developers} people develop this project, and ${playbooks} does not have one file per role`);
      else ok("there is a playbook per role");
    }
  }
  return found;
}

export function report(found) {
  const lines = found.map(({ how, what, fix, why }) => {
    const head = `  ${how.padEnd(8)} ${what}`;
    if (how === "problem") return `${head}\n           fix: ${fix}`;
    if (how === "skipped") return `${head} (${why})`;
    return head;
  });
  const problems = found.filter(({ how }) => how === "problem").length;
  lines.push(problems ? `${problems} problem${problems === 1 ? "" : "s"} found` : "nothing is wrong");
  return lines.join("\n");
}

export function main(argv, from, write) {
  const json = argv.includes("--json");
  const given = argv.find((argument) => !argument.startsWith("--"));
  const where = given ? resolve(from, given) : from;
  const project = findProject(where);
  if (!project) {
    // Blueprint installed and no state file is the normal first minute, not a problem:
    // the state is born from the conversation, so say what to do instead of what is missing.
    const installed = existsSync(join(where, ".blueprint", "installed.json"));
    const message = installed
      ? "Blueprint is installed in this folder, and no project has been started in it yet. Open your coding agent here and say what you want to do: the state file is written as the conversation goes."
      : "I found no Blueprint project here: there is no .blueprint/state.md in this folder or above it.";
    write(json ? JSON.stringify({ project: null, installed, checks: [] }, null, 2) : message);
    return 2;
  }
  let found;
  try {
    found = check(project);
  } catch (error) {
    write(json ? JSON.stringify({ project, error: String(error.message) }, null, 2) : `I could not finish the check: ${error.message}`);
    return 2;
  }
  write(json ? JSON.stringify({ project, checks: found }, null, 2) : report(found));
  return found.some(({ how }) => how === "problem") ? 1 : 0;
}

if (process.argv[1] && import.meta.filename === process.argv[1]) {
  process.exitCode = main(process.argv.slice(2), process.cwd(), (line) => process.stdout.write(`${line}\n`));
}
