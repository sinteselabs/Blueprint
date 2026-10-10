#!/usr/bin/env python3
"""
Runs the blueprint-setup skill in real Claude Code sessions: a project whose
plan is closed and whose repository is not prepared yet.

| Case | The project | What must happen |
|---|---|---|
| one person | `AGENTS.md` already exists, with the person's own rules | The Blueprint block is added, the person's rules are untouched, `CLAUDE.md` points at `AGENTS.md`, and no playbook is created |
| a team | No `AGENTS.md`, and the state says two people develop | The file is created with the block alone, and there is a playbook per role |
| going on after the plan | No `AGENTS.md`, and the person says "let's go on" | The repository is prepared first, before the first task, and the reply says why |

Then the acceptance of a prepared repository (FR-30): a new session in the
project of the first case, **without Blueprint loaded**, is told to start the
first task. A bare agent has only the files, so what it knows comes from the
entry file. It must name the task, where the task is written and where it
records what it does.

The web is closed. The words of a reply are a rough check, and each reply is
printed in full for a person to read. It needs Claude Code on the PATH, takes
a few minutes and spends model usage, so it is not one of the checks to run
before every change. Run it after changing the setup skill:

    python tooling/sessions/test_setup_skill.py [--folder DIR]

With `--folder`, the projects are kept in DIR, which must not exist yet. Exit
code 0 when every case passes, 1 otherwise, 2 when the sessions could not run.
"""

import hashlib
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, find_claude, refused, run, skills_changes, spent, verdict

HERE = Path(__file__).resolve().parent
STATE = (HERE / "setup" / "padaria-plan-closed-state.md").read_text(encoding="utf-8")
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
START, END = "<!-- blueprint:start -->", "<!-- blueprint:end -->"
OWN_RULES = """# O projeto

Site de encomendas da padaria.

## Regras da casa

- Mensagens de commit em português, no imperativo.
- Nada de dependência nova sem me perguntar.
- O preço é guardado em centavos, sempre.
"""
PLAN = """# Plano

**Projeto:** padaria-pedidos · **Versão:** 0.1 · **Data:** 2026-10-10

> **Em resumo:** duas fases e quatro tarefas. Primeiro a encomenda pelo cliente, depois a lista da atendente.

## Como o trabalho corre

- Uma tarefa por vez, na ordem abaixo.
- Toda tarefa entregue diz como testar: o que rodar ou abrir, e o que deve aparecer.
{quem}

## Fases

| Fase | O que entrega | Pronta quando |
|---|---|---|
| 1 · A encomenda | O cliente faz a encomenda e recebe a confirmação | Uma encomenda feita no celular aparece no banco |
| 2 · A lista do dia | A atendente vê e marca as encomendas | A encomenda feita na fase 1 aparece na lista e pode ser marcada |

## Tarefas

### Fase 1 · A encomenda

1. Base e página publicada: o projeto sobe na Cloudflare com uma página vazia. Spec: `specs/01-01-base-e-pagina.md`
2. Tela de encomenda: o cliente escolhe produtos, data, nome e telefone. Spec: `specs/01-02-tela-de-encomenda.md`

### Fase 2 · A lista do dia

1. Entrada com senha: a área da padaria abre com uma senha só. Spec: `specs/02-01-entrada-com-senha.md`
2. Lista do dia: a atendente vê as encomendas do dia e marca pronta ou retirada. Spec: `specs/02-02-lista-do-dia.md`

## O que depende de pessoas

- Criar a conta gratuita na Cloudflare, escolher a senha da padaria e passar a lista de produtos e preços.
"""
SPEC = """# {title}

**Fase:** {phase} · **Situação:** não iniciada

## O que faz

{does}

## O que não faz

{not_does}

## Pronta quando

- [ ] {done}

## Vem de

{comes}

## Como testar

A escrever na entrega.
"""
SPECS = {
    "01-01-base-e-pagina.md": dict(title="Base e página publicada", phase="1 · A encomenda", does="O projeto do site existe e uma página vazia está publicada no endereço gratuito da Cloudflare.", not_does="Nenhuma tela de verdade, nenhum banco.", done="A página abre no celular, fora da rede de quem desenvolve.", comes="D-001, D-002."),
    "01-02-tela-de-encomenda.md": dict(title="Tela de encomenda", phase="1 · A encomenda", does="O cliente escolhe produtos e quantidade, a data de retirada, e deixa nome e telefone.", not_does="Sem pagamento online, sem conta de cliente.", done="Uma encomenda feita numa tela de 360 px é gravada no banco.", comes="FR-01, D-002."),
    "02-01-entrada-com-senha.md": dict(title="Entrada com senha", phase="2 · A lista do dia", does="A área da padaria abre com uma senha única.", not_does="Sem usuário por pessoa, sem recuperação de senha.", done="A área não abre sem a senha e abre com ela.", comes="D-003."),
    "02-02-lista-do-dia.md": dict(title="Lista do dia", phase="2 · A lista do dia", does="A atendente vê as encomendas do dia de retirada e marca cada uma como pronta ou retirada.", not_does="Sem relatório, sem outros dias na primeira versão.", done="A encomenda da fase 1 aparece na lista e muda de situação.", comes="FR-03."),
}
DOCUMENTS = {
    "system-description.md": "# Descrição do sistema\n\n> **Em resumo:** um site onde o cliente da padaria faz a encomenda e a atendente vê a lista do dia.\n",
    "requirements.md": "# Requisitos\n\n> **Em resumo:** o cliente encomenda pelo celular, sem conta; a atendente vê a lista do dia. Nada pode ser pago.\n",
    "research.md": "# Pesquisa\n\n> **Em resumo:** uma pergunta pesquisada, a hospedagem. Nenhuma fonte foi lida na sessão.\n",
    "architecture.md": "# Arquitetura\n\n> **Em resumo:** site em Astro no Cloudflare Workers, dados no D1, tudo no plano gratuito.\n",
    "decisions.md": "# Decisões\n\n## D-001 · Hospedagem na Cloudflare\n\n- **Decisão:** site em Workers, banco no D1.\n- **Situação:** decidida\n",
    "test-plan.md": "# Plano de testes\n\n| # | O que verificar | Vem de | Como | Situação |\n|---|---|---|---|---|\n| T-001 | O plano gratuito da Cloudflare cobre site e banco | D-001 | Abrir as páginas de preço | a fazer |\n",
}
CASES = [
    {
        "name": "one person", "folder": "a", "developers": 1, "entry": OWN_RULES,
        "asks": "Os documentos e o plano estão prontos. Pode preparar o repositório para o desenvolvimento.",
    },
    {
        "name": "a team", "folder": "b", "developers": 2, "entry": None,
        "asks": "Pode preparar o ambiente para a gente começar a desenvolver.",
    },
    {
        "name": "going on after the plan", "folder": "c", "developers": 1, "entry": None,
        "asks": "Vamos continuar.",
    },
]
FIRST_TASK = ("01-01", "base e página", "base e pagina", "página publicada")
RECORDS = (".blueprint/journal", "journal/sessions", "diário", "diario", "registro da sessão", "state.md")
PREPARES = ("preparar", "preparo", "ambiente", "agents.md")


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def build(project: Path, case: dict) -> None:
    put(project / ".blueprint" / "state.md", STATE if case["developers"] == 1 else STATE.replace("developers: 1", "developers: 2"))
    for name, text in DOCUMENTS.items():
        put(project / "docs" / name, text)
    put(project / "docs" / "plan.md", PLAN.format(quem="- Uma pessoa desenvolve: não há divisão de papéis." if case["developers"] == 1 else "- Duas pessoas desenvolvem: quem constrói o site do cliente e quem constrói a área da padaria."))
    for name, parts in SPECS.items():
        put(project / "docs" / "specs" / name, SPEC.format(**parts))
    if case["entry"]:
        put(project / "AGENTS.md", case["entry"])


