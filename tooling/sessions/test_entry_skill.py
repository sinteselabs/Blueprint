#!/usr/bin/env python3
"""
Runs the blueprint skill's first step, finding the starting point, in five real
Claude Code sessions, one per situation a person can be in.

Each session opens in a folder prepared for the case and receives what the
person would say, without naming the skill. The test then looks at what the
agent did and said:

| Case | The folder | What must happen |
|---|---|---|
| start | Empty, nothing beside it | Concludes a new project and asks to confirm |
| continue | Has a Blueprint state | Concludes continuing, says where it stopped, and does not look outside |
| existing code | Has code, no state | Asks whether to change it or to reorganise it |
| similar project beside | Empty, with a project like it in the next folder | Names that folder and asks which |
| cannot look outside | The same, with no access to the folders around | Says it could not look, and asks |

In every case the agent must create nothing, because the starting point is only
confirmed. Where it looks outside the project folder, it must have said
something first. The words of a reply are a rough check, so each reply is
printed in full: a person reading it is the real check.

It needs Claude Code on the PATH, takes a few minutes and spends model usage,
so it is not one of the checks to run before every change. Run it after
changing the blueprint skill:

    python tooling/sessions/test_entry_skill.py [--save FILE | --replay FILE]

`--save` keeps what every session said and did in a file, and `--replay` judges
a saved run again without spending a session, which is how to work on the
checks themselves.

Exit code 0 when every case passes, 1 otherwise, 2 when the sessions could not
run at all: Claude Code is missing, or the account's usage limit was reached.
"""

import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, Session, find_claude, refused, run, skills_changes, spoke_before_leaving

HERE = Path(__file__).resolve().parent
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
EXAMPLE_STATE = REPO / "skills" / "blueprint-record" / "assets" / "state.example.md"
BAKERY_STATE = HERE / "entry" / "padaria-pedidos-state.md"
BAKERY = "Quero começar um projeto novo: um site para a padaria receber encomendas."
QUESTION = ("?",)


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def files(folder: Path) -> set[str]:
    return {p.relative_to(folder).as_posix() for p in folder.rglob("*")}


def has(reply: str, *groups: tuple[str, ...]) -> bool:
    """True when, for every group, the reply has at least one of its words."""
    low = reply.lower()
    return all(any(word in low for word in group) for group in groups)


def cases(root: Path, build: bool = True) -> list[dict]:
    """The five cases: where each project is, what to send and what to expect.

    Each project sits two folders deep in a folder of its own, `<case>/projetos/<project>`,
    so the folders above and beside it belong to the case. `allow` is what the
    person lets the agent read outside the project. With `build`, the folders are made.
    """
    start = root / "a" / "projetos" / "bolos-encomenda"
    resume = root / "b" / "projetos" / "agenda-clinica"
    code = root / "c" / "projetos" / "loja"
    beside = root / "d" / "projetos" / "padaria-site"
    blocked = root / "e" / "projetos" / "padaria-site"
    if build:
        start.mkdir(parents=True)
        put(resume / ".blueprint" / "state.md", EXAMPLE_STATE.read_text(encoding="utf-8"))
        put(code / "package.json", '{\n  "name": "loja",\n  "version": "1.0.0",\n  "scripts": { "start": "node src/index.js" }\n}\n')
        put(code / "src" / "index.js", 'const http = require("http");\nhttp.createServer((req, res) => res.end("loja")).listen(3000);\n')
        put(code / "README.md", "# Loja\n\nSite da loja. Rode com `npm start`.\n")
        beside.mkdir(parents=True)
        put(root / "d" / "projetos" / "padaria-pedidos" / ".blueprint" / "state.md", BAKERY_STATE.read_text(encoding="utf-8"))
        blocked.mkdir(parents=True)
        put(root / "e" / "projetos" / "padaria-pedidos" / ".blueprint" / "state.md", BAKERY_STATE.read_text(encoding="utf-8"))
    return [
        {
            "name": "start", "project": start, "allow": (root / "a",), "leaves": True,
            "prompt": "Quero começar um projeto novo: um site para vender bolos por encomenda.",
            "expect": [("novo", "iniciar", "começar", "começamos", "do zero"), QUESTION],
            "what": "concludes a new project and asks to confirm",
        },
        {
            "name": "continue", "project": resume, "allow": (root / "b",), "leaves": False,
            "prompt": "Vamos continuar o projeto.",
            "expect": [("continu", "retom", "parou", "parad"), ("requisit", "deu certo")],
            "what": "concludes continuing and says where it stopped",
        },
        {
            "name": "existing code", "project": code, "allow": (root / "c",), "leaves": True,
            "prompt": "Quero mexer neste projeto.",
            "expect": [("mudar", "acrescent", "melhor", "alterar"), ("reorganiz", "refator", "document"), QUESTION],
            "what": "asks whether to change it or to reorganise it",
        },
        {
            "name": "similar project beside", "project": beside, "allow": (root / "d",), "leaves": True,
            "prompt": BAKERY,
            "expect": [("padaria-pedidos",), QUESTION],
            "what": "names the folder beside and asks which project it is",
        },
        {
            "name": "cannot look outside", "project": blocked, "allow": (), "leaves": True,
            "prompt": BAKERY,
            "expect": [("não consegui", "não pude", "não foi possível", "não tenho acesso", "sem acesso", "permiss", "bloque", "negad", "recusad"), QUESTION],
            "what": "says it could not look around and asks the person",
        },
    ]


