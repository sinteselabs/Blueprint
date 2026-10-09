#!/usr/bin/env python3
"""
Runs the blueprint skill's first step, finding the starting point, in five real
Claude Code sessions, one per situation a person can be in.

Each session opens in a folder prepared for the case, receives what the person
would say, without naming the skill, and the test then looks at two things: the
agent created nothing (the starting point is only confirmed, never acted on),
and its reply has the words the case calls for. The reply is printed in full,
because the words are a rough check and a person reading the reply is the real one.

| Case | The folder | What the reply must do |
|---|---|---|
| start | Empty, nothing beside it | Conclude a new project and ask to confirm |
| continue | Has a Blueprint state | Conclude continuing and say where it stopped |
| existing code | Has code, no state | Ask whether to change it or to reorganise it |
| similar project beside | Empty, with a project like it in the next folder | Name that folder and ask which |
| cannot look outside | The same, without access to the folders around | Say it could not look, and ask |

It needs Claude Code on the PATH, takes a few minutes and spends model usage,
so it is not one of the checks to run before every change. Run it after
changing the blueprint skill:

    python tooling/sessions/test_entry_skill.py

Exit code 0 when every case passes, 1 otherwise, 2 when Claude Code is missing.
"""

import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness import REPO, find_claude, run, skills_changes

HERE = Path(__file__).resolve().parent
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
EXAMPLE_STATE = REPO / "skills" / "blueprint-record" / "assets" / "state.example.md"
BAKERY_STATE = HERE / "entry" / "padaria-pedidos-state.md"
BAKERY = "Quero começar um projeto novo: um site para a padaria receber encomendas."


def put(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def files(folder: Path) -> set[str]:
    return {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}


def has(reply: str, *groups: tuple[str, ...]) -> bool:
    """True when, for every group, the reply has at least one of its words."""
    low = reply.lower()
    return all(any(word in low for word in group) for group in groups)


def cases(root: Path) -> list[dict]:
    """Builds the five folders and says, for each, what to send and what to expect."""
    start = root / "a" / "bolos-encomenda"
    start.mkdir(parents=True)

    resume = root / "b" / "agenda-clinica"
    put(resume / ".blueprint" / "state.md", EXAMPLE_STATE.read_text(encoding="utf-8"))

    code = root / "c" / "loja"
    put(code / "package.json", '{\n  "name": "loja",\n  "version": "1.0.0",\n  "scripts": { "start": "node src/index.js" }\n}\n')
    put(code / "src" / "index.js", 'const http = require("http");\nhttp.createServer((req, res) => res.end("loja")).listen(3000);\n')
    put(code / "README.md", "# Loja\n\nSite da loja. Rode com `npm start`.\n")

    beside = root / "d" / "padaria-site"
    beside.mkdir(parents=True)
    put(root / "d" / "padaria-pedidos" / ".blueprint" / "state.md", BAKERY_STATE.read_text(encoding="utf-8"))

    blocked = root / "e" / "padaria-site"
    blocked.mkdir(parents=True)
    put(root / "e" / "padaria-pedidos" / ".blueprint" / "state.md", BAKERY_STATE.read_text(encoding="utf-8"))

    question = ("?",)
    return [
        {
            "name": "start: an empty folder, nothing beside it",
            "project": start, "allow": (root / "a",),
            "prompt": "Quero começar um projeto novo: um site para vender bolos por encomenda.",
            "expect": [("novo", "iniciar", "começar", "do zero"), question],
            "what": "concludes a new project and asks to confirm",
        },
        {
            "name": "continue: the folder has a Blueprint state",
            "project": resume, "allow": (),
            "prompt": "Vamos continuar o projeto.",
            "expect": [("continu", "retom", "parou", "parad"), ("requisit", "deu certo")],
            "what": "concludes continuing and says where it stopped",
        },
        {
            "name": "existing code: the folder has code and no state",
            "project": code, "allow": (root / "c",),
            "prompt": "Quero mexer neste projeto.",
            "expect": [("mudar", "acrescent", "melhor", "alterar"), ("reorganiz", "refator", "document"), question],
            "what": "asks whether to change it or to reorganise it",
        },
        {
            "name": "similar project beside: an empty folder next to one like it",
            "project": beside, "allow": (root / "d",),
            "prompt": BAKERY,
            "expect": [("padaria-pedidos",), question],
            "what": "names the folder beside and asks which project it is",
        },
        {
            "name": "cannot look outside: the same folder, without access around it",
            "project": blocked, "allow": (),
            "prompt": BAKERY,
            "expect": [("não consegui", "não pude", "não foi possível", "não tenho", "sem acesso", "permiss", "bloque", "negad", "recusad"), question],
            "what": "says it could not look around and asks the person",
        },
    ]


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    claude = find_claude()
    if not claude:
        print("cannot find Claude Code on the PATH; this test runs real sessions with it")
        return 2
    for fixture in (EXAMPLE_STATE, BAKERY_STATE):
        if subprocess.run([sys.executable, str(CHECK_STATE), str(fixture)], capture_output=True).returncode:
            print(f"the fixture {fixture.name} does not pass check_state.py; fix it before running sessions")
            return 1
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    before = skills_changes()
    with tempfile.TemporaryDirectory(prefix="blueprint entry é ") as folder:
        todo = cases(Path(folder))
        for case in todo:
            case["before"] = files(Path(folder))
        print(f"running {len(todo)} sessions at once ...", flush=True)
        with ThreadPoolExecutor(max_workers=len(todo)) as pool:
            results = list(pool.map(lambda c: run(claude, c["project"], c["prompt"], c["allow"]), todo))
        after = files(Path(folder))
        for case, (code, reply) in zip(todo, results):
            print(f"\n--- {case['name']}\n    the person: {case['prompt']}\n    the agent:\n" + "\n".join("      " + line for line in reply.splitlines()), flush=True)
            check(f"{case['name']}: the session ran", code == 0, f"exit {code}")
            check(f"{case['name']}: {case['what']}", has(reply, *case["expect"]))
        created = sorted(after - todo[0]["before"])
        print()
        check("no session created a file or a folder before the person confirmed", not created, ", ".join(created))
    check("nothing under skills/ changed in this repository", skills_changes() == before)

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
