#!/usr/bin/env python3
"""
Reports skills that break the Agent Skills format.

For every folder under `skills/`:

- there is a `SKILL.md`, and it opens with a frontmatter block;
- `name` equals the folder name: lowercase letters, digits and single hyphens,
  64 characters at most;
- `description` has 1 to 1024 characters;
- `SKILL.md` has 500 lines at most;
- no Markdown link in the skill points outside the skill's own folder, because
  a skill is copied on its own and can only rely on its own files.

Needs only Python:

    python tooling/checks/check_skills.py [root]

Exit code 0 when every skill passes, 1 otherwise.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[2]
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK = re.compile(r'(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
FENCE = re.compile(r"^\s*(```|~~~)")
SKIP = re.compile(r"^(https?:|mailto:|#|<)")
MAX_NAME, MAX_DESCRIPTION, MAX_LINES = 64, 1024, 500


def frontmatter(text: str) -> dict[str, str] | None:
    """Top-level `key: value` pairs of the frontmatter, or None when there is no block.

    A value left empty, or given as `>` or `|`, is read from the indented lines below it.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None
    fields: dict[str, str] = {}
    key = None
    for line in lines[1:end]:
        if line[:1] in (" ", "\t"):
            if key is not None and line.strip():
                fields[key] = (fields[key] + " " + line.strip()).strip()
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            key = None
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in (">", "|", ">-", "|-", ">+", "|+"):
            value = ""
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        fields[key] = value
    return fields


def outside_links(skill: Path) -> list[str]:
    problems = []
    for path in sorted(skill.rglob("*.md")):
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
                relative = unquote(target.split("#", 1)[0])
                if relative and not (path.parent / relative).resolve().is_relative_to(skill.resolve()):
                    where = path.relative_to(skill).as_posix()
                    problems.append(f"{where}:{number} links outside the skill -> {target}")
    return problems


def check(skill: Path) -> list[str]:
    main_file = skill / "SKILL.md"
    if not main_file.is_file():
        return ["no SKILL.md"]
    text = main_file.read_text(encoding="utf-8")
    problems = []
    fields = frontmatter(text)
    if fields is None:
        problems.append("SKILL.md does not open with a frontmatter block")
    else:
        name = fields.get("name", "")
        if name != skill.name:
            problems.append(f"name '{name}' is not the folder name '{skill.name}'")
        if not NAME.match(name) or len(name) > MAX_NAME:
            problems.append(f"name '{name}' must be lowercase letters, digits and single hyphens, {MAX_NAME} characters at most")
        description = fields.get("description", "")
        if not description:
            problems.append("description is missing or empty")
        elif len(description) > MAX_DESCRIPTION:
            problems.append(f"description has {len(description)} characters, the limit is {MAX_DESCRIPTION}")
    lines = len(text.splitlines())
    if lines > MAX_LINES:
        problems.append(f"SKILL.md has {lines} lines, the limit is {MAX_LINES}")
    return problems + outside_links(skill)


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = Path(argv[1]).resolve() if len(argv) > 1 else REPO
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        print("NO SKILLS FOLDER: skills/ does not exist at the root")
        return 1
    skills = sorted(entry for entry in skills_dir.iterdir() if entry.is_dir())
    total = 0
    for skill in skills:
        for problem in check(skill):
            total += 1
            print(f"SKILL {skill.name}: {problem}")
    print(f"{len(skills)} skills checked, {total} problems")
    return 1 if total or not skills else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
