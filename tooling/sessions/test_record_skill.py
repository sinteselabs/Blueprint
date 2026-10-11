#!/usr/bin/env python3
"""
Runs the blueprint-record skill in two real Claude Code sessions and checks
what they left on disk.

Session 1 starts an empty project and saves the first block of an interview.
Session 2 comes back to it with the last answer of the step, a decision, and a
key the person pasted and asked to keep. The test then reads the files:

- the state passes check_state.py after each session, with the step open at
  3 of 4 and then advanced at 4 of 4;
- the first session, which says it is ending, leaves a session record, and the second,
  which does not, leaves none and says why;
- the decision is in the decisions record;
- the pasted key is in no file of the project;
- nothing under skills/ in this repository changed.

What the person says in each session is in `record/`, written as someone
conducting an interview would write it.

It needs Claude Code on the PATH, takes a few minutes and spends model usage,
so it is not one of the checks to run before every change. Run it after
changing the record skill:

    python tooling/sessions/test_record_skill.py

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not
run: Claude Code is missing, or the account's usage limit was reached.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from harness import REPO, find_claude, refused, run, skills_changes, spent, used_skill, verdict

PROMPTS = Path(__file__).resolve().parent / "record"
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
PLANTED_KEY = "chave-falsa-de-teste-9f3k2x7q"


def step_row(project: Path, step: str) -> str:
    """The situation and the count of one step, as written in the state's Steps table."""
    for line in (project / ".blueprint" / "state.md").read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] == step:
            return f"{cells[1]} {cells[2]}"
    return "missing"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    claude = find_claude()
    if not claude:
        print("cannot find Claude Code on the PATH; this test runs real sessions with it")
        return 2
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    before = skills_changes()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True, prefix="blueprint session é ") as folder:
        project = Path(folder) / "padaria-pedidos"
        project.mkdir()
        state = project / ".blueprint" / "state.md"
        sessions = project / ".blueprint" / "journal" / "sessions"

        def state_passes() -> bool:
            return state.is_file() and subprocess.run([sys.executable, str(CHECK_STATE), str(state)], capture_output=True).returncode == 0

        turns = []

        def say(number: int, prompt: Path) -> bool:
            """One session of the person. False when it could not run at all."""
            said = prompt.read_text(encoding="utf-8")
            turn = run(claude, project, said, timeout=900, web=False)
            turns.append(turn)
            print(f"\n--- session {number}\n    the person: {said.strip().splitlines()[0][:100]} ...\n    the agent:", flush=True)
            for line in turn.reply.splitlines():
                print("      " + line)
            return not refused(turn)

        print("session 1: an empty project, the first block answered ...", flush=True)
        if not say(1, PROMPTS / "01-first-block.txt"):
            print(f"could not run: {refused(turns[-1])}")
            print("nothing was tested; run this again when the limit resets")
            return 2
        check("session 1 ran", turns[0].code == 0, f"exit {turns[0].code}")
        check("session 1: the record skill guided the session", used_skill(turns[0], "blueprint-record"))
        check("session 1: the state passes check_state.py", state_passes())
        if state.is_file():
            check("session 1: the step is open at 3 of 4", step_row(project, "system-description") == "open 3 of 4", step_row(project, "system-description"))
        check("session 1: one session record", sessions.is_dir() and len(list(sessions.glob("*.md"))) == 1)

        print("session 2: the last answer, a decision and a pasted key ...", flush=True)
        if not say(2, PROMPTS / "02-second-block.txt"):
            print(f"could not run: {refused(turns[-1])}")
            return 2
        check("session 2 ran", turns[1].code == 0, f"exit {turns[1].code}")
        check("session 2: the state passes check_state.py", state_passes())
        if state.is_file():
            check("session 2: the step is advanced at 4 of 4", step_row(project, "system-description") == "advanced 4 of 4", step_row(project, "system-description"))
        # The session record is written when the session is ending. The second prompt does not say
        # that it is, so there must still be one, and the agent has to say why it wrote no other.
        check("session 2: still one session record, because this session is not ending", sessions.is_dir() and len(list(sessions.glob("*.md"))) == 1, f"{len(list(sessions.glob('*.md')))} records")
        check("session 2: it says why it wrote no session record", any(word in turns[1].reply.lower() for word in ("não gravei registro de sessão", "não está terminando", "não gravei o registro da sessão")))
        decisions = project / "docs" / "decisions.md"
        check("session 2: the decision is in the decisions record", decisions.is_file() and "D-001" in decisions.read_text(encoding="utf-8"))
        holding = [p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file() and PLANTED_KEY in p.read_text(encoding="utf-8", errors="replace")]
        check("session 2: the pasted key is in no file", not holding, ", ".join(holding))
        outside = [p.name for p in Path(folder).iterdir() if p != project]
        check("nothing was written beside the project folder", not outside, ", ".join(outside))
    check("nothing under skills/ changed in this repository", skills_changes() == before)
    print("\n" + spent(turns))
    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