def snapshot(project: Path) -> dict[str, str]:
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(project.rglob("*")) if p.is_file()}


def has(text: str, *groups: tuple[str, ...]) -> bool:
    low = text.lower()
    return all(any(word in low for word in group) for group in groups)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def block(project: Path) -> str:
    """What the entry file has between the two marks, empty when it has none."""
    text = read(project / "AGENTS.md")
    if START not in text or END not in text:
        return ""
    return text.split(START, 1)[1].split(END, 1)[0]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    arguments = sys.argv[1:]
    kept = Path(arguments[1]).resolve() if arguments[:1] == ["--folder"] and len(arguments) > 1 else None
    if kept and kept.exists():
        print(f"{kept} already exists; give a folder that does not, so nothing of an earlier run is mixed in")
        return 2
    claude = find_claude()
    if not claude:
        print("cannot find Claude Code on the PATH; this test runs real sessions with it")
        return 2
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    before_skills = skills_changes()
    bare = None
    temporary = None if kept else tempfile.TemporaryDirectory(prefix="blueprint setup é ")
    root = kept or Path(temporary.name)
    try:
        for case in CASES:
            case["path"] = root / case["folder"] / "projetos" / "padaria-pedidos"
            build(case["path"], case)
            case["before"] = snapshot(case["path"])

        print(f"running {len(CASES)} cases at once ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(CASES)) as pool:
            results = list(pool.map(lambda c: run(claude, c["path"], c["asks"], (root / c["folder"],), timeout=1500, web=False), CASES))
        stopped = [refused(s) for s in results if refused(s)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of {len(results)} turns: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        for case, session in zip(CASES, results):
            name, project = case["name"], case["path"]
            print(f"\n--- {name}\n    the person: {case['asks']}\n    the agent:", flush=True)
            for line in session.reply.splitlines():
                print("      " + line)
            after = snapshot(project)
            case["new"] = sorted(set(after) - set(case["before"]))
            changed = sorted(path for path in case["before"] if after.get(path) != case["before"][path])
            print(f"    new: {', '.join(case['new']) or 'none'}; changed: {', '.join(changed) or 'none'}", flush=True)
            inside = block(project)
            case["block"] = inside

            check(f"{name}: the session ran", session.code == 0, f"exit {session.code}")
            check(f"{name}: the setup skill was called", any(kind == "tool" and what.startswith("Skill") and "blueprint-setup" in what for kind, what in session.steps))
            check(f"{name}: the entry file has the Blueprint block, between the two marks", bool(inside.strip()), "no AGENTS.md" if not read(project / "AGENTS.md") else "no marks")
            check(f"{name}: the block names the state file and the plan", has(inside, (".blueprint/state.md",), ("plan.md",)))
            check(f"{name}: the block says that every delivery says how to test", has(inside, ("como testar",)))
            check(f"{name}: the block says what a small change is, and what goes through a spec", has(inside, ("pequena", "pequeno"), ("spec",)))
            check(f"{name}: the block carries no leftover of its template", "{{" not in inside and "<!--" not in inside.replace(START, "").replace(END, ""))
            claude_md = read(project / "CLAUDE.md")
            check(f"{name}: CLAUDE.md names AGENTS.md", "AGENTS.md" in claude_md, "no CLAUDE.md" if not claude_md else "does not name it")
            journal = project / ".blueprint" / "journal"
            check(f"{name}: the project journal exists", journal.is_dir() and any(journal.rglob("*.md")))
            state = project / ".blueprint" / "state.md"
            passes = subprocess.run([sys.executable, str(CHECK_STATE), str(state)], capture_output=True, text=True, encoding="utf-8")
            check(f"{name}: the state still passes check_state.py", passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])
            check(f"{name}: the reply names the first task of the plan", has(session.reply, FIRST_TASK))
            check(f"{name}: no document of the project was rewritten", not [p for p in changed if p.startswith("docs/")], ", ".join(p for p in changed if p.startswith("docs/")))
            outside = sorted(p.name for p in (root / case["folder"]).rglob("*") if project not in p.parents and p != project and p != root / case["folder"] / "projetos")
            check(f"{name}: nothing was written beside the project folder", not outside, ", ".join(outside))
            playbooks = sorted(p.name for p in (project / "docs" / "playbooks").glob("*.md")) if (project / "docs" / "playbooks").is_dir() else []
            case["playbooks"] = playbooks

        one, team, going_on = CASES
        own = read(one["path"] / "AGENTS.md")
        check("one person: the person's own rules are untouched", OWN_RULES.strip() in own, "the file no longer holds them as they were")
        check("one person: the block was added after them, not in their place", own.find(OWN_RULES.strip()) < own.find(START))
        check("one person: no playbook was created, because one person develops", not one["playbooks"], ", ".join(one["playbooks"]))

        check("a team: the entry file was created by the skill", "AGENTS.md" in team["new"])
        check("a team: there is a playbook per role", len(team["playbooks"]) >= 2, f"{len(team['playbooks'])} playbooks")
        leftovers = [name for name in team["playbooks"] if "{{" in read(team["path"] / "docs" / "playbooks" / name)]
        check("a team: no playbook carries a leftover of its template", not leftovers, ", ".join(leftovers))

        check("going on after the plan: it prepared the repository before the first task", bool(going_on["block"].strip()))
        check("going on after the plan: the reply says that this came first", has(results[2].reply, PREPARES))

        print("\n--- the acceptance of a prepared repository: a new session, with Blueprint not loaded", flush=True)
        bare = run(claude, one["path"], "Começa a primeira tarefa. Antes de escrever qualquer coisa, me diga em poucas linhas qual é a tarefa, onde ela está escrita e onde você registra o que fizer.", timeout=900, web=False, plugin=False)
        print("    the agent:", flush=True)
        for line in bare.reply.splitlines():
            print("      " + line)
        if refused(bare):
            check("the acceptance ran", False, refused(bare))
        else:
            check("the acceptance ran", bare.code == 0, f"exit {bare.code}")
            check("a bare agent names the first task", has(bare.reply, FIRST_TASK))
            check("a bare agent knows where the task is written", has(bare.reply, ("specs/", "spec ", "plan.md", "plano")))
            check("a bare agent knows where to record what it does", has(bare.reply, RECORDS))
        if kept:
            print(f"\nthe projects are kept in {kept}")
    finally:
        if temporary:
            temporary.cleanup()
    check("nothing under skills/ changed in this repository", skills_changes() == before_skills)
    print("\n" + spent(results + ([bare] if bare else [])))
    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
