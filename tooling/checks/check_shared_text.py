#!/usr/bin/env python3
"""
Reports copies of a shared text that are no longer identical.

A skill can only point at files inside its own folder, so a text that several
skills need is copied into each of them. A copy is marked, in Markdown, with

    <!-- shared: NAME -->
    the text
    <!-- /shared: NAME -->

Every block with the same NAME, in any `.md` file under `skills/`, must have the
same content. Line endings and blank lines at the edges are ignored. A marker
that is never closed, or closed without having been opened, is a problem too. A
NAME found only once is listed as a note and does not fail the check. Needs only
Python:

    python tooling/checks/check_shared_text.py [root]

Exit code 0 when every copy matches, 1 otherwise.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OPEN = re.compile(r"^\s*<!--\s*shared:\s*([A-Za-z0-9_.-]+)\s*-->\s*$")
CLOSE = re.compile(r"^\s*<!--\s*/shared:\s*([A-Za-z0-9_.-]+)\s*-->\s*$")


def blocks(path: Path, label: str) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Shared blocks of one file as (name, where, content), and the marker problems found."""
    found, problems = [], []
    name, start, body = None, 0, []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        opened, closed = OPEN.match(line), CLOSE.match(line)
        if opened:
            if name is not None:
                problems.append(f"{label}:{number} opens '{opened.group(1)}' inside '{name}', opened at line {start}")
            name, start, body = opened.group(1), number, []
        elif closed:
            if name != closed.group(1):
                problems.append(f"{label}:{number} closes '{closed.group(1)}', which is not open")
            else:
                found.append((name, f"{label}:{start}", "\n".join(body).strip("\n")))
            name = None
        elif name is not None:
            body.append(line.rstrip())
    if name is not None:
        problems.append(f"{label}:{start} opens '{name}' and never closes it")
    return found, problems


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = Path(argv[1]).resolve() if len(argv) > 1 else REPO
    skills_dir = root / "skills"
    by_name: dict[str, list[tuple[str, str]]] = {}
    problems = 0
    count = 0
    for path in sorted(skills_dir.rglob("*.md")) if skills_dir.is_dir() else []:
        found, bad = blocks(path, path.relative_to(root).as_posix())
        for problem in bad:
            problems += 1
            print(f"MARKER {problem}")
        for name, where, content in found:
            count += 1
            by_name.setdefault(name, []).append((where, content))
    for name, copies in sorted(by_name.items()):
        if len(copies) == 1:
            print(f"NOTE '{name}' has a single copy, at {copies[0][0]}")
            continue
        first_where, first_content = copies[0]
        for where, content in copies[1:]:
            if content != first_content:
                problems += 1
                print(f"DIFFERENT '{name}': {where} is not the same as {first_where}")
    print(f"{count} shared blocks under {len(by_name)} names, {problems} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
