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
  // a path with an accent and a space, which is where this repository itself lives
  root = mkdtempSync(join(tmpdir(), "blueprint é check "));
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
    const pointing = await cli(folder, "check");
    assert.equal(pointing.code, 1, "an agent that reads only GEMINI.md would still be blind here");
    assert.match(pointing.out, /problem\s+the agents' own files name AGENTS\.md/);
    assert.match(pointing.out, /GEMINI\.md/);

    put(join(folder, "GEMINI.md"), "See @AGENTS.md for how to work on this project.\n");
    const again = await cli(folder, "check");
    assert.equal(again.code, 0, again.out);
    assert.match(again.out, /ok\s+the repository is prepared for development/);
    assert.match(again.out, /ok\s+what the entry file names is there/);
    assert.match(again.out, /ok\s+the agents' own files name AGENTS\.md/);
  });

  it("says plainly when there is no project here", async () => {
    const folder = join(root, "no-project");
    mkdirSync(folder, { recursive: true });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 2);
    assert.match(out, /I found no Blueprint project here/);
  });

  it("after init, says the project has not started instead of that nothing is here", async () => {
    // The first minute of a fresh install: Blueprint is there and the state file is not,
    // because the conversation writes it. That is not a missing piece.
    const folder = join(root, "just-installed");
    mkdirSync(folder, { recursive: true });
    await cli(folder, "init");
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 2);
    assert.match(out, /Blueprint is installed in this folder/);
    assert.match(out, /say what you want to do/);
    assert.doesNotMatch(out, /I found no Blueprint project here/);
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

describe("blueprint check: the code and the documents", () => {
  const NUMBERED = "# Requisitos\n\n| Nº | Requisito | Prioridade | Vem de |\n|---|---|---|---|\n| FR-01 | A recepção cancela uma consulta | Primeira versão | o que a pessoa disse |\n| FR-02 | O paciente confirma a presença | Primeira versão | o que a pessoa disse |\n";

  /** A project whose requirements are numbered, so the code has something to point at. */
  function numbered(name, files = {}) {
    const folder = project(name);
    put(join(folder, "docs", "requirements.md"), NUMBERED);
    for (const [path, text] of Object.entries(files)) put(join(folder, ...path.split("/")), text);
    return folder;
  }

  it("skips the three while the project has no anchor in its code", async () => {
    const { code, out } = await cli(numbered("no-anchors"), "check");
    assert.equal(code, 0, out);
    assert.match(out, /skipped\s+no anchor in the code names an id the documents do not have \(there is no anchor/);
    assert.match(out, /skipped\s+a task whose done-when list is complete is anchored in the code/);
  });

  it("finds an anchor the code has and no document has", async () => {
    const folder = numbered("orphan", { "src/old.js": "// FR-99: ninguém escreveu isso.\nexport function mystery() {}\n" });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1, out);
    assert.match(out, /problem\s+no anchor in the code names an id the documents do not have/);
    assert.match(out, /FR-99: the code names it and no document does/);
    assert.match(out, /fix: /);
  });

  it("finds a task spec that comes from an id no document has", async () => {
    const folder = numbered("broken-trace", {
      "src/cancel.js": "// FR-01\nexport function cancel() {}\n",
      "docs/specs/01-01-cancelar.md": "# Cancelar\n\n## Vem de\n\nFR-01, FR-42\n",
    });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1, out);
    assert.match(out, /problem\s+every task spec comes from an id the documents have/);
    assert.match(out, /01-01-cancelar\.md comes from FR-42/);
  });

  it("finds a task that says it is done and is anchored nowhere", async () => {
    const folder = numbered("drift", {
      "src/cancel.js": "// FR-01\nexport function cancel() {}\n",
      "docs/specs/01-02-confirmar.md": "# Confirmar\n\n## Quando está pronta\n\n- [x] O paciente confirma\n\n## Vem de\n\nFR-02\n",
    });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 1, out);
    assert.match(out, /problem\s+a task whose done-when list is complete is anchored in the code/);
    assert.match(out, /01-02-confirmar\.md: the task says it is done and nothing in the code carries the id/);
  });

  it("says nothing is wrong when the code and the documents agree", async () => {
    const folder = numbered("agreeing", {
      "src/cancel.js": "// FR-01\nexport function cancel() {}\n",
      "src/confirm.js": "// FR-02\nexport function confirm() {}\n",
      "docs/specs/01-01-cancelar.md": "# Cancelar\n\n## Quando está pronta\n\n- [x] A recepção cancela\n\n## Vem de\n\nFR-01\n",
      "docs/specs/01-02-confirmar.md": "# Confirmar\n\n## Quando está pronta\n\n- [x] O paciente confirma\n\n## Vem de\n\nFR-02\n",
    });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 0, out);
    assert.match(out, /ok\s+no anchor in the code names an id the documents do not have/);
    assert.match(out, /ok\s+every task spec comes from an id the documents have/);
    assert.match(out, /ok\s+a task whose done-when list is complete is anchored in the code/);
  });

  it("does not fire on a task that is not finished yet", async () => {
    const folder = numbered("unfinished", {
      "src/cancel.js": "// FR-01\nexport function cancel() {}\n",
      "docs/specs/01-02-confirmar.md": "# Confirmar\n\n## Quando está pronta\n\n- [ ] O paciente confirma\n\n## Vem de\n\nFR-02\n",
    });
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 0, out);
    assert.match(out, /skipped\s+a task whose done-when list is complete is anchored in the code \(no task spec has its done-when list complete yet\)/);
  });

  it("skips the three when the documents live in a tool", async () => {
    const folder = project("in-a-tool", (text) => text.replace("documents_at: docs/", "documents_at: notion"));
    const { code, out } = await cli(folder, "check");
    assert.equal(code, 0, out);
    assert.match(out, /skipped\s+no anchor in the code names an id the documents do not have \(the documents are in notion/);
  });
});
