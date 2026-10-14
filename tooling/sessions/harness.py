"""
What the session tests share: finding Claude Code and running one headless
session with this repository loaded as a plugin.

A session runs in the folder of a throwaway project, fenced in: reading outside
that folder is refused, for the file tools and for the read-only shell commands
Claude Code runs without asking (`ls`, `Get-ChildItem`). It can still read this
repository's `skills/` (a skill reads its own `references/` and `assets/`) and
any folder a test names, which stands for the person granting access to it.

A session does not see the connectors (MCP servers) of the account that runs
the test: they have no part in what is tested, a session could reach for them,
and their list alone costs tokens at every session start.
"""

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = ["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Bash(date *)"]
WEB = ["WebFetch", "WebSearch"]  # allowed when a session may use the web: a headless session has nobody to approve them
FENCE = json.dumps({"permissions": {"blockReadsOutsideWorkingDirectories": True}})
CLIMBS = re.compile(r"(?<![\w.])\.\.(?![\w.])")  # `..` standing as a path, not as part of a name or of an ellipsis


@dataclass
class Session:
    code: int
    reply: str  # the agent's last message, which is what the person reads at the end
    steps: list[tuple[str, str]] = field(default_factory=list)  # ("text", what it said) or ("tool", name and input), in order
    session_id: str = ""
    cost: float = 0.0  # what Claude Code reports, in dollars at API prices: for a resumed session, the whole session so far
    seconds: float = 0.0
    denied: list[str] = field(default_factory=list)  # the tools the agent called and was refused, in order


def find_claude() -> str | None:
    return shutil.which("claude")


def run(claude: str, project: Path, prompt: str, allow_folders: tuple[Path, ...] = (), timeout: int = 900, resume: str = "", keep: bool = False, web: bool = True, plugin: bool = True, extra_tools: tuple[str, ...] = ()) -> Session:
    """Runs one turn in `project` with `prompt` and returns what the agent said and did, in order.

    With `keep`, Claude Code keeps the session, so a later call can pass its id in `resume` and go on from it.
    With `web` on, the agent may search and fetch pages. With it off, it cannot, which is cheaper and tests what it does then.
    With `plugin` off, this repository is not loaded: a bare agent, which is what a person has when they open a prepared project without Blueprint installed.
    `extra_tools` widens what the session may call, for a skill that carries a script: without it the agent cannot run one.
    """
    command = [claude, "-p", "--strict-mcp-config"]
    if plugin:
        command += ["--plugin-dir", str(REPO), "--add-dir", str(REPO / "skills")]
    if resume:
        command += ["--resume", resume]
    for folder in allow_folders:
        command += ["--add-dir", str(folder)]
    command += [
        "--settings", FENCE, "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS, *extra_tools, *(WEB if web else ()),
        "--output-format", "stream-json", "--verbose",
    ]
    if not (keep or resume):
        command.append("--no-session-persistence")
    if not web:
        command += ["--disallowedTools", *WEB]
    done = subprocess.run(command, cwd=project, input=prompt.encode("utf-8"), capture_output=True, timeout=timeout)
    out = done.stdout.decode("utf-8", errors="replace")
    session = Session(done.returncode, "")
    for line in out.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("session_id"):
            session.session_id = str(event["session_id"])
        if event.get("type") == "assistant":
            for block in (event.get("message") or {}).get("content") or []:
                if block.get("type") == "text" and block.get("text", "").strip():
                    session.steps.append(("text", block["text"].strip()))
                elif block.get("type") == "tool_use":
                    session.steps.append(("tool", f"{block.get('name')} {json.dumps(block.get('input'), ensure_ascii=False)}"))
        elif event.get("type") == "result":
            session.reply = str(event.get("result") or "").strip()
            session.cost = float(event.get("total_cost_usd") or 0)
            session.seconds = float(event.get("duration_ms") or 0) / 1000
            session.denied = [str(denial.get("tool_name")) for denial in event.get("permission_denials") or [] if isinstance(denial, dict)]
    if not session.reply:
        session.reply = out.strip() if not session.steps else next((s for kind, s in reversed(session.steps) if kind == "text"), "")
    return session


def converse(claude: str, project: Path, turns: list[str], allow_folders: tuple[Path, ...] = (), timeout: int = 1200) -> list[Session]:
    """Says each of `turns` in one continuing session; stops early when a turn does not run."""
    done: list[Session] = []
    for said in turns:
        resume = done[-1].session_id if done else ""
        done.append(run(claude, project, said, allow_folders, timeout=timeout, resume=resume, keep=True))
        if done[-1].code != 0 or refused(done[-1]) or not done[-1].session_id:
            break
    return done


