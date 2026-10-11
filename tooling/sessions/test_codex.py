#!/usr/bin/env python3
"""
Runs Blueprint in Codex, to see whether the skills work in an agent they were
not written in (NFR-01).

Two things are checked, both from the plan of the phase:

1. **Starting a project in Codex.** A project folder with Blueprint installed
   by the CLI, for Codex (`.agents/skills/`), and the first thing a person
   says. The agent has to find the entry skill on its own, say which step the
   conversation is in, and ask before writing anything.
2. **Continuing in Codex a project that was started in Claude Code.** The same
   state file the Claude Code tests leave behind, in a folder Codex has never
   seen. It has to pick up the next question from the state and not ask again
   what is answered there.

This spends the account's ChatGPT quota, not the Claude one, and it needs
`codex` on the PATH and logged in:

    python tooling/sessions/test_codex.py [--model NAME]

The model matters: a ChatGPT account refuses some of them through Codex (this
is reported plainly). Exit code 0 when every check passes, 1 otherwise, 2 when
Codex could not run.
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from harness import REPO, verdict

MODEL = "gpt-5.6-luna"
TIMEOUT = 900  # one turn of Codex; it has sat for twenty minutes on one, so this is said and not waited out
NODE = ["node", str(REPO / "cli" / "blueprint.js")]  # our own CLI, which is what installs the skills for Codex
STATE = (Path(__file__).resolve().parent / "entry" / "padaria-pedidos-state.md").read_text(encoding="utf-8")
CHECK_STATE = REPO / "tooling" / "checks" / "check_state.py"
POSITION = re.compile(r"^[\W_]*etapa\s+(\d)\s+de\s+5", re.IGNORECASE)
START = "Quero começar um projeto novo: um site para a padaria receber encomendas."
GO_ON = "Vamos continuar o projeto."
ANSWER = "O pagamento online fica fora da primeira versão: o cliente paga na retirada."
NEXT_QUESTION = STATE.split("## Next question", 1)[1].strip().strip(".?!").lower()  # what the state has as the next question


def launcher() -> list[str]:
    """How to start Codex from here. On Windows it is a `.cmd` shim, which only runs through the shell."""
    path = shutil.which("codex")
    if not path:
        return []
    return ["cmd", "/c", path] if path.lower().endswith((".cmd", ".bat")) else [path]


def stop(pid: int) -> None:
    """Takes down a process and everything it started."""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
    else:
        subprocess.run(["pkill", "-TERM", "-P", str(pid)], capture_output=True)


def codex(model: str, folder: Path, prompt: str, resume: str = "") -> tuple[int, str, str, list[str], str]:
    """One turn of Codex in `folder`: the exit code, the last message, the whole log, the skill files it read, and the session id."""
    with tempfile.NamedTemporaryFile("r+", suffix=".txt", delete=False, encoding="utf-8") as last:
        answer = Path(last.name)
    command = [
        *launcher(), "exec", *(["resume", resume] if resume else []),
        "-m", model, "--sandbox", "workspace-write", "--skip-git-repo-check",
        "-C", str(folder), "--json", "-o", str(answer), prompt,
    ]
    # Codex has sat on a turn for more than half an hour. Say so and go on, and
    # take the whole tree down: through the `.cmd` shim, killing the shell leaves
    # `codex.exe` running, which then holds the pipes open for ever.
    started = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    try:
        out, error = started.communicate(timeout=TIMEOUT)
        code, log = started.returncode, (out or "") + (error or "")
    except subprocess.TimeoutExpired:
        stop(started.pid)
        try:
            out, error = started.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            out, error = "", ""
        code = 124
        log = f"codex did not answer within {TIMEOUT // 60} minutes\n{(out or '') + (error or '')}"
    read = []
    session = ""
    for line in log.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        text = json.dumps(event, ensure_ascii=False)
        if not session:
            found = re.search(r'"(?:session_id|conversation_id|thread_id)":\s*"([^"]+)"', text)
            if found:
                session = found.group(1)
        # the paths come out of a JSON log, where every Windows separator is escaped: one slash again before matching
        flat = re.sub(r"/+", "/", text.replace("\\\\", "/").replace("\\", "/"))
        read.extend(re.findall(r"[\w./-]*skills/[\w./-]+\.md", flat))
    reply = answer.read_text(encoding="utf-8").strip() if answer.is_file() else ""
    answer.unlink(missing_ok=True)
    return code, reply, log, sorted(set(read)), session


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    arguments = sys.argv[1:]
    model = arguments[arguments.index("--model") + 1] if "--model" in arguments and len(arguments) > arguments.index("--model") + 1 else MODEL
    if not launcher():
        print("cannot find codex on the PATH; this test runs it")
        return 2
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + (f"  [{detail}]" if detail and not ok else ""), flush=True)

    print(f"running Codex with the model {model} ...", flush=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True, prefix="blueprint é codex ") as folder:
        root = Path(folder)

        # 1. a new project, with Blueprint installed by our own CLI, for Codex
        fresh = root / "novo"
        fresh.mkdir()
        installed = subprocess.run([*NODE, "init", "--agent", "codex"], cwd=fresh, capture_output=True, text=True, encoding="utf-8", errors="replace")
        check("the CLI installs Blueprint for Codex", installed.returncode == 0 and (fresh / ".agents" / "skills" / "blueprint" / "SKILL.md").is_file(), installed.stdout.strip()[-200:])

        code, reply, log, read, session = codex(model, fresh, START)
        print(f"\n--- starting a project\n    the person: {START}\n    Codex:", flush=True)
        for line in reply.splitlines():
            print("      " + line)
        print(f"    skill files it read: {', '.join(read) or 'none'}", flush=True)
        if code != 0 and "not supported when using Codex with a ChatGPT account" in log:
            print(f"\ncould not run: this account cannot use the model {model} through Codex.")
            print("Run it again with --model and one the account has, for example gpt-5.6-luna.")
            return 2
        check("starting: the turn ran", code == 0, f"exit {code}: {log.strip()[-300:]}")
        check("starting: Codex found and read the Blueprint entry skill", any("skills/blueprint/SKILL.md" in path for path in read), ", ".join(read) or "it read none")
        opening = next((line.strip() for line in reply.splitlines() if line.strip()), "")
        check("starting: it says which step the conversation is in", bool(POSITION.match(opening)), opening[:90])
        check("starting: it asks before writing", "?" in reply)
        check("starting: it wrote no document before the person answered", not (fresh / "docs").exists())

        # 2. a project like it in the folder beside: does Codex read outside the folder it was given?
        beside = root / "vizinho" / "projetos" / "padaria-site"
        beside.mkdir(parents=True)
        other = root / "vizinho" / "projetos" / "padaria-pedidos" / ".blueprint"
        other.mkdir(parents=True)
        (other / "state.md").write_text(STATE, encoding="utf-8", newline="\n")
        subprocess.run([*NODE, "init", "--agent", "codex"], cwd=beside, capture_output=True, text=True)

        code, reply, log, read, _ = codex(model, beside, START)
        print(f"\n--- a project like it in the folder beside\n    the person: {START}\n    Codex:", flush=True)
        for line in reply.splitlines():
            print("      " + line)
        low = reply.lower()
        named = "padaria-pedidos" in low
        said_no = any(word in low for word in ("não consegui", "não pude", "não foi possível", "sem acesso", "fora da pasta", "não tenho acesso", "permiss", "bloque"))
        print(f"    it found the folder beside: {named} · it said it could not look: {said_no}", flush=True)
        check("beside: the turn ran", code == 0, f"exit {code}: {log.strip()[-300:]}")
        check("beside: it either names the project beside or says it could not look", named or said_no, "it did neither, and concluded in silence")
        check("beside: it asks which project this is", "?" in reply)
        check("beside: it created nothing before the person answered", not (beside / "docs").exists() and not (beside / ".blueprint" / "state.md").exists())

        # 3. continuing, in Codex, a project that was started in Claude Code
        going = root / "continuando" / "padaria-pedidos"
        going.mkdir(parents=True)
        (going / ".blueprint").mkdir()
        (going / ".blueprint" / "state.md").write_text(STATE, encoding="utf-8", newline="\n")
        subprocess.run([*NODE, "init", "--agent", "codex"], cwd=going, capture_output=True, text=True)

        code, reply, log, read, _ = codex(model, going, GO_ON)
        print(f"\n--- continuing a project started in Claude Code\n    the person: {GO_ON}\n    Codex:", flush=True)
        for line in reply.splitlines():
            print("      " + line)
        print(f"    skill files it read: {', '.join(read) or 'none'}", flush=True)
        check("continuing: the turn ran", code == 0, f"exit {code}: {log.strip()[-300:]}")
        check("continuing: it read the state file", "state.md" in log)
        low = reply.lower()
        check("continuing: it says where the project stopped", any(word in low for word in ("requisit", "etapa")), opening[:90])
        check("continuing: it goes on from the state's next question", NEXT_QUESTION in low, f"it did not ask: {NEXT_QUESTION}")
        passes = subprocess.run([sys.executable, str(CHECK_STATE), str(going / ".blueprint" / "state.md")], capture_output=True, text=True, encoding="utf-8")
        check("continuing: the state file still passes check_state.py", passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])

        # 4. answering that question: does the entry reach the skill that writes, in Codex?
        before = (going / ".blueprint" / "state.md").read_text(encoding="utf-8")
        code, reply, log, read, _ = codex(model, going, ANSWER)
        print(f"\n--- answering the question\n    the person: {ANSWER}\n    Codex:", flush=True)
        for line in reply.splitlines():
            print("      " + line)
        print(f"    skill files it read: {', '.join(read) or 'none'}", flush=True)
        after = (going / ".blueprint" / "state.md").read_text(encoding="utf-8")
        check("answering: the turn ran", code == 0, f"exit {code}: {log.strip()[-300:]}")
        check("answering: the entry reached the skill that records", any("blueprint-record" in path for path in read), ", ".join(read) or "it read none")
        check("answering: the state file was saved with the answer", after != before and "pagamento" in after.lower(), "the state did not change")
        check("answering: the step's last question is ticked now", "- [x] O que fica fora da primeira versão" in after, "the checklist was not updated")
        passes = subprocess.run([sys.executable, str(CHECK_STATE), str(going / ".blueprint" / "state.md")], capture_output=True, text=True, encoding="utf-8")
        check("answering: the state it wrote passes check_state.py", passes.returncode == 0, (passes.stdout.strip().splitlines() or ["no output"])[0])
    return verdict(failures)


if __name__ == "__main__":
    sys.exit(main())
