#!/usr/bin/env python3
"""
Test of the structure checks: each one must pass on a sound input and fail on an
input with one planted error.

Covers check_root_names.py, check_skills.py, check_shared_text.py and
check_state.py. Every case builds a throwaway folder, so nothing in the
repository is touched. Needs only Python:

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

    # The project state file
    repo = CHECKS.parents[1]
    assets = repo / "skills" / "blueprint-record" / "assets"
    example = (assets / "state.example.md").read_text(encoding="utf-8")
    template = (assets / "state.md").read_text(encoding="utf-8")

    def state(name: str, text: str, expected: int, as_template: bool = False) -> None:
        with tempfile.TemporaryDirectory(prefix="blueprint checks é ") as folder:
            path = Path(folder) / "state.md"
            path.write_text(text, encoding="utf-8", newline="")
            command = [sys.executable, str(CHECKS / "check_state.py")] + (["--template"] if as_template else []) + [str(path)]
            got = subprocess.run(command, capture_output=True).returncode
        ok = got == expected
        if not ok:
            failures.append(name)
        print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else f"  [exit {got}, expected {expected}]"))

    def changed(old: str, new: str) -> str:
        assert old in example, f"the example no longer has: {old}"
        return example.replace(old, new, 1)

    state("state: the shipped example passes", example, 0)
    state("state: the example with CRLF line endings passes", example.replace("\n", "\r\n"), 0)
    state("state: the shipped template passes as a template", template, 0, as_template=True)
    state("state: the template fails as a real state", template, 1)
    state("state: no header fails", example.split("---", 2)[2], 1)
    state("state: a missing header field fails", changed("developers: 1\n", ""), 1)
    state("state: an unknown format number fails", changed("blueprint_state: 1", "blueprint_state: 2"), 1)
    state("state: 'continue' as a starting point fails", changed("starting_point: start", "starting_point: continue"), 1)
    state("state: a date that is not UTC fails", changed("2026-10-09T15:30:00Z", "09/10/2026 15:30"), 1)
    state("state: a missing section fails", changed("## Open points", "## Open questions"), 1)
    state("state: a missing fact fails", changed("| calls-a-model | unknown | - |\n", ""), 1)
    state("state: a fact value out of the list fails", changed("| has-screens | yes | said |", "| has-screens | maybe | said |"), 1)
    state("state: a step situation out of the list fails", changed("| requirements | open | 2 of 3 |", "| requirements | done | 2 of 3 |"), 1)
    state("state: counts that disagree with the checklist fail", changed("| requirements | open | 2 of 3 |", "| requirements | open | 1 of 3 |"), 1)
    state("state: a step advanced with a question open fails", changed("| requirements | open | 2 of 3 |", "| requirements | advanced | 2 of 3 |"), 1)
    state("state: a missing fixed document fails", changed("| research | in-progress | docs/research.md |\n", ""), 1)
    state("state: a ready document with no place fails", changed("| system-description | ready | docs/system-description.md |", "| system-description | ready | - |"), 1)
    state("state: a leftover placeholder fails", example + "\n{{SOMETHING}}\n", 1)

    # The repository itself
    for check in ("check_root_names.py", "check_skills.py", "check_shared_text.py"):
        got = run(check, repo)
        ok = got == 0
        if not ok:
            failures.append(check)
        print(("PASS  " if ok else "FAIL  ") + f"this repository passes {check}" + ("" if ok else f"  [exit {got}]"))
    got = subprocess.run([sys.executable, str(CHECKS / "check_state.py")], capture_output=True).returncode
    if got:
        failures.append("check_state.py")
    print(("PASS  " if not got else "FAIL  ") + "this repository passes check_state.py" + ("" if not got else f"  [exit {got}]"))

    print(f"\n{'OK' if not failures else 'FAILED'}: {len(failures)} failing check(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
