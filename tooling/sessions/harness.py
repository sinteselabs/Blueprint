"""
What the session tests share: finding Claude Code and running one headless
session with this repository loaded as a plugin.

A session runs in the folder of a throwaway project, fenced in: reading outside
that folder is refused, for the file tools and for the read-only shell commands
Claude Code runs without asking (`ls`, `Get-ChildItem`). It can still read this
repository's `skills/` (a skill reads its own `references/` and `assets/`) and
any folder a test names, which stands for the person granting access to it.
"""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = ["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Bash(date *)"]
FENCE = json.dumps({"permissions": {"blockReadsOutsideWorkingDirectories": True}})
CLIMBS = re.compile(r"(?<![\w.])\.\.(?![\w.])")  # `..` standing as a path, not as part of a name or of an ellipsis


@dataclass
class Session:
    code: int
    reply: str  # the agent's last message, which is what the person reads at the end
    steps: list[tuple[str, str]] = field(default_factory=list)  # ("text", what it said) or ("tool", name and input), in order


def find_claude() -> str | None:
    return shutil.which("claude")


def run(claude: str, project: Path, prompt: str, allow_folders: tuple[Path, ...] = (), timeout: int = 900) -> Session:
    """Runs one session in `project` with `prompt` and returns what the agent said and did, in order."""
    command = [claude, "-p", "--plugin-dir", str(REPO), "--add-dir", str(REPO / "skills")]
    for folder in allow_folders:
        command += ["--add-dir", str(folder)]
    command += [
        "--settings", FENCE, "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS,
        "--output-format", "stream-json", "--verbose", "--no-session-persistence",
    ]
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
        if event.get("type") == "assistant":
            for block in (event.get("message") or {}).get("content") or []:
                if block.get("type") == "text" and block.get("text", "").strip():
                    session.steps.append(("text", block["text"].strip()))
                elif block.get("type") == "tool_use":
                    session.steps.append(("tool", f"{block.get('name')} {json.dumps(block.get('input'), ensure_ascii=False)}"))
        elif event.get("type") == "result":
            session.reply = str(event.get("result") or "").strip()
    if not session.reply:
        session.reply = out.strip() if not session.steps else next((s for kind, s in reversed(session.steps) if kind == "text"), "")
    return session


def refused(session: Session) -> str | None:
    """The reason, when Claude Code did not run the session at all, as when the account's usage limit is reached."""
    first = session.reply.strip().splitlines()[0] if session.reply.strip() else ""
    return first if "session limit" in first.lower() or "usage limit" in first.lower() else None


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


def skills_changes() -> str:
    """What git sees changed under skills/, to tell whether a session touched the repository."""
    return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "skills"], capture_output=True, text=True).stdout
