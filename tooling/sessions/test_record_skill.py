#!/usr/bin/env python3
"""
Runs the blueprint-record skill in two real Claude Code sessions and checks
what they left on disk.

Session 1 starts an empty project and saves the first block of an interview.
Session 2 comes back to it with the last answer of the step, a decision, and a
key the person pasted and asked to keep. The test then reads the files:

- the state passes check_state.py after each session, with the step open at
  3 of 4 and then advanced at 4 of 4;
- each session left a session record, and the decision is in the decisions record;
- the pasted key is in no file of the project;
- nothing under skills/ in this repository changed.

It needs Claude Code on the PATH, takes a few minutes and spends model usage,
so it is not one of the checks to run before every change. Run it after
changing the record skill:

    python tooling/sessions/test_record_skill.py

Exit code 0 when every case passes, 1 otherwise, 2 when Claude Code is missing.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROMPTS = Path(__file__).resolve().parent / "record"
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
PLANTED_KEY = "chave-falsa-de-teste-9f3k2x7q"
TOOLS = ["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Bash(date *)"]


def session(claude: str, project: Path, prompt: Path) -> int:
    command = [
        claude, "-p", "--plugin-dir", str(REPO), "--add-dir", str(REPO / "skills"),
        "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS,
        "--output-format", "text", "--no-session-persistence",
    ]
    done = subprocess.run(command, cwd=project, input=prompt.read_bytes(), capture_output=True, timeout=900)
    return done.returncode


def step_row(project: Path, step: str) -> str:
    """The situation and the count of one step, as written in the state's Steps table."""
    for line in (project / ".blueprint" / "state.md").read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] == step:
            return f"{cells[1]} {cells[2]}"
    return "missing"


def skills_changes() -> str:
    return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "skills"], capture_output=True, text=True).stdout


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    claude = shutil.which("claude")
    if not claude:
        print("cannot find Claude Code on the PATH; this test runs real sessions with it")
        return 2
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    before = skills_changes()
    with tempfile.TemporaryDirectory(prefix="blueprint session é ") as folder:
        project = Path(folder) / "padaria-pedidos"
        project.mkdir()
        state = project / ".blueprint" / "state.md"
        sessions = project / ".blueprint" / "journal" / "sessions"

        def state_passes() -> bool:
            return state.is_file() and subprocess.run([sys.executable, str(CHECK_STATE), str(state)], capture_output=True).returncode == 0

        print("session 1: an empty project, the first block answered ...", flush=True)
        check("session 1 ran", session(claude, project, PROMPTS / "01-first-block.txt") == 0)
        check("session 1: the state passes check_state.py", state_passes())
        if state.is_file():
            check("session 1: the step is open at 3 of 4", step_row(project, "system-description") == "open 3 of 4", step_row(project, "system-description"))
        check("session 1: one session record", sessions.is_dir() and len(list(sessions.glob("*.md"))) == 1)

        print("session 2: the last answer, a decision and a pasted key ...", flush=True)
        check("session 2 ran", session(claude, project, PROMPTS / "02-second-block.txt") == 0)
        check("session 2: the state passes check_state.py", state_passes())
        if state.is_file():
            check("session 2: the step is advanced at 4 of 4", step_row(project, "system-description") == "advanced 4 of 4", step_row(project, "system-description"))
        check("session 2: two session records", sessions.is_dir() and len(list(sessions.glob("*.md"))) == 2)
        decisions = project / "docs" / "decisions.md"
        check("session 2: the decision is in the decisions record", decisions.is_file() and "D-001" in decisions.read_text(encoding="utf-8"))
        holding = [p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file() and PLANTED_KEY in p.read_text(encoding="utf-8", errors="replace")]
        check("session 2: the pasted key is in no file", not holding, ", ".join(holding))
        outside = [p.name for p in Path(folder).iterdir() if p != project]
        check("nothing was written beside the project folder", not outside, ", ".join(outside))
    check("nothing under skills/ changed in this repository", skills_changes() == before)

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    for name in failures:
        print("  failed: " + name)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
