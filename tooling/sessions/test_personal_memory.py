#!/usr/bin/env python3
"""
Runs the personal memory of the blueprint-record skill in real Claude Code
sessions: the person says something that is true of them in any project, and
the agent has to ask before writing anything outside the project folder.

| Case | What the person says | What must happen |
|---|---|---|
| refuses | The preference, and that nothing may be written outside the project | Nothing is written outside it. The learning stays in the project, and the reply says it will not carry over |
| cannot write outside | The preference, and that it may be saved | It tries the person's folder, `~/.blueprint/`, which this session cannot write to. It must say so and keep the learning in the project, not report it as saved |
| writes with permission | The preference, and where their folder is | `preferences.md` holds the preference and no content of the project, and `projects.md` holds the project's name and path |

What no session test covers: the real `~/.blueprint/`. A test session is fenced
into its project folder, so it cannot write to the person's home, and that is
on purpose. To see the real thing, run the last case by hand in your own
terminal, then read and delete the folder.

The web is closed. Each reply is printed in full for a person to read. It needs
Claude Code on the PATH, takes a few minutes and spends model usage, so it is
not one of the checks to run before every change. Run it after changing the
record skill or the personal memory:

    python tooling/sessions/test_personal_memory.py

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not run.
"""

import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, find_claude, refused, run, skills_changes, spent, verdict

HERE = Path(__file__).resolve().parent
EXAMPLE_STATE = (REPO / "skills" / "blueprint-record" / "assets" / "state.example.md").read_text(encoding="utf-8")
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
PREFERENCE = "Uma coisa sobre mim, que vale para qualquer projeto meu: eu sempre uso o Supabase, e prefiro que você decida os detalhes pequenos sozinho e só me avise."
DOCUMENTS = {
    "system-description.md": "# Descrição do sistema\n\n> **Em resumo:** um aplicativo web onde a recepção marca consultas e o paciente confirma.\n",
    "requirements.md": "# Requisitos\n\n> **Em resumo:** a recepção marca, remarca e cancela; o paciente confirma ou desiste.\n",
    "research.md": "# Pesquisa\n\n> **Em resumo:** nada pesquisado ainda.\n",
    "decisions.md": "# Decisões\n\n## D-001 · Aplicativo web em vez de aplicativo de celular\n\n- **Decisão:** aplicativo web, usado no navegador.\n- **Situação:** decidida\n",
}
SAID_NO = ("não vai", "não carrega", "não guardei", "nada fora", "só neste projeto", "só aqui", "não levo", "não sobe", "fica só")
COULD_NOT = ("não consegui", "não pude", "não foi possível", "sem acesso", "não tenho acesso", "bloque", "negad", "recusad", "permiss")
PROJECT_WORDS = ("consulta", "recepção", "paciente", "clínica")
CASES = [
    {
        "name": "refuses", "folder": "a", "new": False,
        "asks": PREFERENCE + " Mas não quero que você grave nada fora da pasta deste projeto.",
    },
    {
        "name": "cannot write outside", "folder": "b", "new": False,
        "asks": PREFERENCE + " Pode guardar o que você aprender sobre mim, para os próximos projetos.",
    },
    {
        "name": "writes with permission", "folder": "c", "new": False,
        "asks": PREFERENCE + " Pode guardar o que aprender sobre mim: a minha pasta pessoal é {home}.",
    },
]


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def files(folder: Path) -> set[str]:
    return {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}


def has(text: str, *groups: tuple[str, ...]) -> bool:
    low = text.lower()
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

    before_skills = skills_changes()
    with tempfile.TemporaryDirectory(prefix="blueprint pessoal é ") as folder:
        root = Path(folder)
        for case in CASES:
            around = case["around"] = root / case["folder"]
            project = case["path"] = around / "projetos" / "agenda-clinica"
            project.mkdir(parents=True)
            if not case["new"]:
                put(project / ".blueprint" / "state.md", EXAMPLE_STATE)
                for name, text in DOCUMENTS.items():
                    put(project / "docs" / name, text)
            case["home"] = around / "casa" / ".blueprint"
            case["before_outside"] = files(around) - files(project)

        print(f"running {len(CASES)} cases at once ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(CASES)) as pool:
            results = list(pool.map(lambda c: run(claude, c["path"], c["asks"].format(home=c["home"]), (c["around"],), timeout=1200, web=False), CASES))
        stopped = [refused(s) for s in results if refused(s)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of {len(results)} turns: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        for case, session in zip(CASES, results):
            name, project = case["name"], case["path"]
            print(f"\n--- {name}\n    the person: {case['asks'].format(home=case['home'])}\n    the agent:", flush=True)
            for line in session.reply.splitlines():
                print("      " + line)
            outside = sorted(files(case["around"]) - files(project) - case["before_outside"])
            print(f"    written outside the project: {', '.join(outside) or 'nothing'}", flush=True)
            check(f"{name}: the session ran", session.code == 0, f"exit {session.code}")
            check(f"{name}: the record skill was called", any(kind == "tool" and what.startswith("Skill") and "blueprint-record" in what for kind, what in session.steps))
            case["outside"] = outside
            if not case["new"]:
                state = project / ".blueprint" / "state.md"
                passes = subprocess.run([sys.executable, str(CHECK_STATE), str(state)], capture_output=True, text=True, encoding="utf-8")
                check(f"{name}: the state still passes check_state.py", passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])
                check(f"{name}: the preference was kept in the project", has(read(state), ("supabase",)), "it is not in the state file")

        no, blocked, allowed = CASES
        check("refuses: nothing was written outside the project", not no["outside"], ", ".join(no["outside"]))
        check("refuses: the reply says the learning does not carry over", has(results[0].reply, SAID_NO))

        check("cannot write outside: nothing was written outside the project", not blocked["outside"], ", ".join(blocked["outside"]))
        check("cannot write outside: it says it could not write there", has(results[1].reply, COULD_NOT))
        check("cannot write outside: it does not report the personal memory as saved", not has(results[1].reply, ("salvei na sua pasta", "guardei na sua pasta", "gravei na sua pasta")))

        preferences, projects = read(allowed["home"] / "preferences.md"), read(allowed["home"] / "projects.md")
        print(f"\n--- the person's folder\n{preferences}\n{projects}", flush=True)
        check("writes with permission: the preferences file was written where the person said", bool(preferences.strip()), f"nothing at {allowed['home']}")
        check("writes with permission: it holds the preference", has(preferences, ("supabase",)))
        check("writes with permission: it holds no content of the project", not has(preferences, PROJECT_WORDS) and "encomenda" not in preferences.lower())
        check("writes with permission: it carries no leftover of its template", "{{" not in preferences and "<!--" not in preferences)
        check("writes with permission: the project list names the project and its path", has(projects, ("agenda-clinica",), ("projetos",)), "no projects.md" if not projects else "the path is missing")
        check("writes with permission: the reply says what was saved and where", has(results[2].reply, ("guard", "salv", "grav"), ("pasta", str(allowed["home"].name))))
    check("nothing under skills/ changed in this repository", skills_changes() == before_skills)
    print("\n" + spent(results))
    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
