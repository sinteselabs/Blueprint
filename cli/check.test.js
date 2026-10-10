// What `blueprint check` has to find, on real folders in a temporary place.
// The same script the blueprint-status skill carries, so these checks cover both.
// Run with: node --test "cli/**/*.test.js"

import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { after, before, describe, it } from "node:test";

import { run } from "./blueprint.js";
import { PACKAGE } from "./files.js";

const STATE = readFileSync(join(PACKAGE, "skills", "blueprint-record", "assets", "state.example.md"), "utf8");
const MARKS = ["<!-- blueprint:start -->", "<!-- blueprint:end -->"];
let root;

async function cli(folder, ...argv) {
  const lines = [];
  const code = await run(argv, folder, (line) => lines.push(line));
  return { code, out: lines.join("\n") };
}

function put(path, text) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, text, "utf8");
}

/**
 * A project whose state is the filled example, with every file that state names.
 * `change` rewrites the state before it is written, to break one thing on purpose.
 */
function project(name, change = (text) => text) {
  const folder = join(root, name);
  put(join(folder, ".blueprint", "state.md"), change(STATE));
  put(join(folder, ".blueprint", "journal", "milestones.md"), "# Marcos\n\n| Data | O que foi alcançado |\n|---|---|\n| 2026-10-09 | A descrição do sistema ficou pronta |\n");
  put(join(folder, "docs", "system-description.md"), "# Descrição do sistema\n\n> **Em resumo:** a clínica marca consultas por telefone e perde horários.\n");
  put(join(folder, "docs", "requirements.md"), "# Requisitos\n\n> **Em resumo:** a recepção marca e cancela; o paciente confirma.\n");
  put(join(folder, "docs", "research.md"), "# Pesquisa\n\n> **Em resumo:** nada pesquisado ainda.\n");
  put(join(folder, "docs", "decisions.md"), "# Decisões\n\n## D-001 · Aplicativo web em vez de aplicativo de celular\n\n- **Decisão:** aplicativo web.\n- **Situação:** decidida\n");
  return folder;
}

before(() => {
  root = mkdtempSync(join(tmpdir(), "blueprint-check-"));
});

after(() => {
  rmSync(root, { recursive: true, force: true });
});

