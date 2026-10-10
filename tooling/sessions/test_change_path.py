#!/usr/bin/env python3
"""
Runs a change to a project that already exists, through the blueprint skill, in
real Claude Code sessions: one small change, one improvement and one
reorganisation.

Each case opens in a copy of a small project kept in `change/`, whose code
runs, and receives what the person would say, without naming a skill. The
person asks to plan the change, or to reorganise the project: asked plainly for
a change to the code, a coding agent makes it and Blueprint is never called,
which is what a plain request should get.

| Case | The project | What must happen |
|---|---|---|
| small change | Code and a README that matches it | The agent reads first and says the change is small. With the go-ahead it writes one spec and nothing else: no state, no document, no code |
| improvement | The same, with an architecture document that is outdated in two places | The agent says what is outdated and what it proposes to write, and waits. Then: a state marked `improve`, a plan with what enters, what changes and what leaves, and a spec per task. The README is left alone, the outdated part the change does not touch is reported and not corrected, and no whole document is written |
| reorganisation | Everything in one file, requirements that match it, tests for part of it | The agent proposes and waits. Then: a state marked `refactor`, the requirements untouched, a test plan with what must keep working, the affected part as it is and as it will be, the decision recorded, and tasks with specs |

In every case nothing is written before the person answers the first message,
no file of code changes, and an existing file that changed is named in a reply.
The person tells the agent to decide the details, and takes its recommendation.

The web is closed. The words of a reply are a rough check, and each reply is
printed in full for a person to read. It needs Claude Code on the PATH, takes
about ten minutes and spends model usage, so it is not one of the checks to run
before every change. Run it after changing the survey skill or the change path:

    python tooling/sessions/test_change_path.py [--folder DIR]

With `--folder`, the three projects are kept in DIR, which must not exist yet,
so what was written can be read afterwards. Exit code 0 when every case passes,
1 otherwise, 2 when the sessions could not run at all.
"""

import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, Session, find_claude, read_state, refused, run, skills_changes, spent, verdict

FIXTURES = Path(__file__).resolve().parent / "change"
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
GO_ON = "Vou com a sua recomendação. Pode seguir até fechar o plano; se faltar algum detalhe, decida você e me avise."
MAX_TURNS = 6
CODE = ("src/", "test/", "data/", "package.json")
POSITION = re.compile(r"^[\W_]*etapa\s+(\d)\s+de\s+5", re.IGNORECASE)
DECIDED = re.compile(r"^- D-\d+ · .* · decided\s*$", re.MULTILINE)
ROW = re.compile(r"^\|\s*T-\d+\s*\|", re.MULTILINE)
CASES = [
    {
        "name": "small change", "folder": "a", "project": "loja", "extra": {}, "turns": 2,
        "asks": "Quero planejar uma mudança neste projeto antes de mexer no código: a lista de produtos deve vir em ordem alfabética pelo nome.",
        "then": "Pode gravar a spec. Ainda não comece a tarefa.",
    },
    {
        "name": "improvement", "folder": "b", "project": "loja", "extra": {"docs/arquitetura.md": "loja-arquitetura.md"}, "turns": MAX_TURNS,
        "asks": "Quero melhorar este projeto, e planejar antes de mexer no código: acrescentar uma página no navegador com a lista de produtos, para o cliente ver nome, preço e categoria. Hoje só existe a rota que devolve JSON.",
        "then": "Pode escrever. A página é uma só: a lista de produtos, com nome, preço e categoria. Se faltar algum detalhe, decida você e me avise.",
    },
    {
        "name": "reorganisation", "folder": "c", "project": "balcao", "extra": {}, "turns": MAX_TURNS,
        "asks": "Quero reorganizar este projeto por dentro, sem mudar o que ele faz. Hoje está tudo no src/server.js: as rotas, as regras e a leitura dos arquivos de produtos, clientes e pedidos. Quero separar isso em partes.",
        "then": "Pode escrever. Se faltar algum detalhe, decida você e me avise.",
    },
]


def snapshot(project: Path) -> dict[str, str]:
    """Every file of the project, with a hash of what it holds."""
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(project.rglob("*")) if p.is_file()}


