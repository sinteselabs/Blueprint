// What the four views of the comprehension layer have to answer, on real folders
// in a temporary place. The same engine the blueprint-explain skill carries, so
// these cover both it and `blueprint why | trace | map | budget`.
// Run with: node --test "cli/**/*.test.js"

import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { after, before, describe, it } from "node:test";

import { run } from "./blueprint.js";
import { PACKAGE } from "./files.js";

const STATE = readFileSync(join(PACKAGE, "skills", "blueprint-record", "assets", "state.example.md"), "utf8");
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

const REQUIREMENTS = `# Requisitos

## Requisitos funcionais

| Nº | Requisito | Prioridade | Vem de |
|---|---|---|---|
| FR-01 | A recepção cancela uma consulta, e só a recepção | Primeira versão | o que a pessoa disse |
| FR-02 | O paciente confirma a presença | Primeira versão | o que a pessoa disse |

## Requisitos não funcionais

| Nº | Requisito | Prioridade | Vem de |
|---|---|---|---|
| NFR-01 | A tela responde em menos de 2 segundos, D-001 | Primeira versão | deduzido |
`;

const DECISIONS = `# Decisões

## D-001 · Aplicativo web em vez de aplicativo de celular

- **Decisão:** aplicativo web.
`;

const CANCEL = `// FR-01: só a recepção cancela uma consulta.
export function cancelAppointment(id, by) {
  if (by.role !== "reception") throw new Error("not allowed");
  return { id, cancelled: true };
}

// NFR-01: a lista é paginada para a tela responder rápido.
export function pageOf(items) {
  return items.slice(0, 20);
}
`;

/**
 * A project with documents that number things, code that anchors some of them, a
 * test, an orphaned anchor and two task specs. `extra` adds or replaces files.
 */
function project(name, extra = {}) {
  const folder = join(root, name);
  put(join(folder, ".blueprint", "state.md"), STATE);
  put(join(folder, ".blueprint", "journal", "milestones.md"), "# Marcos\n");
  put(join(folder, "docs", "requirements.md"), REQUIREMENTS);
  put(join(folder, "docs", "decisions.md"), DECISIONS);
  put(join(folder, "docs", "specs", "01-01-cancelar.md"), "# Cancelar\n\n## Quando está pronta\n\n- [x] A recepção cancela\n\n## Vem de\n\nFR-01, D-001\n");
  put(join(folder, "src", "cancel.js"), CANCEL);
  put(join(folder, "src", "plain.js"), "export function noAnchorHere() {}\n");
  put(join(folder, "src", "legacy.js"), "// FR-99: algo que ninguém escreveu.\nexport function mystery() {}\n");
  put(join(folder, "tests", "cancel.test.js"), "// FR-01\ntest(\"só a recepção cancela\", () => {});\n");
  for (const [path, text] of Object.entries(extra)) put(join(folder, ...path.split("/")), text);
  return folder;
}

/** The same project, inside a git repository with one commit, so budget has a diff to read. */
function committed(name, extra = {}) {
  const folder = project(name, extra);
  const git = (...argv) => execFileSync("git", argv, { cwd: folder, stdio: "ignore" });
  git("init");
  git("-c", "user.email=t@example.com", "-c", "user.name=Test", "add", "-A");
  git("-c", "user.email=t@example.com", "-c", "user.name=Test", "commit", "-m", "start");
  return folder;
}

before(() => {
  // a path with an accent and a space, which is where this repository itself lives (NFR-08)
  root = mkdtempSync(join(tmpdir(), "blueprint é explain "));
});

after(() => {
  rmSync(root, { recursive: true, force: true });
});

