#!/usr/bin/env python3
"""
Reports files in the plugin folder that the plugin directory refuses.

The directory accepts scripts, programs and files outside the allowed types only
from Verified organizations. Ours is not one, so everything under `plugin/` must
be Markdown, text, JSON, YAML, or a PNG, JPEG, GIF, WebP or ICO image, and must
be UTF-8 with no NUL bytes. Also refused: a file that starts with `#!`, a package
manager configuration file, a `.claude/skills` folder, and a `.claude-plugin`
folder that holds anything but `plugin.json`, an image or a `marketplace.json`.
A licence, a readme, `.gitignore` and the icon are fine. Needs only Python:

    python tooling/checks/check_plugin_files.py [plugin folder]

Exit code 0 when the directory would take the folder, 1 otherwise.
"""

import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2] / "plugin"
ALLOWED = {".md", ".txt", ".json", ".yaml", ".yml", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}
# Files with no extension, or a dotfile, that are plain text and are allowed.
PLAIN = {"license", "readme", ".gitignore", ".gitattributes"}
PACKAGE_MANAGER = {"package.json", "pnpm-workspace.yaml", "pnpm-lock.yaml", "yarn.lock", "package-lock.json", ".npmrc", ".yarnrc", ".yarnrc.yml"}


def problems(root: Path) -> list[str]:
    found = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        name = path.name.lower()
        suffix = path.suffix.lower()
        parts = path.relative_to(root).parts
        data = path.read_bytes()
        if name in PACKAGE_MANAGER:
            found.append(f"{rel}: a package manager configuration file")
        if parts[0] == ".claude" or ".claude/skills" in rel:
            found.append(f"{rel}: a .claude folder in the plugin")
        if parts[0] == ".claude-plugin" and name != "plugin.json" and suffix not in IMAGES and name != "marketplace.json":
            found.append(f"{rel}: .claude-plugin holds only plugin.json and an image")
        if data.startswith(b"#!"):
            found.append(f"{rel}: starts with #!")
        if suffix in IMAGES:
            continue
        if b"\x00" in data:
            found.append(f"{rel}: has NUL bytes")
        if name not in PLAIN and suffix not in ALLOWED:
            found.append(f"{rel}: type {suffix or 'none'} is not Markdown, text, JSON, YAML or an image")
            continue
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            found.append(f"{rel}: not UTF-8 text")
    return found


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = Path(argv[1]).resolve() if len(argv) > 1 else PLUGIN
    if not root.is_dir():
        print(f"NO PLUGIN FOLDER: {root} does not exist")
        return 1
    found = problems(root)
    for line in found:
        print("REFUSED " + line)
    print(f"{sum(1 for p in root.rglob('*') if p.is_file())} files checked, {len(found)} the directory would refuse")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