def has(text: str, *groups: tuple[str, ...]) -> bool:
    """True when, for every group, the text has at least one of its words."""
    low = text.lower()
    return all(any(word in low for word in group) for group in groups)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def first_line(reply: str) -> str:
    return next((line.strip() for line in reply.splitlines() if line.strip()), "")


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
    temporary = None if kept else tempfile.TemporaryDirectory(prefix="blueprint change é ")
    root = kept or Path(temporary.name)
    try:
        for case in CASES:
            project = case["path"] = root / case["folder"] / "projetos" / case["project"]
            shutil.copytree(FIXTURES / case["project"], project)
            for where, source in case["extra"].items():
                (project / where).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(FIXTURES / source, project / where)
            case["before"] = snapshot(project)

        def conduct(case: dict) -> list[Session]:
            project, around = case["path"], (root / case["folder"],)
            turns = [run(claude, project, case["asks"], around, timeout=1500, keep=True, web=False)]
            case["after_first"] = snapshot(project)
            while len(turns) < case["turns"] and turns[-1].code == 0 and not refused(turns[-1]) and turns[-1].session_id:
                if len(turns) > 1 and read_state(project)[0].get("plan") == "closed":
                    break
                said = case["then"] if len(turns) == 1 else GO_ON
                turns.append(run(claude, project, said, around, timeout=1500, resume=turns[-1].session_id, keep=True, web=False))
            return turns

        print(f"running {len(CASES)} cases at once, up to {MAX_TURNS} turns each ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(CASES)) as pool:
            results = list(pool.map(conduct, CASES))
        every = [turn for turns in results for turn in turns]
        stopped = [refused(s) for s in every if refused(s)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of {len(every)} turns: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        for case, turns in zip(CASES, results):
            name, project, before = case["name"], case["path"], case["before"]
            for number, turn in enumerate(turns, 1):
                said = case["asks"] if number == 1 else case["then"] if number == 2 else GO_ON
                print(f"\n--- {name}, turn {number}\n    the person: {said}\n    the agent:", flush=True)
                for line in turn.reply.splitlines():
                    print("      " + line)
            first, replies = turns[0], "\n".join(turn.reply for turn in turns)
            after = case["after"] = snapshot(project)
            case["new"] = sorted(set(after) - set(before))
            changed = sorted(path for path in before if after.get(path) != before[path])
            tools = [what for turn in turns for kind, what in turn.steps if kind == "tool"]
            print(f"    {len(turns)} turns; new files: {', '.join(case['new']) or 'none'}; changed: {', '.join(changed) or 'none'}", flush=True)

            check(f"{name}: every turn ran", all(turn.code == 0 for turn in turns), ", ".join(f"exit {turn.code}" for turn in turns))
            check(f"{name}: the survey skill was called", any(what.startswith("Skill") and "blueprint-survey" in what for what in tools))
            read_first = [what for kind, what in first.steps if kind == "tool" and what.split(" ")[0] in ("Read", "Grep") and ("server.js" in what or "package.json" in what)]
            check(f"{name}: it read the code before its first message", bool(read_first))
            check(f"{name}: nothing was written before the person answered", case["after_first"] == before, ", ".join(sorted(set(case["after_first"]) ^ set(before))))
            check(f"{name}: the first message ends in a question", "?" in first.reply)
            code = [path for path in sorted(set(before) | set(after)) if path.startswith(CODE) and after.get(path) != before.get(path)]
            check(f"{name}: no file of code was created or changed", not code, ", ".join(code))
            unnamed = [path for path in changed if Path(path).name.lower() not in replies.lower()]
            check(f"{name}: every existing file that changed is named in a reply", not unnamed, ", ".join(unnamed))
            leftovers = [path for path in case["new"] if path.endswith(".md") and ("{{" in read(project / path) or "<!--" in read(project / path))]
            check(f"{name}: no new document carries a leftover of its template", not leftovers, ", ".join(leftovers))
            case["steps"], case["documents"], case["header"] = read_state(project)
            case["replies"], case["turn_list"] = replies, turns

        small, improve, refactor = CASES

        name, project = small["name"], small["path"]
        check(f"{name}: the first message says the change is small", has(small["turn_list"][0].reply, ("pequena", "pequeno")))
        check(f"{name}: one spec was written, and nothing else", len(small["new"]) == 1 and small["new"][0].startswith("docs/specs/") and small["new"][0].endswith(".md"), ", ".join(small["new"]) or "nothing")
        check(f"{name}: no state file was created", not (project / ".blueprint").exists())
        spec = "\n".join(read(project / path) for path in small["new"])
        check(f"{name}: the spec says what it does, what it does not, when it is done and how to test", has(spec, ("o que faz",), ("não faz",), ("quando",), ("como testar",)))
        check(f"{name}: no existing file changed", all(small["after"].get(path) == digest for path, digest in small["before"].items()))

        for case, point in ((improve, "improve"), (refactor, "refactor")):
            name, project = case["name"], case["path"]
            state = project / ".blueprint" / "state.md"
            passes = subprocess.run([sys.executable, str(CHECK_STATE), str(state)], capture_output=True, text=True, encoding="utf-8")
            check(f"{name}: the state passes check_state.py", state.is_file() and passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])
            check(f"{name}: the state says how the project came: {point}", case["header"].get("starting_point") == point, case["header"].get("starting_point", "missing"))
            check(f"{name}: the plan closed within {MAX_TURNS} turns", case["steps"].get("plan") == "closed", f"{len(case['turn_list'])} turns, plan {case['steps'].get('plan', 'missing')}")
            later = [turn.reply for turn in case["turn_list"][1:]]
            opened = [reply for reply in later if POSITION.match(first_line(reply))]
            check(f"{name}: every message after the go-ahead opened with where the conversation was", bool(later) and len(opened) == len(later), f"{len(opened)} of {len(later)}")
            situation, where = case["documents"].get("plan", ("missing", "-"))
            case["plan"] = read(project / where) if where != "-" else ""
            check(f"{name}: the plan exists where the state says", bool(case["plan"]), f"{situation}, {where}")
            specs = [path for path in case["new"] if "/specs/" in path and path.endswith(".md")]
            case["specs"] = "\n".join(read(project / path) for path in specs)
            check(f"{name}: the plan has a spec per task, each with how to test", bool(specs) and all("como testar" in read(project / path).lower() for path in specs), f"{len(specs)} specs")
            whole = [path for path in case["new"] if Path(path).name in ("system-description.md", "requirements.md", "descricao-do-sistema.md")]
            check(f"{name}: no whole document was written that the change does not need", not whole, ", ".join(whole))

        name, project = improve["name"], improve["path"]
        first = improve["turn_list"][0].reply
        check(f"{name}: the first message says the architecture document is outdated, and in what", has(first, ("arquitetura",), ("desatualiz",), ("app.js", "jest")))
        check(f"{name}: the first message says what it proposes to write", has(first, ("plano", "plan.md")))
        low = improve["plan"].lower()
        check(f"{name}: the plan has what enters, what changes and what leaves", all(re.search(rf"\b{word}\b", low) for word in ("entra", "muda", "sai")))
        check(f"{name}: the README, which matches the code, was left alone", improve["after"].get("README.md") == improve["before"]["README.md"])
        check(f"{name}: the outdated part the change does not touch was reported", "jest" in improve["replies"].lower())
        check(f"{name}: and it was not corrected", "jest" in read(project / "docs" / "arquitetura.md").lower())
        check(f"{name}: no second architecture document was started", "docs/architecture.md" not in improve["new"])

        name, project = refactor["name"], refactor["path"]
        check(f"{name}: the requirements were not rewritten", refactor["after"].get("docs/requisitos.md") == refactor["before"]["docs/requisitos.md"])
        situation, where = refactor["documents"].get("test-plan", ("missing", "-"))
        tests = read(project / where) if where != "-" else ""
        check(f"{name}: the test plan lists what must keep working", len(ROW.findall(tests)) >= 2, f"{situation}, {where}, {len(ROW.findall(tests))} rows")
        check(f"{name}: it says which behaviour no test covers", has(refactor["replies"] + tests, ("sem teste", "não tem teste", "não têm teste", "nenhum teste", "não há teste", "não cobre", "cobre só", "cobrem só", "só cobre", "sem cobertura", "falta teste", "faltam testes", "à mão", "manual")))
        situation, where = refactor["documents"].get("architecture", ("missing", "-"))
        architecture = read(project / where) if where != "-" else ""
        check(f"{name}: the affected part is written as it is and as it will be", has(architecture, ("como está", "como é hoje", "hoje"), ("como vai ficar", "como ficará", "como fica", "vai ficar")), f"{situation}, {where}")
        check(f"{name}: the decide skill brought how it will be", any(kind == "tool" and what.startswith("Skill") and "blueprint-decide" in what for turn in refactor["turn_list"] for kind, what in turn.steps))
        check(f"{name}: the decision is recorded as decided", bool(DECIDED.search(read(project / ".blueprint" / "state.md"))))
        check(f"{name}: a spec names the rows of the test plan that must pass", "T-0" in refactor["specs"])
        if kept:
            print(f"\nthe projects are kept in {kept}")
    finally:
        if temporary:
            temporary.cleanup()
    check("nothing under skills/ changed in this repository", skills_changes() == before_skills)
    print("\n" + spent(every))
    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
