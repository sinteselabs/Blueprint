#!/usr/bin/env python3
"""
Runs the blueprint skill's "continue" path in real Claude Code sessions, on a
project that stopped in the middle of its first step.

| Case | The folder | What must happen |
|---|---|---|
| stopped mid-step | A state with three of the four main questions of the system description answered, and the fourth as the next question | The first message says where the project is and asks the fourth question, without asking again what is answered. With the answer, the step closes, its document is written, and the conversation moves to the requirements |
| the state is behind | The same state, but the document is already written and the session record says the answer was given: the session ended before saving | Says the state is behind, shows what it rebuilt from the files, asks to confirm, and does not touch the state before that |

Every session is new: the agent has only the files. The words of a reply are a
rough check, and each reply is printed in full for a person to read.

It needs Claude Code on the PATH, takes a few minutes and spends model usage,
so it is not one of the checks to run before every change. Run it after
changing how the blueprint skill continues a project:

    python tooling/sessions/test_continue.py

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not
run at all.
"""

import hashlib
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, Session, find_claude, refused, run, skills_changes, spent

sys.path.insert(0, str(REPO / "tooling" / "checks"))
import check_state  # noqa: E402  (the same reader the gate uses)

HERE = Path(__file__).resolve().parent
STATE = (HERE / "entry" / "padaria-pedidos-state.md").read_text(encoding="utf-8")
POSITION = re.compile(r"^[\W_]*etapa\s+(\d)\s+de\s+5", re.IGNORECASE)
ASKED_AGAIN = ("que problema", "para quem", "quer conseguir", "como ele chega", "como o site chega")
SESSION_LEFT_OPEN = """# Sessão 2026-10-09 15:51 · Claude Code

- **Início:** 2026-10-09T15:51:07Z
- **Fim:** 2026-10-09T15:52:12Z

## Pedido

Começar o projeto padaria-pedidos.

## Feito

Primeiro bloco da descrição do sistema respondido: três das quatro perguntas principais.

## Decidido

Nada.

## Ficou em aberto

Falta a quarta pergunta principal: o que fica fora da primeira versão.
"""
SESSION_NOT_SAVED = """# Sessão 2026-10-09 17:10 · Claude Code

- **Início:** 2026-10-09T17:10:02Z
- **Fim:** 2026-10-09T17:14:40Z

## Pedido

Continuar o projeto padaria-pedidos.

## Feito

A pessoa respondeu a quarta pergunta da descrição do sistema: fora da primeira
versão fica o pagamento online, porque o cliente paga na retirada. Escrevi
`docs/system-description.md`.

## Decidido

Nada.

## Ficou em aberto

A sessão terminou antes de gravar o estado: `.blueprint/state.md` ainda mostra a
descrição do sistema com três de quatro perguntas e o documento como não começado.
"""
DOCUMENT = """# Descrição do sistema

**Projeto:** padaria-pedidos · **Versão:** 0.1 · **Data:** 2026-10-09

> **Em resumo:** um site onde o cliente da padaria faz a encomenda e a padaria vê a lista do dia. A primeira versão não tem pagamento online.

## O que é

Um site de encomendas para a padaria, no lugar do WhatsApp.

## Escopo

- **Na primeira versão:** a encomenda pelo site e a lista do dia.
- **Fora da primeira versão:** pagamento online. O cliente paga na retirada.
"""


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_line(reply: str) -> str:
    return next((line.strip() for line in reply.splitlines() if line.strip()), "")


def has(reply: str, *groups: tuple[str, ...]) -> bool:
    low = reply.lower()
    return all(any(word in low for word in group) for group in groups)


