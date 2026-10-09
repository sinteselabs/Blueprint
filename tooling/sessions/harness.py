"""
What the session tests share: finding Claude Code and running one headless
session with this repository loaded as a plugin.

A session runs in the folder of a throwaway project. It can read this
repository's `skills/` (a skill reads its own `references/` and `assets/`), and
any other folder a test names, which stands for the person granting access to it.
"""

import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
READ_AND_WRITE = ["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Bash(date *)", "Bash(ls *)"]


def find_claude() -> str | None:
    return shutil.which("claude")


def run(claude: str, project: Path, prompt: str, allow_folders: tuple[Path, ...] = (), timeout: int = 900) -> tuple[int, str]:
    """Runs one session in `project` with `prompt`; returns the exit code and what the agent said."""
    command = [claude, "-p", "--plugin-dir", str(REPO), "--add-dir", str(REPO / "skills")]
    for folder in allow_folders:
        command += ["--add-dir", str(folder)]
    command += [
        "--permission-mode", "acceptEdits", "--allowedTools", *READ_AND_WRITE,
        "--output-format", "text", "--no-session-persistence",
    ]
    done = subprocess.run(command, cwd=project, input=prompt.encode("utf-8"), capture_output=True, timeout=timeout)
    return done.returncode, done.stdout.decode("utf-8", errors="replace").strip()


def skills_changes() -> str:
    """What git sees changed under skills/, to tell whether a session touched the repository."""
    return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "skills"], capture_output=True, text=True).stdout
