#!/usr/bin/env python3
"""
Runs the blueprint-decide skill in real Claude Code sessions: one decision that
is costly to undo, brought to the person and answered in three ways.

The project is at the architecture step, with the hosting already researched
and nothing decided. In every case the person first says they want to decide
where to host, and the agent must present the decision: the recommendation
before the other options, four options at most, short, ending in a question,
and nothing recorded as decided yet. Then the person answers:

| Case | The answer | What must happen |
|---|---|---|
| takes the recommendation | "I go with your recommendation" | The decision is recorded with its reason, who decided, the date and the sources; what was left to verify becomes an item of the test plan |
| decides later | "I would rather decide this later" | The decision is recorded as open, the reply says what depends on it, and the rest goes on |
| chooses against it | Names another option, with a reason | That choice is recorded as the person's, and the agent does not insist |

The web is closed, so nothing is read: the research document already says so.
The words of a reply are a rough check, and each reply is printed in full for a
person to read.

It needs Claude Code on the PATH, takes a few minutes and spends model usage,
so it is not one of the checks to run before every change. Run it after
changing the decide skill:

    python tooling/sessions/test_decide_skill.py

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not
run at all.
"""

import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, Session, find_claude, refused, run, skills_changes, spent

HERE = Path(__file__).resolve().parent
STATE = (HERE / "decide" / "padaria-architecture-state.md").read_text(encoding="utf-8")
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
ASKS = "Preciso decidir onde hospedar o site e o banco de dados. A pesquisa já está em docs/research.md."
OPTIONS = ("cloudflare", "supabase", "firebase")
GRADES_ITSELF = (
    "recomendação fraca", "recomendação frágil", "recomendação incerta", "recomendação é fraca", "recomendação é frágil",
    "pouca confiança", "baixa confiança", "não tenho certeza", "inconclusiv", "testar antes de decidir", "teste antes de decidir",
    "faça um teste antes", "recomendo testar antes",
)
INSISTS = ("tem certeza", "reconsider", "ainda recomendo", "mesmo assim recomendo", "insisto", "sugiro repensar", "recomendo repensar")
DECISION = re.compile(r"^- D-001 · .* · (\S+)\s*$", re.MULTILINE)
RESEARCH = """# Pesquisa

**Projeto:** padaria-pedidos · **Versão:** 0.1 · **Data:** 2026-10-09

> **Em resumo:** uma pergunta pesquisada, a hospedagem. A recomendação é a Cloudflare, e a escolha ainda está em aberto. Nenhuma fonte pôde ser lida na sessão: o acesso à internet estava bloqueado.

## Onde hospedar o site e o banco de dados sem pagar nada

- **Decisão:** em aberto. A recomendação é a Cloudflare, com o site em Workers e os dados no banco D1.
- **Motivo:** os critérios declarados são "sem verba" e "nenhuma encomenda se perder". É a opção que põe site e banco no mesmo plano gratuito, sem pausa por falta de uso.
- **Alternativas:**

| Opção | O que dá | O que custa | Por que ficou de fora |
|---|---|---|---|
| Cloudflare Workers + D1 | Site e banco num plano gratuito só, que não pausa | Banco mais simples (SQLite). Endereço gratuito termina em `workers.dev` | Recomendada |
| Supabase + páginas em outro serviço gratuito | Banco Postgres e login pronto | O projeto gratuito é pausado depois de uma semana sem uso. Dois serviços para cuidar | Site pausado não recebe encomenda |
| Firebase, plano gratuito | Banco e páginas num plano que não pausa | Código de servidor exige o plano pago | O site precisa de código de servidor para proteger nome e telefone |

- **Fontes:** nenhuma lida nesta sessão. A conferir, todas oficiais:
  - `https://developers.cloudflare.com/workers/platform/pricing/`
  - `https://developers.cloudflare.com/d1/platform/pricing/`
  - `https://supabase.com/pricing`
  - `https://firebase.google.com/pricing`

## Não verificado

- Os limites do plano gratuito da Cloudflare (Workers e D1), e se ele aceita uso comercial.
"""
CASES = [
    {"name": "takes the recommendation", "folder": "a", "answer": "Vou com a sua recomendação."},
    {"name": "decides later", "folder": "b", "answer": "Prefiro decidir isso depois. Pode seguir com o resto."},
    {"name": "chooses against it", "folder": "c", "answer": "Prefiro o Supabase: já uso em outro projeto e conheço bem."},
]


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def has(reply: str, *groups: tuple[str, ...]) -> bool:
    low = reply.lower()
    return all(any(word in low for word in group) for group in groups)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


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
    with tempfile.TemporaryDirectory(prefix="blueprint decide é ") as folder:
        root = Path(folder)
        for case in CASES:
            project = case["path"] = root / case["folder"] / "projetos" / "padaria-pedidos"
            put(project / ".blueprint" / "state.md", STATE)
            put(project / "docs" / "research.md", RESEARCH)
            put(project / "docs" / "system-description.md", "# Descrição do sistema\n\n> **Em resumo:** um site onde o cliente da padaria faz a encomenda e a atendente vê a lista do dia.\n")
            put(project / "docs" / "requirements.md", "# Requisitos\n\n> **Em resumo:** o cliente encomenda pelo celular, sem conta; a atendente vê a lista do dia. Nada pode ser pago.\n")

        def both(case: dict) -> list[Session]:
            around = (root / case["folder"],)
            first = run(claude, case["path"], ASKS, around, timeout=1200, keep=True, web=False)
            case["decided_early"] = DECISION.findall(read(case["path"] / ".blueprint" / "state.md"))
            if first.code != 0 or refused(first) or not first.session_id:
                return [first]
            return [first, run(claude, case["path"], case["answer"], around, timeout=1200, resume=first.session_id, keep=True, web=False)]

        print(f"running {len(CASES)} cases at once, two turns each ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(CASES)) as pool:
            results = list(pool.map(both, CASES))
        every = [turn for turns in results for turn in turns]
        stopped = [refused(s) for s in every if refused(s)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of {len(every)} turns: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        for case, turns in zip(CASES, results):
            name, project = case["name"], case["path"]
            first = turns[0]
            print(f"\n--- {name}, turn 1\n    the person: {ASKS}\n    the agent:", flush=True)
            for line in first.reply.splitlines():
                print("      " + line)
            low = first.reply.lower()
            lines = [line for line in first.reply.splitlines() if line.strip()]
            named = [option for option in OPTIONS if option in low]
            others = [low.find(option) for option in named if option != "cloudflare"]
            print(f"    {len(lines)} lines; options named: {', '.join(named) or 'none'}", flush=True)
            check(f"{name}: the first turn ran", first.code == 0, f"exit {first.code}")
            check(f"{name}: the decide skill was called", any(kind == "tool" and what.startswith("Skill") and "blueprint-decide" in what for turn in turns for kind, what in turn.steps))
            check(f"{name}: it presents the options, four at most, and recommends one", 2 <= len(named) <= 4 and "recomend" in low, f"{len(named)} options")
            check(f"{name}: the recommendation comes before the other options", "recomend" in low and bool(others) and low.find("recomend") < min(others))
            check(f"{name}: it says why the decision is costly to undo", has(first.reply, ("trocar depois", "mudar depois", "desfazer", "mover", "migrar", "refazer", "reescrever")))
            check(f"{name}: the message is short", len(lines) <= 16, f"{len(lines)} lines")
            check(f"{name}: it asks, and waits for the person", "?" in first.reply)
            check(f"{name}: nothing is recorded as decided before the person answers", "decided" not in case["decided_early"], ", ".join(case["decided_early"]))
            if len(turns) < 2:
                check(f"{name}: the second turn ran", False, "the first turn did not leave a session to continue")
                continue
            second = turns[1]
            print(f"\n--- {name}, turn 2\n    the person: {case['answer']}\n    the agent:", flush=True)
            for line in second.reply.splitlines():
                print("      " + line)
            check(f"{name}: the second turn ran", second.code == 0, f"exit {second.code}")
            graded = [words for turn in turns for words in GRADES_ITSELF if words in turn.reply.lower()]
            check(f"{name}: it does not call its recommendation weak or ask for a test before deciding", not graded, ", ".join(graded))
            state = project / ".blueprint" / "state.md"
            passes = subprocess.run([sys.executable, str(CHECK_STATE), str(state)], capture_output=True, text=True, encoding="utf-8")
            check(f"{name}: the state passes check_state.py", passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])
            case["record"] = read(project / "docs" / "decisions.md")
            case["situation"] = (DECISION.findall(read(state)) or ["missing"])[-1]
            check(f"{name}: the decision is in the decisions record, as D-001", "D-001" in case["record"])
            check(
                f"{name}: the entry has the reason, the alternatives, who decided, the date and the sources",
                has(case["record"], ("motivo",), ("alternativa",), ("decidido por", "decidida por", "quem decidiu"), ("data",), ("fonte",)) and bool(re.search(r"20\d\d-\d\d-\d\d", case["record"])),
            )

        taken, later, against = CASES
        check("takes the recommendation: the state has the decision as decided", taken.get("situation") == "decided", str(taken.get("situation")))
        check("takes the recommendation: the recorded decision is the recommended option", "cloudflare" in taken.get("record", "").lower())
        plan = read(taken["path"] / "docs" / "test-plan.md")
        check("takes the recommendation: what was left to verify is an item of the test plan", "T-001" in plan and "D-001" in plan, "no docs/test-plan.md" if not plan else "no T-001 from D-001")
        check("takes the recommendation: the test plan carries no leftover of its template", bool(plan) and "{{" not in plan and "<!--" not in plan)

        check("decides later: the state has the decision as open", later.get("situation") == "open", str(later.get("situation")))
        check("decides later: the reply says what depends on the decision", len(results[1]) > 1 and has(results[1][1].reply, ("depend", "espera", "aguarda")))
        check("decides later: the reply goes on with something else", len(results[1]) > 1 and "?" in results[1][1].reply)

        check("chooses against it: the state has the decision as decided", against.get("situation") == "decided", str(against.get("situation")))
        check("chooses against it: the recorded decision is the person's choice", "supabase" in against.get("record", "").lower().split("alternativa")[0])
        insisted = [words for words in INSISTS if len(results[2]) > 1 and words in results[2][1].reply.lower()]
        check("chooses against it: the agent does not insist", len(results[2]) > 1 and not insisted, ", ".join(insisted))
    check("nothing under skills/ changed in this repository", skills_changes() == before)
    print("\n" + spent(every))

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
