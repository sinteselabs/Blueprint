#!/usr/bin/env python3
"""
Reports names at the repository root that a Claude Code plugin loads on its own.

The repository root is the plugin root. A file or folder with one of these names
would reach everyone who installs the plugin as an MCP server, a hook, an agent
or an executable, without anyone having decided to ship it. Names are compared
without regard to case, because a clone on Windows or macOS does not tell
`Hooks/` from `hooks/`. Needs only Python:

    python tooling/checks/check_root_names.py [root]

Exit code 0 when none of them is there, 1 otherwise.
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESERVED = {
    ".mcp.json": "MCP servers",
    ".lsp.json": "LSP servers",
    "settings.json": "plugin settings",
    "hooks": "hooks",
    "agents": "agents",
    "commands": "commands",
    "bin": "executables (and claude.ai and Cowork refuse a plugin that has it)",
    "output-styles": "output styles",
    "workflows": "workflows",
    "themes": "themes",
    "monitors": "monitors",
}


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = Path(argv[1]).resolve() if len(argv) > 1 else REPO
    present = {entry.name.lower(): entry.name for entry in root.iterdir()}
    found = 0
    for name, what in RESERVED.items():
        if name in present:
            found += 1
            print(f"RESERVED {present[name]} -> the plugin would load it as {what}")
    print(f"{len(RESERVED)} reserved names checked at the root, {found} found")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
