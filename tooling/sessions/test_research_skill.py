#!/usr/bin/env python3
"""
Runs the blueprint-research skill in three real Claude Code sessions, each in
the situation one of its rules is for.

| Case | The folder | The web | What must happen |
|---|---|---|---|
| alone, with the web | Empty, no project | Open | Reads pages in the session, recommends one option with a reason, names its sources with the date, and creates no file |
| in a project, without the web | A Blueprint project whose state declares "no budget" | Closed | Says it could not read the pages, recommends all the same by the declared criterion, and writes the research document with what is left to verify |
| no criterion declared | Empty, no project | Closed | Says which criteria it used, since the person declared none, and recommends |

In no case may the agent say that its recommendation is weak, or propose a test
before the person decides. The words of a reply are a rough check, and each
reply is printed in full for a person to read.

It needs Claude Code on the PATH, takes a few minutes and spends model usage,
so it is not one of the checks to run before every change. Run it after
changing the research skill:

    python tooling/sessions/test_research_skill.py

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not
run at all.
"""

import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, Session, find_claude, refused, run, skills_changes, spent

HERE = Path(__file__).resolve().parent
STATE = (HERE / "entry" / "padaria-pedidos-state.md").read_text(encoding="utf-8")
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b|\b\d{1,2}/\d{1,2}/20\d\d\b|\b\d{1,2} de [a-zç]+ de 20\d\d\b", re.IGNORECASE)
GRADES_ITSELF = (
    "recomendação fraca", "recomendação frágil", "recomendação incerta", "recomendação é fraca", "recomendação é frágil",
    "pouca confiança", "baixa confiança", "não tenho certeza", "inconclusiv", "testar antes de decidir", "teste antes de decidir",
    "faça um teste antes", "recomendo testar antes",
)
COULD_NOT_READ = ("não consegui", "não pude", "não foi possível", "sem acesso", "bloque", "não li", "não foi lid", "de memória", "negad", "recusad")
CASES = [
    {
        "name": "alone, with the web", "folder": "a", "project": False, "web": True,
        "prompt": "Preciso escolher onde hospedar de graça um site pequeno, feito em Astro, com um banco de dados simples. Não tenho verba para serviço pago. Pesquise e me recomende uma opção.",
    },
    {
        "name": "in a project, without the web", "folder": "b", "project": True, "web": False,
        "prompt": "Me ajude a pensar numa coisa antes de seguirmos: onde hospedar o site e o banco de dados?",
    },
    {
        "name": "no criterion declared", "folder": "c", "project": False, "web": False,
        "prompt": "Qual biblioteca de testes devo usar num projeto pequeno em Python? Pesquise e me recomende uma.",
    },
]


def has(reply: str, *groups: tuple[str, ...]) -> bool:
    low = reply.lower()
    return all(any(word in low for word in group) for group in groups)


def called(session: Session, *tools: str) -> int:
    return sum(1 for kind, what in session.steps if kind == "tool" and what.startswith(tools))


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
    with tempfile.TemporaryDirectory(prefix="blueprint research é ") as folder:
        root = Path(folder)
        for case in CASES:
            case["path"] = root / case["folder"] / "projetos" / ("padaria-pedidos" if case["project"] else "rascunho")
            case["path"].mkdir(parents=True)
            if case["project"]:
                (case["path"] / ".blueprint").mkdir()
                (case["path"] / ".blueprint" / "state.md").write_text(STATE, encoding="utf-8", newline="\n")

        print(f"running {len(CASES)} sessions at once ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(CASES)) as pool:
            results = list(pool.map(lambda c: run(claude, c["path"], c["prompt"], (root / c["folder"],), timeout=1200, web=c["web"]), CASES))
        stopped = [refused(s) for s in results if refused(s)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of {len(CASES)} sessions: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2

        for case, session in zip(CASES, results):
            name = case["name"]
            print(f"\n--- {name}\n    the person: {case['prompt']}\n    the agent:", flush=True)
            for line in session.reply.splitlines():
                print("      " + line)
            skills = [str(json.loads(what.partition(" ")[2]).get("skill")) for kind, what in session.steps if kind == "tool" and what.startswith("Skill ")]
            print(f"    pages searched or read: {called(session, 'WebFetch', 'WebSearch')}; skills called: {', '.join(skills) or 'none'}", flush=True)
            check(f"{name}: the session ran", session.code == 0, f"exit {session.code}")
            check(f"{name}: the research skill was called from the plain request", any(kind == "tool" and what.startswith("Skill") and "blueprint-research" in what for kind, what in session.steps))
            check(f"{name}: it recommends one option", has(session.reply, ("recomend",)))
            graded = [words for words in GRADES_ITSELF if words in session.reply.lower()]
            check(f"{name}: it does not call its recommendation weak or ask for a test before deciding", not graded, ", ".join(graded))

        alone, project, bare = results
        made = sorted(p.relative_to(CASES[0]["path"]).as_posix() for p in CASES[0]["path"].rglob("*") if p.is_file())
        check("alone, with the web: it read pages in the session", called(alone, "WebFetch", "WebSearch") > 0)
        check("alone, with the web: the reply names its sources, with an address", "http" in alone.reply.lower() or "](" in alone.reply)
        check("alone, with the web: the sources carry the date they were read", bool(DATE.search(alone.reply)) or has(alone.reply, ("hoje",)))
        check("alone, with the web: the reason is the criterion the person gave", has(alone.reply, ("gratuit", "grátis", "sem custo", "de graça", "verba")))
        check("alone, with the web: no file was created outside a project", not made, ", ".join(made))

        check("in a project, without the web: it says it could not read the pages", has(project.reply, COULD_NOT_READ))
        check("in a project, without the web: it recommends by the criterion in the state", has(project.reply, ("gratuit", "grátis", "sem custo", "verba")))
        check("in a project, without the web: the choice stays with the person", "?" in project.reply)
        document = CASES[1]["path"] / "docs" / "research.md"
        text = document.read_text(encoding="utf-8") if document.is_file() else ""
        check("in a project, without the web: the research document was written", bool(text))
        check("in a project, without the web: the document has the decision, the reason, the alternatives and the sources", has(text, ("decisão",), ("motivo",), ("alternativa",), ("fonte",)))
        check("in a project, without the web: the document says what was not verified", has(text, ("não verificad", "a conferir", "a verificar", "não conferid")))
        check("in a project, without the web: the document carries no leftover of its template", bool(text) and "{{" not in text and "<!--" not in text)
        state = CASES[1]["path"] / ".blueprint" / "state.md"
        passes = subprocess.run([sys.executable, str(CHECK_STATE), str(state)], capture_output=True, text=True, encoding="utf-8")
        check("in a project, without the web: the state still passes check_state.py", passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])
        decided = [line for line in state.read_text(encoding="utf-8").splitlines() if line.startswith("- D-") and "· decided" in line]
        check("in a project, without the web: no decision was recorded as taken", not decided, "; ".join(decided))

        check("no criterion declared: it says it could not read the pages", has(bare.reply, COULD_NOT_READ))
        check("no criterion declared: it says which criteria it used, since none was declared", has(bare.reply, ("critério", "criterio", "comparei p", "levei em conta", "considerei")))
        made = sorted(p.relative_to(CASES[2]["path"]).as_posix() for p in CASES[2]["path"].rglob("*") if p.is_file())
        check("no criterion declared: no file was created outside a project", not made, ", ".join(made))
    check("nothing under skills/ changed in this repository", skills_changes() == before)
    print("\n" + spent(results))

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