def refused(session: Session) -> str | None:
    """The reason, when Claude Code did not run the session at all, as when the account's usage limit is reached."""
    first = session.reply.strip().splitlines()[0] if session.reply.strip() else ""
    return first if "session limit" in first.lower() or "usage limit" in first.lower() else None


def cost_of(sessions: list[Session]) -> float:
    """What the turns cost together, in dollars at API prices.

    A turn that resumes a session reports the cost of the whole session so far,
    not its own: in a run of seven turns, the last one took 22 seconds and
    reported $3.47. So the turns of one session count once, by how much each
    added. A turn that reports less than the one before it is counted whole.
    """
    total = 0.0
    so_far: dict[str, float] = {}
    for session in sessions:
        before = so_far.get(session.session_id, 0.0) if session.session_id else 0.0
        total += session.cost - before if session.cost >= before else session.cost
        if session.session_id:
            so_far[session.session_id] = session.cost
    return total


def spent(sessions: list[Session]) -> str:
    """One line with what the turns took, to print at the end of a test: the time, the cost, and what was refused."""
    line = f"{len(sessions)} session turn(s), {sum(s.seconds for s in sessions) / 60:.1f} min of agent time, about ${cost_of(sessions):.2f} at API prices"
    denied = [name for s in sessions for name in s.denied]
    if denied:
        line += f"; {len(denied)} tool call(s) refused: " + ", ".join(f"{name} x{denied.count(name)}" for name in sorted(set(denied)))
    return line


def verdict(failures: list[str], note: str = "") -> int:
    """Prints the last lines of a test and returns its exit code: how many checks failed, and which, so the end of the output is enough."""
    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s){note}")
    for name in failures:
        print("  failed: " + name)
    return 1 if failures else 0


def spoke_before_leaving(session: Session, project: Path) -> bool | None:
    """Whether the agent said something before its first look outside the project folder.

    None when it never looked outside. A look outside is a file tool or a shell
    command whose input names a path above the project: `..` as a path, or a
    path under the folder two levels up that is not the project itself. Agents
    list folders with shell commands as often as with file tools, so both count.
    """
    project_text = str(project).replace("\\", "/").lower()
    skills_text = str(REPO / "skills").replace("\\", "/").lower()
    around_text = str(Path(project).parent.parent).replace("\\", "/").lower()
    spoke = False
    for kind, what in session.steps:
        if kind == "text":
            spoke = True
            continue
        name, _, raw = what.partition(" ")
        if name not in ("Read", "Glob", "Grep", "Bash", "PowerShell"):
            continue
        low = raw.replace("\\\\", "/").replace("\\", "/").lower()
        elsewhere = low.replace(project_text, "").replace(skills_text, "")
        if CLIMBS.search(low) or around_text in elsewhere:
            return spoke
    return None


def used_skill(session: Session, name: str) -> bool:
    """Whether a skill guided the turn: the agent called it, or read a file of it.

    An agent reaches a skill's text either way, and what is being tested is the
    behaviour the text asks for, not which tool carried it.
    """
    folder = f"skills/{name}/"
    for kind, what in session.steps:
        if kind != "tool":
            continue
        head, _, raw = what.partition(" ")
        low = raw.replace("\\\\", "/").replace("\\", "/").lower()
        if head == "Skill" and name in low:
            return True
        if head in ("Read", "Glob", "Grep") and folder in low:
            return True
    return False


def read_state(project: Path) -> tuple[dict[str, str], dict[str, tuple[str, str]], dict[str, str]]:
    """What a project's state file says: the situation of each step, the situation and place of each document, and the header.

    Three empty dictionaries when the project has no state file. It reads with the gate's own reader, `check_state.py`.
    """
    path = Path(project) / ".blueprint" / "state.md"
    if not path.is_file():
        return {}, {}, {}
    checks = str(REPO / "tooling" / "checks")
    if checks not in sys.path:
        sys.path.insert(0, checks)
    import check_state

    lines = path.read_text(encoding="utf-8").splitlines()
    problems: list[str] = []
    fields, start = check_state.header(lines, problems)
    found = check_state.sections(lines, start, problems)
    steps = {row[0]: row[1] for row in check_state.table(found.get("Steps", []), ["Step", "Situation", "Main questions"], "Steps", problems)}
    documents = {row[0]: (row[1], row[2]) for row in check_state.table(found.get("Documents", []), ["Document", "Situation", "Where"], "Documents", problems)}
    return steps, documents, fields


def skills_changes() -> str:
    """What git sees changed under skills/, to tell whether a session touched the repository."""
    return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "skills"], capture_output=True, text=True).stdout
