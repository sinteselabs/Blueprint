#!/usr/bin/env python3
"""
Reports what is wrong in a Blueprint project state file.

Reads format 1, described in skills/blueprint-record/references/state-format.md:
a header of fixed `key: value` fields, ten fixed sections, three tables with
fixed values, and counts that must agree with each other. With no file given it
checks the two files the record skill ships: the filled example, in full, and
the template, where `{{placeholders}}` stand for the values. Needs only Python:

    python tooling/checks/check_state.py [--template] [file ...]

`--template` checks only that the keys and the sections are there. Exit code 0
when nothing is wrong, 1 otherwise.
"""

import re
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ASSETS = REPO / "skills" / "blueprint-record" / "assets"

FORMAT = "1"
KEYS = [
    "blueprint_state", "project", "starting_point", "document_language", "developers",
    "documents_at", "tasks_at", "memory", "observability", "updated", "updated_by",
]
STARTING_POINTS = {"start", "improve", "refactor"}
SECTIONS = [
    "Project kind", "Criteria the person declared", "Steps", "Documents", "Main questions",
    "Refinement questions left for later", "Answers", "Decisions", "Open points", "Next question",
]
FACTS = ["has-screens", "stores-data", "holds-personal-data", "used-by-command-or-code", "calls-a-model"]
FACT_VALUES = {"yes", "no", "unknown"}
KNOWN_HOW = {"said", "deduced", "-"}
STEPS = ["system-description", "requirements", "modeling", "architecture", "plan"]
STEP_SITUATIONS = {"not-started", "open", "advanced", "closed"}
FIXED_DOCUMENTS = ["system-description", "requirements", "research", "architecture", "decisions", "plan"]
OTHER_DOCUMENTS = {
    "use-cases", "data-model", "data-classification", "wireframes", "design",
    "interface-contract", "ai-features", "test-plan", "playbooks",
}
DOCUMENT_SITUATIONS = {"not-started", "in-progress", "ready"}

FENCE = re.compile(r"^\s*(```|~~~)")
FIELD = re.compile(r"^([a-z_]+):\s*(.*)$")
COUNT = re.compile(r"^(\d+) of (\d+)$")
STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
RULE = re.compile(r"^:?-+:?$")


def header(lines: list[str], problems: list[str]) -> tuple[dict[str, str], int]:
    """The header's fields and the index of the first line after it."""
    if not lines or lines[0].strip() != "---":
        problems.append("the file does not open with a header between two --- lines")
        return {}, 0
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        problems.append("the header is never closed with ---")
        return {}, 0
    fields: dict[str, str] = {}
    for number, line in enumerate(lines[1:end], 2):
        match = FIELD.match(line)
        if not match:
            if line.strip():
                problems.append(f"line {number}: the header takes only `key: value` lines")
            continue
        if match.group(1) in fields:
            problems.append(f"line {number}: {match.group(1)} appears twice in the header")
        fields[match.group(1)] = match.group(2).strip()
    return fields, end + 1


def check_fields(fields: dict[str, str], problems: list[str]) -> None:
    if fields["blueprint_state"] != FORMAT:
        problems.append(f"blueprint_state is '{fields['blueprint_state']}', and this check knows format {FORMAT} only")
    if fields["starting_point"] not in STARTING_POINTS:
        problems.append(f"starting_point is '{fields['starting_point']}': it must be start, improve or refactor")
    if not fields["developers"].isdigit() or int(fields["developers"]) < 1:
        problems.append(f"developers is '{fields['developers']}': it must be a whole number, 1 or more")
    stamp = fields["updated"]
    try:
        if not STAMP.match(stamp):
            raise ValueError
        datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        problems.append(f"updated is '{stamp}': it must be a UTC date and time like 2026-10-09T15:30:00Z")
    for key in ("project", "document_language", "documents_at", "tasks_at", "memory", "observability", "updated_by"):
        if not fields[key]:
            problems.append(f"{key} is empty")


def sections(lines: list[str], start: int, problems: list[str]) -> dict[str, list[str]]:
    """The lines under each second-level heading, in the order found."""
    found: dict[str, list[str]] = {}
    current = None
    in_fence = False
    for line in lines[start:]:
        if FENCE.match(line):
            in_fence = not in_fence
        if not in_fence and line.startswith("## "):
            current = line[3:].strip()
            if current in found:
                problems.append(f"the section '{current}' appears twice")
            found[current] = []
        elif current is not None:
            found[current].append(line)
    for name in found:
        if name not in SECTIONS:
            problems.append(f"'{name}' is not a section of the format")
    missing = [name for name in SECTIONS if name not in found]
    for name in missing:
        problems.append(f"the section '{name}' is missing")
    if not missing and [name for name in found if name in SECTIONS] != SECTIONS:
        problems.append("the sections are not in the order of the format")
    return found


def table(body: list[str], columns: list[str], section: str, problems: list[str]) -> list[list[str]]:
    """The rows of the section's table, without the heading row and the rule under it."""
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in body if line.strip().startswith("|")]
    rows = [row for row in rows if not all(RULE.match(cell) for cell in row)]
    if not rows or rows[0] != columns:
        problems.append(f"{section}: the table must have the columns {', '.join(columns)}")
        return []
    good = []
    for row in rows[1:]:
        if len(row) != len(columns):
            problems.append(f"{section}: the row '{row[0]}' has {len(row)} cells and the table has {len(columns)} columns")
        else:
            good.append(row)
    return good


