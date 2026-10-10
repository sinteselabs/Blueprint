// What `blueprint update` has to do: bring Blueprint's own files, and touch
// nothing the person wrote. The three cases that matter are told apart by the
// hash of each file: what the package carries, what the record says was
// installed, and what is on disk now.
// Run with: node --test "cli/**/*.test.js"

import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, describe, it } from "node:test";

import { run } from "./blueprint.js";
import { PACKAGE } from "./files.js";

let root;

async function cli(folder, ...argv) {
  const lines = [];
  const code = await run(argv, folder, (line) => lines.push(line), { ask: () => "y" });
  return { code, out: lines.join("\n") };
}

const RECORD = join(".blueprint", "installed.json");
const SKILL = ".claude/skills/blueprint/SKILL.md";

function record(folder) {
  return JSON.parse(readFileSync(join(folder, RECORD), "utf8"));
}

function keepRecord(folder, change) {
  const kept = change(record(folder));
  writeFileSync(join(folder, RECORD), `${JSON.stringify(kept, null, 2)}\n`, "utf8");
}

/** A folder with Blueprint installed for Claude Code, as `init` leaves it. */
async function installed(name) {
  const folder = join(root, name);
  mkdirSync(folder, { recursive: true });
  await cli(folder, "init", "--agent", "claude");
  return folder;
}

before(() => {
  root = mkdtempSync(join(tmpdir(), "blueprint-update-"));
});

after(() => {
  rmSync(root, { recursive: true, force: true });
});