describe("blueprint why", () => {
  it("answers from the nearest anchor at or above the line", async () => {
    const { code, out } = await cli(project("why-line"), "why", "src/cancel.js:8");
    assert.equal(code, 0, out);
    // line 7 carries NFR-01 and line 1 carries FR-01: the nearest above comes first
    assert.ok(out.indexOf("NFR-01") < out.indexOf("FR-01"), out);
    assert.match(out, /A tela responde em menos de 2 segundos/);
    assert.match(out, /docs\/requirements\.md:/);
    assert.match(out, /depends on D-001/);
  });

  it("names the task that delivered it", async () => {
    const { out } = await cli(project("why-task"), "why", "src/cancel.js:2");
    assert.match(out, /delivered by docs\/specs\/01-01-cancelar\.md/);
  });

  it("says plainly that a file carries no anchor, and what is anchored beside it", async () => {
    const { code, out } = await cli(project("why-none"), "why", "src/plain.js");
    assert.equal(code, 1);
    assert.match(out, /carries no anchor/);
    assert.match(out, /Anchored beside it: FR-01, FR-99/);
    assert.match(out, /A file with no anchor is normal/);
  });

  it("says when the anchor is in the code and in no document", async () => {
    const { out } = await cli(project("why-orphan"), "why", "src/legacy.js");
    assert.match(out, /FR-99/);
    assert.match(out, /no document says this id/);
  });

  it("says when the file is not there", async () => {
    const { code, out } = await cli(project("why-missing"), "why", "src/nope.js");
    assert.equal(code, 2);
    assert.match(out, /I cannot find src\/nope\.js/);
  });

  it("needs a file", async () => {
    const { code, out } = await cli(project("why-bare"), "why");
    assert.equal(code, 2);
    assert.match(out, /why needs a file/);
  });
});

describe("blueprint trace", () => {
  it("says where one identifier lives: document, code, tests and tasks", async () => {
    const { code, out } = await cli(project("trace-all"), "trace", "FR-01");
    assert.equal(code, 0, out);
    assert.match(out, /said in\s+docs\/requirements\.md:7/);
    assert.match(out, /code\s+src\/cancel\.js:1/);
    assert.match(out, /tests\s+tests\/cancel\.test\.js:1/);
    assert.match(out, /tasks\s+docs\/specs\/01-01-cancelar\.md/);
  });

  it("does not care about the case of the identifier", async () => {
    const { code, out } = await cli(project("trace-case"), "trace", "fr-01");
    assert.equal(code, 0);
    assert.match(out, /^FR-01/);
  });

  it("says that a requirement is implemented nowhere, instead of staying quiet", async () => {
    const { code, out } = await cli(project("trace-nowhere"), "trace", "FR-02");
    assert.equal(code, 0);
    assert.match(out, /code\s+nowhere yet/);
    assert.match(out, /tests\s+nothing proves it/);
  });

  it("calls out an identifier the code has and no document has", async () => {
    const { out } = await cli(project("trace-orphan"), "trace", "FR-99");
    assert.match(out, /in the code and in no document/);
  });

  it("says when nothing in the project names it", async () => {
    const { code, out } = await cli(project("trace-unknown"), "trace", "FR-77");
    assert.equal(code, 1);
    assert.match(out, /Nothing in this project names FR-77/);
  });
});

