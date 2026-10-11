#!/usr/bin/env python3
"""
Runs Blueprint in the Antigravity CLI (the `gemini` command), to see whether the
skills work in the third agent of NFR-01.

It is split in two on purpose, because the two halves cost different things:

1. **What costs nothing.** The CLI's own commands: that it discovers the seven
   skills where `blueprint init --agent antigravity` puts them, that the entry
   file an agent of this family actually reads is there, and that its native
   skills installer takes our `skills/` folder whole. No model is called, so
   this half always runs.
2. **What spends the account.** One turn in a prepared project, to see the
   agent find the entry skill and say where the project is. This half is
   skipped, loudly, when no model can be reached.

    python tooling/sessions/test_antigravity.py [--model NAME] [--no-turn]

Exit code 0 when every check passes, 1 otherwise, 2 when the Antigravity CLI is
not on the machine.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from harness import REPO, verdict

MODEL = "gemini-3.8-flash"
TIMEOUT = 600
NODE = ["node", str(REPO / "cli" / "blueprint.js")]
STATE = (Path(__file__).resolve().parent / "entry" / "padaria-pedidos-state.md").read_text(encoding="utf-8")
SKILLS = ["blueprint", "blueprint-decide", "blueprint-record", "blueprint-research",
          "blueprint-setup", "blueprint-status", "blueprint-survey"]
GO_ON = "Vamos continuar o projeto."
# What the environment says when the key has no credit left, or names no model we may use.
NO_MODEL = ("credits are depleted", "RESOURCE_EXHAUSTED", "no longer available", "API key not valid",
            "PERMISSION_DENIED", "Payment Required", "429")


def launcher() -> list[str]:
    """How to start the Antigravity CLI from here. On Windows it is a `.cmd` shim, which only runs through the shell."""
    path = shutil.which("gemini")
    if not path:
        return []
    return ["cmd", "/c", path] if path.lower().endswith((".cmd", ".bat")) else [path]


def gemini(folder: Path, *arguments: str, timeout: int = 180) -> tuple[int, str]:
    """One command of the CLI in `folder`: the exit code and everything it printed."""
    started = subprocess.run(
        [*launcher(), *arguments], cwd=folder, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout,
    )
    return started.returncode, (started.stdout or "") + (started.stderr or "")


def turn(folder: Path, model: str, prompt: str) -> tuple[str, str, str]:
    """One model turn. Gives back the reply, the error the CLI reported, and the whole log."""
    code, log = gemini(folder, "-m", model, "-p", prompt, "-o", "json",
                       "--approval-mode", "default", timeout=TIMEOUT)
    answer: dict = {}
    for match in re.finditer(r"\{\s*\"session_id\"", log):
        try:
            answer = json.loads(log[match.start():])
            break
        except ValueError:
            continue
    error = json.dumps(answer.get("error") or "", ensure_ascii=False) if answer else (log[-400:] if code else "")
    return str(answer.get("response") or ""), error, log


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    arguments = sys.argv[1:]
    model = arguments[arguments.index("--model") + 1] if "--model" in arguments and len(arguments) > arguments.index("--model") + 1 else MODEL
    if not launcher():
        print("cannot find the Antigravity CLI (`gemini`) on the PATH; this test runs it")
        return 2
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    version = gemini(Path.cwd(), "--version")[1].strip().splitlines()[-1]
    print(f"Antigravity CLI {version}\n", flush=True)

    with tempfile.TemporaryDirectory(prefix="blueprint é antigravity ") as folder:
        root = Path(folder)

        # 1. our own CLI puts the skills where this agent reads them
        ours = root / "nossa-cli"
        ours.mkdir()
        installed = subprocess.run([*NODE, "init", "--agent", "antigravity"], cwd=ours,
                                   capture_output=True, text=True, encoding="utf-8", errors="replace")
        check("our CLI installs Blueprint for the Antigravity CLI", installed.returncode == 0, installed.stdout.strip()[-200:])

        found = gemini(ours, "skills", "list")[1]
        enabled = sorted(re.findall(r"^(blueprint[\w-]*) \[Enabled\]", found, re.MULTILINE))
        check("it discovers the seven skills where our CLI put them", enabled == SKILLS, f"it found {enabled or 'none'}")
        check("and it reads them from .agents/skills", ".agents" in found and ".gemini" not in found.replace(".gemini/skills\n", ""), "the location it printed is another folder")

        # The entry file this family of agents actually reads. It does not open AGENTS.md:
        # on version 0.63.0 the string "AGENTS.md" is not anywhere in the CLI.
        pointer = ours / "GEMINI.md"
        check("the entry file this agent reads is there", pointer.is_file(), "no GEMINI.md: it would work with none of the project's rules")
        check("and it points at AGENTS.md", pointer.is_file() and "AGENTS.md" in pointer.read_text(encoding="utf-8"))

        # 2. its own skills installer, against our folder: a way in that is not ours
        native = root / "instalador-nativo"
        native.mkdir()
        code, log = gemini(native, "skills", "install", str(REPO / "skills"), "--scope", "workspace", "--consent", timeout=300)
        landed = sorted(p.parent.name for p in native.rglob("SKILL.md"))
        check("its native installer takes our skills/ folder whole", code == 0 and landed == SKILLS, f"exit {code}, it installed {landed or 'none'}: {log.strip()[-200:]}")
        files = len(list((native / ".gemini" / "skills").rglob("*"))) if (native / ".gemini" / "skills").is_dir() else 0
        check("with the references, the templates and the check script", files >= 45 and (native / ".gemini" / "skills" / "blueprint-status" / "check.js").is_file(), f"{files} entries")

        if "--no-turn" in arguments:
            print("\n--no-turn: the half that spends the account was not run")
            return verdict(failures, " (the model turn was not run)")

        # 3. one turn in a prepared project: does the entry skill get found and read?
        going = root / "continuando" / "padaria-pedidos"
        going.mkdir(parents=True)
        (going / ".blueprint").mkdir()
        (going / ".blueprint" / "state.md").write_text(STATE, encoding="utf-8", newline="\n")
        subprocess.run([*NODE, "init", "--agent", "antigravity"], cwd=going, capture_output=True, text=True)

        print(f"\n--- continuing a project, with the model {model}\n    the person: {GO_ON}", flush=True)
        reply, error, log = turn(going, model, GO_ON)
        if not reply and any(word in (error + log) for word in NO_MODEL):
            print("    the model could not be reached:")
            print(f"      {error[:300]}")
            print("\ncould not run the turn: this account has no model to spend on right now.")
            print("The half that costs nothing passed. Run it again, or with --no-turn, when the account has credit.")
            return 2 if not failures else verdict(failures)
        print("    the agent:", flush=True)
        for line in reply.splitlines():
            print("      " + line)
        low = reply.lower()
        check("the turn ran", bool(reply), error[:300] or "it said nothing")
        check("it read the Blueprint entry skill", "blueprint" in log.lower() and "skill" in log.lower(), "no sign of a skill in the log")
        check("it says where the project stopped", any(word in low for word in ("requisit", "etapa", "step")), reply[:90])
        check("it asks before writing", "?" in reply)
        check("it wrote no document before the person answered", not (going / "docs").exists())
    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