describe("blueprint update", () => {
  it("says there is nothing to do when the installed files are this version's", async () => {
    const { code, out } = await cli(await installed("current"), "update");
    assert.equal(code, 0, out);
    assert.match(out, /Nothing to do/);
  });

  it("brings a file that changed in the package, and says the version it moved to", async () => {
    const folder = await installed("changed");
    const before = readFileSync(join(folder, ...SKILL.split("/")), "utf8");
    keepRecord(folder, (kept) => ({ ...kept, blueprint: "0.0.1", files: { ...kept.files, [SKILL]: "0".repeat(64) } }));
    writeFileSync(join(folder, ...SKILL.split("/")), before.replace(/^/, "a version from before\n"), "utf8");
    keepRecord(folder, (kept) => ({ ...kept, files: { ...kept.files, [SKILL]: JSON.parse(readFileSync(join(folder, RECORD), "utf8")).files[SKILL] } }));

    // what is on disk is what the record says, and both differ from the package: Blueprint's to update
    const { createHash } = await import("node:crypto");
    const disk = createHash("sha256").update(readFileSync(join(folder, ...SKILL.split("/")), "utf8")).digest("hex");
    keepRecord(folder, (kept) => ({ ...kept, files: { ...kept.files, [SKILL]: disk } }));

    const { code, out } = await cli(folder, "update", "--yes");
    assert.equal(code, 0, out);
    assert.match(out, /0\.0\.1 -> \d+\.\d+\.\d+/);
    assert.match(out, /change\s+1 file/);
    assert.equal(readFileSync(join(folder, ...SKILL.split("/")), "utf8"), before, "the file is the package's again");
    assert.equal(record(folder).files[SKILL], createHash("sha256").update(before).digest("hex"), "and the record says so");
  });

  it("keeps a file of Blueprint that the person edited, and writes the new version beside it", async () => {
    const folder = await installed("edited");
    const path = join(folder, ...SKILL.split("/"));
    const mine = "o meu jeito de conduzir\n";
    writeFileSync(path, mine, "utf8");
    keepRecord(folder, (kept) => ({ ...kept, blueprint: "0.0.1" }));

    const { code, out } = await cli(folder, "update", "--yes");
    assert.equal(code, 0, out);
    assert.match(out, /keep\s+\.claude\/skills\/blueprint\/SKILL\.md, which you edited/);
    assert.match(out, /SKILL\.md\.new/);
    assert.equal(readFileSync(path, "utf8"), mine, "what the person wrote is still there");
    assert.ok(readFileSync(`${path}.new`, "utf8").includes("name: blueprint"), "and the new version is beside it");
  });

  it("adds a file the package has and the installation does not", async () => {
    const folder = await installed("added");
    const path = join(folder, ...SKILL.split("/"));
    rmSync(path);
    keepRecord(folder, (kept) => {
      const files = { ...kept.files };
      delete files[SKILL];
      return { ...kept, blueprint: "0.0.1", files };
    });

    const { code, out } = await cli(folder, "update", "--yes");
    assert.equal(code, 0, out);
    assert.match(out, /add\s+1 file/);
    assert.ok(existsSync(path), "the file is there now");
    assert.ok(record(folder).files[SKILL], "and in the record");
  });

  it("removes a file of Blueprint that this version no longer carries", async () => {
    const folder = await installed("removed");
    const gone = ".claude/skills/blueprint/references/old-thing.md";
    const path = join(folder, ...gone.split("/"));
    const text = "o que o Blueprint carregava antes\n";
    writeFileSync(path, text, "utf8");
    const { createHash } = await import("node:crypto");
    keepRecord(folder, (kept) => ({
      ...kept,
      blueprint: "0.0.1",
      files: { ...kept.files, [gone]: createHash("sha256").update(text).digest("hex") },
    }));

    const { code, out } = await cli(folder, "update", "--yes");
    assert.equal(code, 0, out);
    assert.match(out, /remove\s+1 file/);
    assert.ok(!existsSync(path), "the file is gone");
    assert.ok(!record(folder).files[gone], "and out of the record");
  });

  it("puts back a file of Blueprint that was deleted", async () => {
    const folder = await installed("put-back");
    const path = join(folder, ...SKILL.split("/"));
    rmSync(path);
    const { code, out } = await cli(folder, "update", "--yes");
    assert.equal(code, 0, out);
    assert.match(out, /put back\s+1 file/);
    assert.ok(existsSync(path));
  });

  it("does not touch the documents, the state or the journal", async () => {
    const folder = await installed("mine");
    const files = {
      "docs/system-description.md": "# Descrição do sistema\n\nO que eu escrevi.\n",
      "docs/requirements.md": "# Requisitos\n\nO que eu escrevi.\n",
      "docs/research.md": "# Pesquisa\n\nNada ainda.\n",
      "docs/decisions.md": "# Decisões\n\n## D-001 · Aplicativo web\n\n- **Situação:** decidida\n",
      ".blueprint/state.md": readFileSync(join(PACKAGE, "skills", "blueprint-record", "assets", "state.example.md"), "utf8"),
      ".blueprint/journal/milestones.md": "# Marcos\n",
      "AGENTS.md": "# Meu projeto\n\n<!-- blueprint:start -->\nmeu bloco\n<!-- blueprint:end -->\n",
    };
    for (const [path, text] of Object.entries(files)) {
      mkdirSync(join(folder, ...path.split("/").slice(0, -1)), { recursive: true });
      writeFileSync(join(folder, ...path.split("/")), text, "utf8");
    }
    keepRecord(folder, (kept) => ({ ...kept, blueprint: "0.0.1" }));
    rmSync(join(folder, ...SKILL.split("/"))); // something for the update to do

    const { code, out } = await cli(folder, "update", "--yes");
    assert.equal(code, 0, out);
    for (const [path, text] of Object.entries(files)) {
      assert.equal(readFileSync(join(folder, ...path.split("/")), "utf8"), text, `${path} is untouched`);
    }
    assert.match(out, /Your documents, your state, your journal and your AGENTS\.md are not touched/);
  });

  it("with --dry-run, writes nothing", async () => {
    const folder = await installed("pretend");
    const path = join(folder, ...SKILL.split("/"));
    rmSync(path);
    const { code, out } = await cli(folder, "update", "--dry-run");
    assert.equal(code, 0);
    assert.match(out, /Nothing was written/);
    assert.ok(!existsSync(path), "it did not put the file back");
  });

  it("without --yes and with nobody to ask, writes nothing and says how to apply", async () => {
    const folder = await installed("no-answer");
    rmSync(join(folder, ...SKILL.split("/")));
    const lines = [];
    const code = await run(["update"], folder, (line) => lines.push(line)); // no `ask`: nobody at the terminal
    assert.equal(code, 0);
    assert.match(lines.join("\n"), /Run it again with --yes/);
    assert.ok(!existsSync(join(folder, ...SKILL.split("/"))));
  });

  it("runs the check after updating", async () => {
    const folder = await installed("then-check");
    rmSync(join(folder, ...SKILL.split("/")));
    const { out } = await cli(folder, "update", "--yes");
    assert.match(out, /I found no Blueprint project here/, "the check ran, and said there is no project yet");
  });

  it("says plainly when there is no installation in this folder", async () => {
    const folder = join(root, "not-installed");
    mkdirSync(folder, { recursive: true });
    const { code, out } = await cli(folder, "update");
    assert.equal(code, 1);
    assert.match(out, /no Blueprint installation in this folder/);
  });

  it("says when the record cannot be read", async () => {
    const folder = await installed("bad-record");
    writeFileSync(join(folder, RECORD), "{ not json\n", "utf8");
    const { code, out } = await cli(folder, "update");
    assert.equal(code, 2);
    assert.match(out, /I could not read/);
  });
});