describe("blueprint check", () => {
  it("says nothing is wrong about a whole project", async () => {
    const { code, out } = await cli(project("whole"), "check");
    assert.equal(code, 0, out);
    assert.match(out, /nothing is wrong/);
    assert.match(out, /ok\s+the state file has its ten sections/);
    assert.ok(!out.includes("problem"), out);
  });

  it("finds a document the state calls ready and is not there, and says how to fix it", async () => {
    const folder = project("missing-document");
    rmSync(join(folder, "docs", "system-description.md"));
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+every document the state names is there/);
    assert.match(out, /docs\/system-description\.md is not there/);
    assert.match(out, /fix: /);
    assert.match(out, /1 problem found/);
  });

  it("finds a count that does not agree with the checklist", async () => {
    const folder = project("counts", (text) => text.replace("| requirements | open | 2 of 3 |", "| requirements | open | 1 of 3 |"));
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+the steps and their counts agree/);
    assert.match(out, /requirements says 1 of 3, and the checklist has 2 of 3/);
  });

  it("finds a step that is advanced with a question unanswered", async () => {
    const folder = project("advanced", (text) => text.replace("| requirements | open | 2 of 3 |", "| requirements | advanced | 2 of 3 |"));
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /requirements is advanced with 2 of 3 answered/);
  });

  it("finds a leftover of a template in a ready document", async () => {
    const folder = project("leftover");
    put(join(folder, "docs", "system-description.md"), "# Descrição do sistema\n\n> **Em resumo:** {{WHAT_IT_IS}}\n");
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+no ready document carries a leftover of its template/);
  });

  it("finds a link between documents that leads nowhere", async () => {
    const folder = project("broken-link");
    put(join(folder, "docs", "system-description.md"), "# Descrição do sistema\n\nVeja os [requisitos](requirements.md) e o [plano](plan.md).\n");
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+the links between documents lead somewhere/);
    assert.match(out, /points at plan\.md/);
    assert.ok(!out.includes("points at requirements.md"), "the link that leads somewhere is not reported");
  });

  it("finds a decision in the state that is not in the decisions record", async () => {
    const folder = project("lost-decision");
    put(join(folder, "docs", "decisions.md"), "# Decisões\n\nNenhuma ainda.\n");
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+every decision in the state is in the decisions record/);
    assert.match(out, /D-001/);
  });

  it("finds a second state file inside the project", async () => {
    const folder = project("two-states");
    put(join(folder, "apps", "web", ".blueprint", "state.md"), STATE);
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+there is one state file in this project/);
    assert.match(out, /apps\/web/);
  });

  it("finds a journal that is not there when the journal is what records", async () => {
    const folder = project("no-journal");
    rmSync(join(folder, ".blueprint", "journal"), { recursive: true });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+the project journal is there/);
  });

  it("leaves the prepared repository alone while the plan is not closed", async () => {
    const { out } = await cli(project("not-time-yet"), "check");
    assert.match(out, /skipped\s+the repository is prepared for development \(the plan is not closed yet/);
  });

  it("asks for the Blueprint block once the plan is closed", async () => {
    const closed = (text) =>
      text
        .replace("| plan | not-started | 0 of 2 |", "| plan | closed | 2 of 2 |")
        .replace("- [ ] O que vem primeiro\n- [ ] Quem faz o quê", "- [x] O que vem primeiro\n- [x] Quem faz o quê")
        .replace("| plan | not-started | - |", "| plan | ready | docs/plan.md |");
    const folder = project("plan-closed", closed);
    put(join(folder, "docs", "plan.md"), "# Plano\n\n> **Em resumo:** duas fases.\n");
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+the repository is prepared for development/);
    assert.match(out, /AGENTS\.md has no Blueprint block/);

    put(join(folder, "AGENTS.md"), `# Projeto\n\n${MARKS[0]}\n## Blueprint\n\nO plano está em \`docs/plan.md\`, e o estado em \`.blueprint/state.md\`.\n${MARKS[1]}\n`);
    put(join(folder, "CLAUDE.md"), "See @AGENTS.md for how to work on this project.\n");
    const again = await cli(folder, "check");
    assert.equal(again.code, 0, again.out);
    assert.match(again.out, /ok\s+the repository is prepared for development/);
    assert.match(again.out, /ok\s+what the entry file names is there/);
  });

  it("says plainly when there is no project here", async () => {
    const folder = join(root, "no-project");
    mkdirSync(folder, { recursive: true });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 2);
    assert.match(out, /I found no Blueprint project here/);
  });

  it("says when the state file cannot be read as a state file", async () => {
    const folder = join(root, "unreadable");
    put(join(folder, ".blueprint", "state.md"), "this is not a state file\n");
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1);
    assert.match(out, /problem\s+the state file can be read/);
    assert.match(out, /state-format\.md/);
  });

  it("finds the project from a folder inside it", async () => {
    const folder = project("from-inside");
    mkdirSync(join(folder, "docs", "specs"), { recursive: true });
    const { code } = await cli(join(folder, "docs", "specs"), "check");
    assert.equal(code, 0);
  });

  it("gives the same result as JSON, for an agent to read", async () => {
    const folder = project("as-json");
    rmSync(join(folder, "docs", "requirements.md"));
    const { code, out } = await cli(folder, "check", "--json");
    assert.equal(code, 1);
    const result = JSON.parse(out);
    assert.equal(result.project, folder);
    assert.ok(result.checks.length > 5, "every check is in the result");
    const problem = result.checks.find((one) => one.how === "problem");
    assert.match(problem.what, /every document the state names is there/);
    assert.ok(problem.fix, "a problem comes with how to fix it");
    assert.ok(result.checks.some((one) => one.how === "skipped" && one.why), "and a skipped one says why");
  });
});
