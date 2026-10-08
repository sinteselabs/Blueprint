#!/usr/bin/env python3
"""
Reports internal Markdown links that point at nothing.

Checks every tracked `.md` file: relative link targets must exist on disk. Web
links, mail links, pure anchors and `{{placeholder}}` targets are skipped, and
anchors are stripped rather than checked. Needs only Python and git:

    python tooling/checks/check_links.py

Exit code 0 when no link is broken, 1 otherwise.
"""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[2]
LINK = re.compile(r'(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
FENCE = re.compile(r"^\s*(```|~~~)")
SKIP = re.compile(r"^(https?:|mailto:|#|<)")


def main() -> int:
    listed = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z", "*.md"], capture_output=True, check=True)
    files = [f for f in listed.stdout.decode("utf-8").split("\0") if f]
    checked = broken = 0
    for name in files:
        path = REPO / name
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
                if SKIP.match(target) or "{{" in target:
                    continue
                checked += 1
                relative = unquote(target.split("#", 1)[0])
                if relative and not (path.parent / relative).exists():
                    broken += 1
                    print(f"BROKEN {name}:{number} -> {target}")
    print(f"{len(files)} files, {checked} internal links checked, {broken} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
