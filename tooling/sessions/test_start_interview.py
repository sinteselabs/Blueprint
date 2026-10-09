#!/usr/bin/env python3
"""
Runs a whole interview of a new project with the blueprint skill, in one real
Claude Code session of several turns, and checks what it left on disk.

The person is scripted: a bakery owner who wants a site to take orders, writes
in Portuguese, has no budget, and never approves a document. Each of her turns
answers a block and ends by telling the agent to decide small things itself.
When her script ends and the plan is not closed yet, she says "go on with what
you recommend" until it is, up to a limit of turns. Her last turn asks where
things are.

What is checked afterwards:

- the state passes check_state.py, with the system description, requirements,
  architecture and plan closed, and the modeling advanced;
- the six fixed documents are ready, exist where the state says, are written in
  Portuguese, and carry no leftover of their templates;
- the plan has a spec per task, each with how to test it;
- every message of the interview opened by saying where the conversation was;
- the agent used the blueprint-record skill, wrote nothing outside the project
  and changed nothing in this repository.

Every reply is printed, because a person reading the conversation is the real
check. It needs Claude Code on the PATH, takes about twenty minutes and spends
model usage, so it is not one of the checks to run before every change:

    python tooling/sessions/test_start_interview.py [--save FILE]

`--save` keeps what the agent said and did in every turn. Exit code 0 when
every check passes, 1 otherwise, 2 when the session could not run at all.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from harness import REPO, find_claude, refused, run, skills_changes

sys.path.insert(0, str(REPO / "tooling" / "checks"))
import check_state  # noqa: E402  (the same reader the gate uses)

DECIDE = " Se faltar algum detalhe, decida você e me avise."
SCRIPT = [
    "Quero começar um projeto novo: um site para a padaria receber encomendas.",
    "Isso, é um projeto novo. Pode começar aqui nesta pasta.",
    "Os documentos em português, e só eu desenvolvo. Sobre o sistema: a padaria recebe encomendas pelo WhatsApp e perde "
    "pedidos. Quero que o cliente faça a encomenda num site e a padaria veja a lista do dia. Quem usa é o cliente e a "
    "atendente da padaria. Fora da primeira versão fica o pagamento online: o cliente paga na retirada. Não tenho verba "
    "para serviço pago." + DECIDE,
    "O cliente escolhe os produtos, a data de retirada e deixa nome e telefone. A atendente vê a lista de encomendas do "
    "dia e marca cada uma como pronta ou retirada. Os limites: não tenho verba, precisa funcionar bem no celular do "
    "cliente, e quero no ar em um mês. Vou saber que deu certo se em um mês nenhuma encomenda se perder." + DECIDE,
    "O que não pode dar errado: o cliente conseguir fazer a encomenda, e a atendente ver a lista do dia. O sistema guarda "
    "os produtos, as encomendas e o nome e o telefone do cliente. As telas principais são o catálogo, a tela de fazer a "
    "encomenda e a lista do dia." + DECIDE,
    "Não entendo de tecnologia. Aceito as suas recomendações em todas as decisões de arquitetura, desde que seja tudo gratuito.",
    "Primeiro a encomenda pelo cliente, depois a lista da atendente. Sou só eu que faço tudo. Pode fechar o plano.",
]
GO_ON = "Pode seguir com o que você recomendar." + DECIDE
WHERE = "Onde estamos?"
MAX_TURNS = 11
CLOSED = ["system-description", "requirements", "architecture", "plan"]
ENGLISH_TITLES = {"system description", "requirements", "research", "architecture", "plan", "decisions"}
POSITION = re.compile(r"^[\W_]*etapa\s+\d\s+de\s+5", re.IGNORECASE)


def read_state(project: Path) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    """The situation of each step, and the situation and place of each document, from the state file."""
    path = project / ".blueprint" / "state.md"
    if not path.is_file():
        return {}, {}
    lines = path.read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    _, start = check_state.header(lines, problems)
    found = check_state.sections(lines, start, problems)
    steps = {row[0]: row[1] for row in check_state.table(found.get("Steps", []), ["Step", "Situation", "Main questions"], "Steps", problems)}
    documents = {row[0]: (row[1], row[2]) for row in check_state.table(found.get("Documents", []), ["Document", "Situation", "Where"], "Documents", problems)}
    return steps, documents


def first_line(reply: str) -> str:
    return next((line.strip() for line in reply.splitlines() if line.strip()), "")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    arguments = sys.argv[1:]
    save = Path(arguments[1]) if arguments[:1] == ["--save"] and len(arguments) > 1 else None
    claude = find_claude()
    if not claude:
        print("cannot find Claude Code on the PATH; this test runs a real session with it")
        return 2
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    before = skills_changes()
    with tempfile.TemporaryDirectory(prefix="blueprint interview é ") as folder:
        around = Path(folder) / "caso"
        project = around / "projetos" / "padaria-pedidos"
        project.mkdir(parents=True)
        turns: list[tuple[str, object]] = []

        def say(text: str) -> bool:
            """One turn of the person. False when the session could not go on."""
            resume = turns[-1][1].session_id if turns else ""
            session = run(claude, project, text, (around,), timeout=1500, resume=resume, keep=True)
            turns.append((text, session))
            number = len(turns)
            print(f"\n=== turn {number}\n    the person: {text}\n    the agent:", flush=True)
            for line in session.reply.splitlines():
                print("      " + line)
            if save:
                kept = [{"said": said, "code": s.code, "reply": s.reply, "steps": s.steps} for said, s in turns]
                save.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
            return session.code == 0 and not refused(session) and bool(session.session_id)

        alive = True
        for text in SCRIPT:
            alive = say(text)
            if not alive:
                break
        while alive and len(turns) < MAX_TURNS - 1 and read_state(project)[0].get("plan") != "closed":
            alive = say(GO_ON)
        interview_turns = len(turns)
        if alive:
            alive = say(WHERE)

        stopped = next((refused(s) for _, s in turns if refused(s)), None)
        if stopped:
            print(f"\ncould not run: Claude Code refused a turn: {stopped}")
            print("the interview was not completed; run this again when the limit resets")
            return 2

        print("\n=== what the interview left", flush=True)
        check("every turn ran", alive, f"stopped at turn {len(turns)}")
        state = project / ".blueprint" / "state.md"
        passes = state.is_file() and subprocess.run([sys.executable, str(REPO / "tooling" / "checks" / "check_state.py"), str(state)], capture_output=True, text=True, encoding="utf-8")
        check("the state passes check_state.py", bool(passes) and passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no state file"])[0] if passes else "no state file")
        steps, documents = read_state(project)
        for step in CLOSED:
            check(f"the step {step} is closed", steps.get(step) == "closed", steps.get(step, "missing"))
        check("the modeling step is advanced, its documents not being written yet", steps.get("modeling") in ("advanced", "closed"), steps.get("modeling", "missing"))

        written: dict[str, Path] = {}
        for name in ("system-description", "requirements", "research", "architecture", "decisions", "plan"):
            situation, where = documents.get(name, ("missing", "-"))
            path = project / where
            ok = situation == "ready" and where != "-" and path.is_file()
            check(f"the document {name} is ready and exists where the state says", ok, f"{situation}, {where}")
            if ok:
                written[name] = path
        leftovers = [p.name for p in written.values() if "{{" in p.read_text(encoding="utf-8") or "<!--" in p.read_text(encoding="utf-8")]
        check("no document carries a leftover of its template", not leftovers, ", ".join(leftovers))
        english = []
        for name, path in written.items():
            title = next((line[2:].strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("# ")), "")
            if title in ENGLISH_TITLES:
                english.append(f"{path.name}: {title}")
        check("the documents are written in Portuguese, titles included", bool(written) and not english, "; ".join(english))

        specs = sorted((written["plan"].parent / "specs").glob("*.md")) if "plan" in written else []
        check("the plan has a spec per task", len(specs) >= 2, f"{len(specs)} spec files")
        without = [p.name for p in specs if "como testar" not in p.read_text(encoding="utf-8").lower()]
        check("every spec says how to test the task", bool(specs) and not without, ", ".join(without))

        interview = [s.reply for _, s in turns[2:interview_turns]]
        opened = [reply for reply in interview if POSITION.match(first_line(reply))]
        check("every message of the interview opened with where the conversation was", bool(interview) and len(opened) == len(interview), f"{len(opened)} of {len(interview)}")
        used = sum(1 for _, s in turns for kind, what in s.steps if kind == "tool" and what.startswith("Skill") and "blueprint-record" in what)
        check("the agent used the blueprint-record skill", used > 0, "it never called it")
        check("the answer to 'where are we?' names the plan", "plano" in turns[-1][1].reply.lower())
        outside = sorted(p.name for p in around.rglob("*") if project not in p.parents and p != project and p != around / "projetos")
        check("nothing was written beside the project folder", not outside, ", ".join(outside))
        print(f"\n{len(turns)} turns; blueprint-record called {used} times; steps: {steps}")
    check("nothing under skills/ changed in this repository", skills_changes() == before)

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
