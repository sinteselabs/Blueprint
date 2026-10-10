// What `blueprint init` has to do, checked on real folders in a temporary place.
// Run with: node --test cli/

import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, describe, it } from "node:test";

import { run } from "./blueprint.js";

const MARKS = ["<!-- blueprint:start -->", "<!-- blueprint:end -->"];
let root;

/** Runs the CLI in `folder` and gives back the exit code and everything it printed. */
function cli(folder, ...argv) {
  const lines = [];
  const code = run(argv, folder, (line) => lines.push(line));
  return { code, out: lines.join("\n") };
}

function project(name) {
  const folder = join(root, name);
  mkdirSync(folder, { recursive: true });
  return folder;
}

before(() => {
  root = mkdtempSync(join(tmpdir(), "blueprint-cli-"));
});

after(() => {
  rmSync(root, { recursive: true, force: true });
});

describe("blueprint init", () => {
  it("installs in an empty folder and says what comes next", () => {
    const folder = project("empty");
    const { code, out } = cli(folder, "init");
    assert.equal(code, 0);
    assert.match(out, /installed in this folder/);
    assert.match(out, /Next: open your coding agent/);

    for (const skills of [".claude/skills", ".agents/skills"]) {
      assert.ok(existsSync(join(folder, skills, "blueprint", "SKILL.md")), `${skills} has the entry skill`);
      assert.ok(existsSync(join(folder, skills, "blueprint-record", "references", "state-format.md")), `${skills} has a reference`);
      assert.ok(readFileSync(join(folder, skills, "BLUEPRINT-LICENSE.md"), "utf8").includes("MIT"), `${skills} carries the licence`);
    }
    assert.equal(readdirSync(join(folder, ".claude", "skills")).filter((n) => n.startsWith("blueprint")).length, 7, "seven skills");
  });

  it("records what it installed, with a hash per file", () => {
    const folder = project("record");
    cli(folder, "init");
    const record = JSON.parse(readFileSync(join(folder, ".blueprint", "installed.json"), "utf8"));
    assert.match(record.blueprint, /^\d+\.\d+\.\d+$/);
    assert.match(record.installed_at, /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/);
    const one = ".claude/skills/blueprint/SKILL.md";
    assert.match(record.files[one], /^[0-9a-f]{64}$/, "the file is in the record with its hash");
    assert.ok(Object.keys(record.files).length > 20, "every file it copied is in the record");
  });

  it("writes the Blueprint block of AGENTS.md and points CLAUDE.md at it", () => {
    const folder = project("entry");
    cli(folder, "init");
    const agents = readFileSync(join(folder, "AGENTS.md"), "utf8");
    for (const mark of MARKS) assert.ok(agents.includes(mark), `AGENTS.md has ${mark}`);
    assert.ok(!agents.includes("{{"), "no placeholder is left");
    assert.ok(!agents.includes("<!-- The block the CLI writes"), "the template's own comment is not copied");
    assert.match(agents, /\.blueprint\/state\.md/);
    assert.match(readFileSync(join(folder, "CLAUDE.md"), "utf8"), /AGENTS\.md/);
  });

  it("never overwrites what is already there", () => {
    const folder = project("existing");
    const rules = "# Meu projeto\n\n- Commits em portugues.\n";
    writeFileSync(join(folder, "AGENTS.md"), rules, "utf8");
    writeFileSync(join(folder, "CLAUDE.md"), "Leia o AGENTS.md.\n", "utf8");
    mkdirSync(join(folder, ".claude", "skills", "blueprint"), { recursive: true });
    writeFileSync(join(folder, ".claude", "skills", "blueprint", "SKILL.md"), "mine\n", "utf8");

    const { code, out } = cli(folder, "init");
    assert.equal(code, 0);
    assert.match(out, /kept\s+1 file that w/);
    assert.equal(readFileSync(join(folder, ".claude", "skills", "blueprint", "SKILL.md"), "utf8"), "mine\n", "the file that was there is untouched");
    const agents = readFileSync(join(folder, "AGENTS.md"), "utf8");
    assert.ok(agents.startsWith(rules.trimEnd()), "the person's rules stay at the top, as they were");
    assert.ok(agents.includes(MARKS[0]), "and the block was added after them");
    assert.equal(readFileSync(join(folder, "CLAUDE.md"), "utf8"), "Leia o AGENTS.md.\n", "a CLAUDE.md that already names AGENTS.md is left alone");
  });

  it("leaves a block that is already there for the setup skill to update", () => {
    const folder = project("has-block");
    writeFileSync(join(folder, "AGENTS.md"), `# Projeto\n\n${MARKS[0]}\nminha versao do bloco\n${MARKS[1]}\n`, "utf8");
    cli(folder, "init");
    const agents = readFileSync(join(folder, "AGENTS.md"), "utf8");
    assert.match(agents, /minha versao do bloco/);
    assert.equal(agents.split(MARKS[0]).length - 1, 1, "there is one block, not two");
  });

  it("refuses to install inside another installation, and writes nothing", () => {
    const outer = project("outer");
    cli(outer, "init");
    const inner = join(outer, "apps", "web");
    mkdirSync(inner, { recursive: true });

    const { code, out } = cli(inner, "init");
    assert.equal(code, 1);
    assert.match(out, /already installed/);
    assert.ok(!existsSync(join(inner, ".blueprint")), "nothing was written in the inner folder");
    assert.ok(!existsSync(join(inner, "AGENTS.md")));
  });

  it("with --dry-run, writes nothing and says what it would do", () => {
    const folder = project("pretend");
    const { code, out } = cli(folder, "init", "--dry-run");
    assert.equal(code, 0);
    assert.match(out, /would be installed/);
    assert.match(out, /would create\s+\d+ files/);
    assert.match(out, /Nothing was written/);
    assert.deepEqual(readdirSync(folder), [], "the folder is still empty");
  });

  it("with --agent claude, installs only where Claude Code reads", () => {
    const folder = project("one-agent");
    assert.equal(cli(folder, "init", "--agent", "claude").code, 0);
    assert.ok(existsSync(join(folder, ".claude", "skills", "blueprint", "SKILL.md")));
    assert.ok(!existsSync(join(folder, ".agents")), "the other folder was not created");
  });

  it("says what it does not understand, and does not guess", () => {
    const folder = project("bad-options");
    assert.equal(cli(folder, "init", "--agent", "emacs").code, 2);
    assert.equal(cli(folder, "init", "--whatever").code, 2);
    assert.equal(cli(folder, "sideways").code, 2);
    assert.deepEqual(readdirSync(folder), [], "nothing was written for a command it does not know");
  });

  it("creates no document: those come from the interview", () => {
    const folder = project("no-documents");
    cli(folder, "init");
    assert.ok(!existsSync(join(folder, "docs")), "no documents folder");
    assert.ok(!existsSync(join(folder, ".blueprint", "state.md")), "no state file either");
  });
});

describe("blueprint", () => {
  it("prints the version", () => {
    const { code, out } = cli(root, "--version");
    assert.equal(code, 0);
    assert.match(out, /^\d+\.\d+\.\d+$/);
  });

  it("with no command, prints the usage and exits 2", () => {
    const { code, out } = cli(root);
    assert.equal(code, 2);
    assert.match(out, /Usage: blueprint <command>/);
  });

  it("says plainly that check and update are not built yet", () => {
    for (const command of ["check", "update"]) {
      const { code, out } = cli(root, command);
      assert.equal(code, 2, `${command} exits 2`);
      assert.match(out, /not built yet/);
    }
  });
});