def step_of(project: Path, step: str) -> str:
    lines = (project / ".blueprint" / "state.md").read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    _, start = check_state.header(lines, problems)
    found = check_state.sections(lines, start, problems)
    rows = check_state.table(found.get("Steps", []), ["Step", "Situation", "Main questions"], "Steps", problems)
    return next((f"{row[1]} {row[2]}" for row in rows if row[0] == step), "missing")


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

    def show(name: str, said: str, session: Session) -> None:
        print(f"\n--- {name}\n    the person: {said}\n    the agent:", flush=True)
        for line in session.reply.splitlines():
            print("      " + line)

    before = skills_changes()
    with tempfile.TemporaryDirectory(prefix="blueprint continue é ") as folder:
        root = Path(folder)
        stopped = root / "a" / "projetos" / "padaria-pedidos"
        put(stopped / ".blueprint" / "state.md", STATE)
        put(stopped / ".blueprint" / "journal" / "sessions" / "2026-10-09-1551-claude-code.md", SESSION_LEFT_OPEN)
        behind = root / "b" / "projetos" / "padaria-pedidos"
        put(behind / ".blueprint" / "state.md", STATE)
        put(behind / ".blueprint" / "journal" / "sessions" / "2026-10-09-1551-claude-code.md", SESSION_LEFT_OPEN)
        put(behind / ".blueprint" / "journal" / "sessions" / "2026-10-09-1710-claude-code.md", SESSION_NOT_SAVED)
        put(behind / "docs" / "system-description.md", DOCUMENT)
        behind_state = digest(behind / ".blueprint" / "state.md")

        def mid_step() -> list[Session]:
            first = run(claude, stopped, "Vamos continuar.", (root / "a",), timeout=1200, keep=True, web=False)
            if first.code != 0 or refused(first) or not first.session_id:
                return [first]
            answer = "Fora da primeira versão fica o pagamento online: o cliente paga na retirada."
            return [first, run(claude, stopped, answer, (root / "a",), timeout=1200, resume=first.session_id, keep=True, web=False)]

        print("running the two cases at once: three turns in all ...", flush=True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            going = pool.submit(mid_step)
            late = pool.submit(lambda: run(claude, behind, "Vamos continuar.", (root / "b",), timeout=1200, web=False))
            turns, stale = going.result(), late.result()
        refusals = [refused(s) for s in turns + [stale] if refused(s)]
        if refusals:
            print(f"could not run: Claude Code refused a session: {refusals[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        show("stopped mid-step, turn 1", "Vamos continuar.", turns[0])
        check("stopped mid-step: the session ran", turns[0].code == 0, f"exit {turns[0].code}")
        match = POSITION.match(first_line(turns[0].reply))
        check("stopped mid-step: the first message opens with the step the project is in", bool(match) and match.group(1) == "1", first_line(turns[0].reply)[:80])
        check("stopped mid-step: it asks the question the state has as next", has(turns[0].reply, ("fora da primeira versão", "fica de fora", "fica fora")))
        questions = [line.lower() for line in turns[0].reply.splitlines() if "?" in line]
        again = [line.strip()[:70] for line in questions if any(words in line for words in ASKED_AGAIN)]
        check("stopped mid-step: it does not ask again what is already answered", not again, "; ".join(again))
        if len(turns) > 1:
            show("stopped mid-step, turn 2", "Fora da primeira versão fica o pagamento online: o cliente paga na retirada.", turns[1])
            check("stopped mid-step: the second turn ran", turns[1].code == 0, f"exit {turns[1].code}")
            state = stopped / ".blueprint" / "state.md"
            passes = subprocess.run([sys.executable, str(REPO / "tooling" / "checks" / "check_state.py"), str(state)], capture_output=True, text=True, encoding="utf-8")
            check("stopped mid-step: the state passes check_state.py after the answer", passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])
            now = step_of(stopped, "system-description")
            check("stopped mid-step: the step has four of four and moved on", now in ("closed 4 of 4", "advanced 4 of 4"), now)
            check("stopped mid-step: the step's document was written", (stopped / "docs" / "system-description.md").is_file())
            match = POSITION.match(first_line(turns[1].reply))
            check("stopped mid-step: the conversation moved to the requirements", bool(match) and match.group(1) == "2", first_line(turns[1].reply)[:80])
        else:
            check("stopped mid-step: the second turn ran", False, "the first turn did not leave a session to continue")

        show("the state is behind", "Vamos continuar.", stale)
        check("the state is behind: the session ran", stale.code == 0, f"exit {stale.code}")
        check(
            "the state is behind: it says the state does not have what the files show",
            has(stale.reply, ("desatualiz", "atrasad", "não bate", "não registr", "para trás", "incomplet", "diverg", "não foi salv", "não foi grav", "não chegou a", "antes de gravar", "antes de salvar", "defasad")),
        )
        check("the state is behind: it shows what it rebuilt, marked as rebuilt", has(stale.reply, ("reconstru",)))
        check("the state is behind: it names the document it rebuilt from", has(stale.reply, ("system-description", "descrição do sistema")))
        check("the state is behind: it asks the person to confirm", "?" in stale.reply)
        check("the state is behind: the state file was not touched before the person confirmed", digest(behind / ".blueprint" / "state.md") == behind_state)
    check("nothing under skills/ changed in this repository", skills_changes() == before)
    print("\n" + spent(turns + [stale]))

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
