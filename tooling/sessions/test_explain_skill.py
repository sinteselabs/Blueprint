#!/usr/bin/env python3
"""
Runs the blueprint-explain skill in two real Claude Code sessions and measures the
one thing the comprehension layer exists for: a developer asks why a line of code
is the way it is, and gets the answer without being sent to read a document.

| Case | The line asked about | What must happen |
|---|---|---|
| anchored | `src/cancelar.js`, where the code carries `FR-01` | Names the requirement and says what it requires, and never tells the person to go read a document |
| orphaned | `src/legado.js`, which carries `FR-99`, an id no document has | Says that no document says it, and invents no reason |

The second case is the one that matters most: it is where a model is tempted to
make up a plausible purpose. A layer that invents reasons is worse than no layer.

Each session is new, and the person asks in plain words, so the answer can only
come from the files. The reply is printed in full for a person to read.

It needs Claude Code and Node on the PATH, takes a couple of minutes and spends
model usage, so it is not one of the checks to run before every change. Run it
after changing the explain skill or its engine:

    python tooling/sessions/test_explain_skill.py

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not
run at all.
"""

import hashlib
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, find_claude, refused, run, skills_changes, spent, verdict

EXAMPLE_STATE = REPO / "skills" / "blueprint-record" / "assets" / "state.example.md"

REQUIREMENTS = """# Requisitos

## Requisitos funcionais

| Nº | Requisito | Prioridade | Vem de |
|---|---|---|---|
| FR-01 | A recepção cancela uma consulta, e só a recepção | Primeira versão | o que a pessoa disse |
| FR-02 | O paciente confirma a presença pelo aviso | Primeira versão | o que a pessoa disse |

## Requisitos não funcionais

| Nº | Requisito | Prioridade | Vem de |
|---|---|---|---|
| NFR-01 | A lista de consultas abre em menos de 2 segundos | Primeira versão | deduzido |
"""

DECISIONS = """# Decisões

## D-001 · Aplicativo web em vez de aplicativo de celular

- **Decisão:** aplicativo web.
- **Por quê:** a recepção usa só o navegador do computador.
- **Situação:** decidida
"""

CANCEL = """// FR-01: só a recepção cancela uma consulta.
export function cancelarConsulta(id, quem) {
  if (quem.papel !== "recepcao") throw new Error("não permitido");
  return { id, cancelada: true };
}
"""

LEGACY = """// FR-99
export function reordenarFila(fila) {
  return fila.slice().reverse();
}
"""

ASKS = {
    "anchored": "Por que a linha 3 de src/cancelar.js é assim?",
    "orphaned": "Por que a linha 3 de src/legado.js é assim?",
}


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def snapshot(folder: Path) -> dict[str, str]:
    """Every file under the folder with a digest of its content, to tell whether anything changed."""
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()}


def project(at: Path) -> Path:
    put(at / ".blueprint" / "state.md", EXAMPLE_STATE.read_text(encoding="utf-8"))
    put(at / ".blueprint" / "journal" / "sessions" / "2026-10-09-1500-claude-code.md", "# Sessão 2026-10-09 15:00 · Claude Code\n\n## Pedido\n\nComeçar o projeto.\n")
    put(at / "docs" / "system-description.md", "# Descrição do sistema\n\n> **Em resumo:** a clínica marca consultas por telefone.\n")
    put(at / "docs" / "requirements.md", REQUIREMENTS)
    put(at / "docs" / "research.md", "# Pesquisa\n\n> **Em resumo:** em andamento.\n")
    put(at / "docs" / "decisions.md", DECISIONS)
    put(at / "src" / "cancelar.js", CANCEL)
    put(at / "src" / "legado.js", LEGACY)
    return at


def has(reply: str, *groups: tuple[str, ...]) -> bool:
    low = reply.lower()
    return all(any(word in low for word in group) for group in groups)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    claude = find_claude()
    if not claude:
        print("cannot find Claude Code on the PATH; this test runs real sessions with it")
        return 2
    if not shutil.which("node"):
        print("cannot find Node on the PATH; the explain skill carries a script and the sessions have to run it")
        return 2
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    before = skills_changes()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True, prefix="blueprint explain é ") as folder:
        root = Path(folder)
        folders = {name: project(root / name / "agenda-clinica") for name in ASKS}
        was = snapshot(root)

        print("running 2 sessions at once ...", flush=True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = dict(zip(ASKS, pool.map(
                lambda name: run(claude, folders[name], ASKS[name], (root / name,), web=False, extra_tools=("Bash(node *)",)),
                ASKS,
            )))
        now = snapshot(root)
        stopped = [refused(s) for s in replies.values() if refused(s)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of 2 sessions: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        for name, session in replies.items():
            print(f"\n--- {name}\n    the person: {ASKS[name]}\n    the agent:", flush=True)
            for line in session.reply.splitlines():
                print("      " + line)
            check(f"{name}: the session ran", session.code == 0, f"exit {session.code}")

        anchored, orphaned = replies["anchored"], replies["orphaned"]

        called = any(kind == "tool" and what.startswith("Skill") and "blueprint-explain" in what for kind, what in anchored.steps)
        check("anchored: the explain skill was called from the plain question", called)
        check("anchored: names the requirement the code serves", has(anchored.reply, ("fr-01",)))
        check("anchored: says what that requirement requires", has(anchored.reply, ("recepção", "recepcao")), anchored.reply[:120])
        # The whole point: the answer arrives without sending the person to a document.
        check(
            "anchored: does not tell the person to go read a document",
            not has(anchored.reply, ("leia o", "leia a", "consulte o documento", "veja o documento", "abra o documento", "leia os requisitos")),
        )
        ran = [what for kind, what in anchored.steps if kind == "tool" and "explain.js" in what]
        print(f"      (the engine was run {len(ran)} time(s))")

        check("orphaned: says no document says that id", has(orphaned.reply, ("fr-99",), ("nenhum documento", "não está em nenhum", "não aparece em nenhum", "não há documento", "órf", "orf", "nenhum requisito", "não encontrei", "não existe")))
        # A layer that invents a purpose is worse than no layer. What proves it did not
        # is that it says the reason is recorded nowhere. Listing the requirements that
        # do exist, to show this id is not among them, is the right answer, not invention.
        check(
            "orphaned: says the reason is recorded nowhere, instead of supplying one",
            has(orphaned.reply, ("não está escrito", "nao esta escrito", "não registra", "nao registra", "não há registro", "nada no projeto", "não vou inventar", "nao vou inventar", "em lugar nenhum", "não documentado")),
            orphaned.reply[:160],
        )

        changed = sorted(set(was) ^ set(now)) + sorted(name for name in set(was) & set(now) if was[name] != now[name])
        print()
        check("no session created, changed or deleted a file", not changed, ", ".join(changed))
    check("nothing under skills/ changed in this repository", skills_changes() == before)
    print("\n" + spent(list(replies.values())))

    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