def expect_rows(rows: list[list[str]], required: list[str], allowed: set[str], section: str, problems: list[str]) -> None:
    names = [row[0] for row in rows]
    for name in required:
        if name not in names:
            problems.append(f"{section}: the row '{name}' is missing")
    for name in sorted(set(names)):
        if name not in required and name not in allowed:
            problems.append(f"{section}: '{name}' is not a row of the format")
        if names.count(name) > 1:
            problems.append(f"{section}: the row '{name}' appears more than once")


def check_body(found: dict[str, list[str]], problems: list[str]) -> None:
    kind = table(found["Project kind"], ["Fact", "Value", "Known how"], "Project kind", problems)
    expect_rows(kind, FACTS, set(), "Project kind", problems)
    for fact, value, how in kind:
        if value not in FACT_VALUES:
            problems.append(f"Project kind: {fact} is '{value}': it must be yes, no or unknown")
        if how not in KNOWN_HOW:
            problems.append(f"Project kind: {fact} is known '{how}': it must be said, deduced or -")
        elif (value == "unknown") != (how == "-"):
            problems.append(f"Project kind: {fact} is '{value}' and known '{how}': - goes with unknown, and only with it")
    if not any(line.startswith("Deduced:") and line[8:].strip() for line in found["Project kind"]):
        problems.append("Project kind: the line 'Deduced:' is missing or empty")

    steps = table(found["Steps"], ["Step", "Situation", "Main questions"], "Steps", problems)
    expect_rows(steps, STEPS, set(), "Steps", problems)
    counted = main_questions(found["Main questions"], problems)
    for step, situation, count in steps:
        if situation not in STEP_SITUATIONS:
            problems.append(f"Steps: {step} is '{situation}': it must be not-started, open, advanced or closed")
            continue
        match = COUNT.match(count)
        if not match:
            problems.append(f"Steps: {step} has '{count}' main questions: it must be written like '2 of 4'")
            continue
        answered, total = int(match.group(1)), int(match.group(2))
        if step in counted and counted[step] != (answered, total):
            problems.append(f"Steps: {step} says {answered} of {total}, and Main questions has {counted[step][0]} of {counted[step][1]}")
        if situation == "not-started" and answered:
            problems.append(f"Steps: {step} is not-started with {answered} main questions answered")
        if situation == "open" and answered >= total:
            problems.append(f"Steps: {step} is open with every main question answered: it is advanced")
        if situation in ("advanced", "closed") and (answered != total or not total):
            problems.append(f"Steps: {step} is {situation} with {answered} of {total} main questions answered")

    documents = table(found["Documents"], ["Document", "Situation", "Where"], "Documents", problems)
    expect_rows(documents, FIXED_DOCUMENTS, OTHER_DOCUMENTS, "Documents", problems)
    for document, situation, where in documents:
        if situation not in DOCUMENT_SITUATIONS:
            problems.append(f"Documents: {document} is '{situation}': it must be not-started, in-progress or ready")
        if not where or (situation == "ready" and where == "-"):
            problems.append(f"Documents: {document} is {situation} and has no place in 'Where'")

    if not any(line.strip() for line in found["Next question"]):
        problems.append("Next question: the section is empty")


def main_questions(body: list[str], problems: list[str]) -> dict[str, tuple[int, int]]:
    """For each step under Main questions, how many questions are answered and how many there are."""
    counted: dict[str, list[int]] = {}
    step = None
    for line in body:
        if line.startswith("### "):
            step = line[4:].strip()
            if step not in STEPS:
                problems.append(f"Main questions: '{step}' is not a step of the format")
            counted[step] = [0, 0]
        elif step is not None and re.match(r"^\s*- \[[ xX]\] ", line):
            counted[step][1] += 1
            if line.lstrip()[3] in "xX":
                counted[step][0] += 1
    for name in STEPS:
        if name not in counted:
            problems.append(f"Main questions: the step '{name}' is missing")
    return {name: (done, total) for name, (done, total) in counted.items()}


def check(path: Path, template: bool) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    fields, start = header(lines, problems)
    missing = [key for key in KEYS if key not in fields]
    for key in missing:
        problems.append(f"the header has no {key}")
    for key in fields:
        if key not in KEYS:
            problems.append(f"{key} is not a field of the format")
    found = sections(lines, start, problems)
    if template or missing or any(name not in found for name in SECTIONS):
        return problems
    check_fields(fields, problems)
    check_body(found, problems)
    if "{{" in text:
        problems.append("a template placeholder, {{...}}, was left in the file")
    return problems


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    arguments = [a for a in argv[1:] if a != "--template"]
    template = "--template" in argv[1:]
    jobs = [(Path(a).resolve(), template) for a in arguments] or [(ASSETS / "state.example.md", False), (ASSETS / "state.md", True)]
    total = 0
    for path, as_template in jobs:
        label = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else path.name
        if not path.is_file():
            total += 1
            print(f"STATE {label}: the file does not exist")
            continue
        for problem in check(path, as_template):
            total += 1
            print(f"STATE {label}: {problem}")
    print(f"{len(jobs)} state files checked, {total} problems")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
