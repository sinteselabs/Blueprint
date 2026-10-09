#!/usr/bin/env python3
"""
Test of the three structure checks: each one must pass on a sound tree and fail
on a tree with one planted error.

Covers check_root_names.py, check_skills.py and check_shared_text.py. Every case
builds a throwaway folder, so nothing in the repository is touched. Needs only
Python:

    python tooling/checks/test_checks.py

Exit code 0 when every case passes, 1 otherwise.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

CHECKS = Path(__file__).resolve().parent
SOUND_SKILL = "---\nname: {name}\ndescription: Does one thing. Use when that thing is needed.\n---\n\n# Title\n"
SHARED = "<!-- shared: state-format -->\n{body}\n<!-- /shared: state-format -->\n"


def run(check: str, root: Path) -> int:
    done = subprocess.run([sys.executable, str(CHECKS / check), str(root)], capture_output=True)
    return done.returncode


def skill(root: Path, folder: str, text: str | None = None, name: str | None = None) -> Path:
    path = root / "skills" / folder
    path.mkdir(parents=True, exist_ok=True)
    # newline="" keeps the bytes as given, so a case can plant CRLF on any system.
    (path / "SKILL.md").write_text(text if text is not None else SOUND_SKILL.format(name=name or folder), encoding="utf-8", newline="")
    return path


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failures = []

    def case(name: str, check: str, build, expected: int) -> None:
        # A folder name with an accent and a space: the checks must read it on any system.
        with tempfile.TemporaryDirectory(prefix="blueprint checks é ") as folder:
            root = Path(folder)
            build(root)
            got = run(check, root)
        ok = got == expected
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"  [exit {got}, expected {expected}]"))

    # Reserved names at the root
    case("root names: a clean root passes", "check_root_names.py", lambda r: (r / "skills").mkdir(), 0)
    case("root names: .mcp.json fails", "check_root_names.py", lambda r: (r / ".mcp.json").write_text("{}", encoding="utf-8"), 1)
    case("root names: a hooks folder in another case fails", "check_root_names.py", lambda r: (r / "Hooks").mkdir(), 1)
    case("root names: bin fails", "check_root_names.py", lambda r: (r / "bin").mkdir(), 1)

    # Skill format
    case("skills: a sound skill passes", "check_skills.py", lambda r: skill(r, "sample-skill"), 0)
    case("skills: no skills folder fails", "check_skills.py", lambda r: None, 1)
    case("skills: a folder without SKILL.md fails", "check_skills.py", lambda r: (r / "skills" / "empty").mkdir(parents=True), 1)
    case("skills: a name that is not the folder name fails", "check_skills.py", lambda r: skill(r, "sample-skill", name="other-name"), 1)
    case("skills: an uppercase name fails", "check_skills.py", lambda r: skill(r, "Sample", name="Sample"), 1)
    case("skills: no frontmatter fails", "check_skills.py", lambda r: skill(r, "sample-skill", text="# Title\n"), 1)
    case("skills: an empty description fails", "check_skills.py", lambda r: skill(r, "sample-skill", text="---\nname: sample-skill\ndescription:\n---\n"), 1)
    case(
        "skills: a description over 1024 characters fails",
        "check_skills.py",
        lambda r: skill(r, "sample-skill", text="---\nname: sample-skill\ndescription: " + "x" * 1025 + "\n---\n"),
        1,
    )
    case(
        "skills: a folded description is read",
        "check_skills.py",
        lambda r: skill(r, "sample-skill", text="---\nname: sample-skill\ndescription: >\n  Does one thing.\n  Use when needed.\n---\n"),
        0,
    )
    case(
        "skills: SKILL.md over 500 lines fails",
        "check_skills.py",
        lambda r: skill(r, "sample-skill", text=SOUND_SKILL.format(name="sample-skill") + "line\n" * 500),
        1,
    )

    def link_inside(root: Path) -> None:
        path = skill(root, "sample-skill", text=SOUND_SKILL.format(name="sample-skill") + "See [the reference](references/detail.md).\n")
        (path / "references").mkdir()
        (path / "references" / "detail.md").write_text("# Detail\n", encoding="utf-8")

    def link_outside(root: Path) -> None:
        skill(root, "other-skill")
        skill(root, "sample-skill", text=SOUND_SKILL.format(name="sample-skill") + "See [the other skill](../other-skill/SKILL.md).\n")

    case("skills: a link inside the skill passes", "check_skills.py", link_inside, 0)
    case("skills: a link to another skill fails", "check_skills.py", link_outside, 1)

    # Shared text
    def shared(first: str, second: str):
        def build(root: Path) -> None:
            skill(root, "skill-a", text=SOUND_SKILL.format(name="skill-a") + SHARED.format(body=first))
            skill(root, "skill-b", text=SOUND_SKILL.format(name="skill-b") + SHARED.format(body=second))

        return build

    case("shared text: no shared block passes", "check_shared_text.py", lambda r: skill(r, "sample-skill"), 0)
    case("shared text: identical copies pass", "check_shared_text.py", shared("one\ntwo", "one\ntwo"), 0)
    case("shared text: copies that differ only in line endings pass", "check_shared_text.py", shared("one\ntwo", "one\r\ntwo"), 0)
    case("shared text: copies that differ fail", "check_shared_text.py", shared("one\ntwo", "one\nthree"), 1)
    case(
        "shared text: a marker never closed fails",
        "check_shared_text.py",
        lambda r: skill(r, "sample-skill", text=SOUND_SKILL.format(name="sample-skill") + "<!-- shared: state-format -->\none\n"),
        1,
    )
    case(
        "shared text: a close without an open fails",
        "check_shared_text.py",
        lambda r: skill(r, "sample-skill", text=SOUND_SKILL.format(name="sample-skill") + "<!-- /shared: state-format -->\n"),
        1,
    )

    # The repository itself
    repo = CHECKS.parents[1]
    for check in ("check_root_names.py", "check_skills.py", "check_shared_text.py"):
        got = run(check, repo)
        ok = got == 0
        if not ok:
            failures.append(check)
        print(("PASS  " if ok else "FAIL  ") + f"this repository passes {check}" + ("" if ok else f"  [exit {got}]"))

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