describe("blueprint map", () => {
  it("counts what the documents promise against what the code anchors", async () => {
    const { code, out } = await cli(project("map-all"), "map");
    assert.equal(code, 0, out);
    assert.match(out, /2 of 3 requirements and use cases anchored in the code/);
    assert.match(out, /FR-01\s+1 place\s+1 test/);
    assert.match(out, /FR-02\s+nowhere\s+no test/);
    assert.match(out, /Orphaned anchors, in the code and in no document: FR-99/);
  });

  it("does not read an installed tool's files, or prose, as anchors", async () => {
    // Blueprint's own skills name FR-01 and D-004 to explain the convention, and a
    // prepared project's entry file repeats them. Reading those as anchors reported
    // the whole installation as orphaned.
    const folder = project("map-not-prose", {
      ".claude/skills/blueprint-explain/references/anchors.md": "An anchor is FR-77 written in a comment.\n",
      ".claude/skills/blueprint/assets/documents/task-spec.md": "Comes from: FR-78, D-404.\n",
      "AGENTS.md": "The code carries the id of what it serves, such as FR-88.\n",
      "README.md": "This project implements FR-89.\n",
    });
    const { out } = await cli(folder, "map");
    assert.match(out, /Orphaned anchors, in the code and in no document: FR-99$/m);
    for (const id of ["FR-77", "FR-78", "D-404", "FR-88", "FR-89"]) {
      assert.doesNotMatch(out, new RegExp(id), `${id} is an example in prose, not an anchor`);
    }
  });

  it("does not count a decision as something to implement", async () => {
    const { out } = await cli(project("map-decisions"), "map");
    // D-001 is listed, and it is not in the ratio: a decision explains a shape
    assert.match(out, /D-001\s+nowhere/);
    assert.match(out, /of 3 requirements/);
  });
});

describe("blueprint budget", () => {
  it("says a small delivery can be handed over as one", async () => {
    const folder = committed("budget-small");
    writeFileSync(join(folder, "src", "plain.js"), "// FR-02: o paciente confirma.\nexport function confirm() {}\n", "utf8");
    const { code, out } = await cli(folder, "budget");
    assert.equal(code, 0, out);
    assert.match(out, /Within budget/);
    assert.match(out, /The budget is 400 lines and 10 files/);
    assert.match(out, /Anchored in the files touched: FR-02/);
  });

  it("counts files git does not track yet, which is most of what an agent writes", async () => {
    const folder = committed("budget-untracked");
    for (let at = 1; at <= 12; at += 1) {
      writeFileSync(join(folder, "src", `bulk${at}.js`), "// noise\n".repeat(40), "utf8");
    }
    const { code, out } = await cli(folder, "budget");
    assert.equal(code, 1, out);
    assert.match(out, /Over budget/);
    assert.match(out, /one commit per requirement/);
    assert.match(out, /Biggest: src\/bulk/);
  });

  it("is over budget on one very long new file too", async () => {
    const folder = committed("budget-long");
    writeFileSync(join(folder, "src", "huge.js"), "// one long new file\n".repeat(500), "utf8");
    const { code, out } = await cli(folder, "budget");
    assert.equal(code, 1);
    assert.match(out, /Over budget/);
  });

  it("says there is nothing to measure where git cannot read a diff", async () => {
    const { code, out } = await cli(project("budget-no-git"), "budget");
    assert.equal(code, 2);
    assert.match(out, /nothing to measure/);
  });
});

describe("the four views", () => {
  it("say the same thing as JSON, for an agent to read", async () => {
    const folder = project("as-json");
    const why = JSON.parse((await cli(folder, "why", "src/cancel.js:8", "--json")).out);
    assert.equal(why.project, folder);
    assert.equal(why.answers[0].id, "NFR-01");
    assert.equal(why.answers[0].because[0], "D-001");

    const trace = JSON.parse((await cli(folder, "trace", "FR-99", "--json")).out);
    assert.equal(trace.orphan, true);

    const map = JSON.parse((await cli(folder, "map", "--json")).out);
    assert.equal(map.total, 3);
    assert.deepEqual(map.orphans, ["FR-99"]);
  });

  it("say plainly when there is no Blueprint project here", async () => {
    const folder = join(root, "bare");
    mkdirSync(folder, { recursive: true });
    const { code, out } = await cli(folder, "map");
    assert.equal(code, 2);
    assert.match(out, /I found no Blueprint project here/);
  });

  it("are in the CLI's own help", async () => {
    const { out } = await cli(root, "--help");
    for (const view of ["why", "trace", "map", "budget"]) {
      assert.match(out, new RegExp(`\\n  ${view} `), `${view} is in the help`);
    }
  });
});