def judge(todo: list[dict], results: list[Session], check) -> None:
    for case, session in zip(todo, results):
        name = case["name"]
        print(f"\n--- {name}\n    the person: {case['prompt']}\n    the agent:", flush=True)
        for line in session.reply.splitlines():
            print("      " + line)
        check(f"{name}: the session ran", session.code == 0, f"exit {session.code}")
        check(f"{name}: {case['what']}", has(session.reply, *case["expect"]))
        spoke = spoke_before_leaving(session, Path(case["project"]))
        if case["leaves"] is True:
            check(f"{name}: looked, or tried to look, at the folders around the project", spoke is not None)
            check(f"{name}: said something before the first look outside the project", spoke is True)
        elif case["leaves"] is False:
            check(f"{name}: did not look outside, the state was right there", spoke is None)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    arguments = sys.argv[1:]
    save = Path(arguments[1]) if arguments[:1] == ["--save"] and len(arguments) > 1 else None
    replay = Path(arguments[1]) if arguments[:1] == ["--replay"] and len(arguments) > 1 else None
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    if replay:
        saved = json.loads(replay.read_text(encoding="utf-8"))
        todo = cases(Path("."), build=False)
        for case, old in zip(todo, saved):
            case["project"] = old["project"]
        judge(todo, [Session(old["code"], old["reply"], [tuple(step) for step in old["steps"]]) for old in saved], check)
        print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s), judging a saved run")
        return 1 if failures else 0

    claude = find_claude()
    if not claude:
        print("cannot find Claude Code on the PATH; this test runs real sessions with it")
        return 2
    for fixture in (EXAMPLE_STATE, BAKERY_STATE):
        if subprocess.run([sys.executable, str(CHECK_STATE), str(fixture)], capture_output=True).returncode:
            print(f"the fixture {fixture.name} does not pass check_state.py; fix it before running sessions")
            return 1

    before = skills_changes()
    with tempfile.TemporaryDirectory(prefix="blueprint entry é ") as folder:
        todo = cases(Path(folder))
        built = files(Path(folder))
        print(f"running {len(todo)} sessions at once ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(todo)) as pool:
            results = list(pool.map(lambda c: run(claude, c["project"], c["prompt"], c["allow"]), todo))
        created = sorted(files(Path(folder)) - built)
        stopped = [refused(session) for session in results if refused(session)]
        if stopped:
            print(f"could not run: Claude Code refused {len(stopped)} of {len(todo)} sessions: {stopped[0]}")
            print("nothing was tested; run this again when the limit resets")
            return 2
        if save:
            kept = [{"name": c["name"], "project": str(c["project"]), "code": s.code, "reply": s.reply, "steps": s.steps} for c, s in zip(todo, results)]
            save.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
        judge(todo, results, check)
        print()
        check("no session created a file or a folder before the person confirmed", not created, ", ".join(created))
    check("nothing under skills/ changed in this repository", skills_changes() == before)

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
