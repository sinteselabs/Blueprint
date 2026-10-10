#!/usr/bin/env python3
"""
Runs the blueprint-status skill in two real Claude Code sessions and checks what
it answered and that it changed nothing.

| Case | The folder | What must happen |
|---|---|---|
| a project under way | A state stopped at the requirements, with one planted problem: a document the state calls ready does not exist | Says where the project is, the decision taken and the next question, all from the state, and reports the missing document |
| no project | Empty | Says there is no Blueprint project here, and creates none |

The person only asks "Onde estamos?". Each session is new, so the answer can
only come from the files. The words of a reply are a rough check, and the reply
is printed in full for a person to read.

It needs Claude Code on the PATH, takes a couple of minutes and spends model
usage, so it is not one of the checks to run before every change. Run it after
changing the status skill:

    python tooling/sessions/test_status_skill.py

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not
run at all.
"""

import hashlib
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, find_claude, refused, run, skills_changes, spent, verdict

EXAMPLE_STATE = REPO / "skills" / "blueprint-record" / "assets" / "state.example.md"
ASKS = "Onde estamos?"


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def snapshot(folder: Path) -> dict[str, str]:
    """Every file under the folder with a digest of its content, to tell whether anything changed."""
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()}


def has(reply: str, *groups: tuple[str, ...]) -> bool:
    low = reply.lower()
    return all(any(word in low for word in group) for group in groups)


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
    with tempfile.TemporaryDirectory(prefix="blueprint status é ") as folder:
        root = Path(folder)
        project = root / "a" / "projetos" / "agenda-clinica"
        put(project / ".blueprint" / "state.md", EXAMPLE_STATE.read_text(encoding="utf-8"))
        put(project / ".blueprint" / "journal" / "sessions" / "2026-10-09-1500-claude-code.md", "# Sessão 2026-10-09 15:00 · Claude Code\n\n## Pedido\n\nComeçar o projeto.\n")
        put(project / "docs" / "requirements.md", "# Requisitos\n\n> **Em resumo:** em andamento.\n")
        put(project / "docs" / "research.md", "# Pesquisa\n\n> **Em resumo:** em andamento.\n")
        put(project / "docs" / "decisions.md", "# Decisões\n\n## D-001 · Aplicativo web em vez de aplicativo de celular\n\n- **Decisão:** aplicativo web.\n- **Situação:** decidida\n")
        # Planted: the state calls docs/system-description.md ready, and the file is not there.
        empty = root / "b" / "projetos" / "vazio"
        empty.mkdir(parents=True)
        was = snapshot(root)

        print("running 2 sessions at once ...", flush=True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            under_way, none = pool.map(lambda c: run(claude, c[0], ASKS, (c[1],), web=False), [(project, root / "a"), (empty, root / "b")])
        now = snapshot(root)
        stopped = [refused(s) for s in (under_way, none) if refused(s)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of 2 sessions: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        for name, session in (("a project under way", under_way), ("no project", none)):
            print(f"\n--- {name}\n    the person: {ASKS}\n    the agent:", flush=True)
            for line in session.reply.splitlines():
                print("      " + line)
            check(f"{name}: the session ran", session.code == 0, f"exit {session.code}")

        called = any(kind == "tool" and what.startswith("Skill") and "blueprint-status" in what for kind, what in under_way.steps)
        check("a project under way: the status skill was called from the plain question", called)
        check("a project under way: says the project is at the requirements", has(under_way.reply, ("requisit",)))
        check("a project under way: gives the next question from the state", has(under_way.reply, ("deu certo",)))
        check("a project under way: names the decision taken", has(under_way.reply, ("d-001", "aplicativo web")))
        check(
            "a project under way: reports the ready document that does not exist",
            has(under_way.reply, ("system-description", "descrição do sistema"), ("não existe", "não encontr", "falta", "ausente", "não está", "inexist", "sumiu")),
        )
        check("no project: says there is no Blueprint project here", has(none.reply, ("não encontr", "nenhum projeto", "não há", "não existe", "não tem")))
        changed = sorted(set(was) ^ set(now)) + sorted(name for name in set(was) & set(now) if was[name] != now[name])
        print()
        check("no session created, changed or deleted a file", not changed, ", ".join(changed))
    check("nothing under skills/ changed in this repository", skills_changes() == before)
    print("\n" + spent([under_way, none]))

    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
