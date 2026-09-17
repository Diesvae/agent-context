#!/usr/bin/env python3
"""The gate of the open register — create, close and verify unsettled objects.

A procedure with a correct state, a correct rule and nothing joining them to the next gesture
is not a procedure. This script is that joint: it is the only way an object enters or leaves
the register, so the register cannot drift from the fiches it addresses.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # hard failure: a half-written register is worse than none
    raise SystemExit(f"missing Python dependency for the open register: {exc}")

ROOT = Path(__file__).resolve().parents[1]
DIRECTION = ROOT / "_direction"
REGISTER = DIRECTION / "cartes/open.yaml"
SPECIES = ("workstream", "arbitration")
TEMPLATE = """# {subject}

**Open** — `{branch} #{number}` · {species}

## What is not settled

<state the question, and why it is not being answered now>

## Measured so far

<nothing yet — a dated measurement goes here, and dating it is what makes it re-examinable>

## What would end this

<for a workstream: what "finished" means. For an arbitration: who decides, and on what>
"""


class OpenError(RuntimeError):
    """Register error presentable without a traceback."""


def load() -> tuple[dict[str, Any], str]:
    """The register plus its leading comment block, which carries the rule and must survive."""
    text = REGISTER.read_text(encoding="utf-8")
    header: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("#") or not line.strip():
            header.append(line)
            continue
        break
    data = yaml.safe_load(text)
    if not isinstance(data, dict) or data.get("version") != 1:
        raise OpenError(f"{rel(REGISTER)}: missing or unsupported `version: 1`")
    if not isinstance(data.get("branches"), list):
        raise OpenError(f"{rel(REGISTER)}: `branches` must be a list")
    return data, "".join(header)


def save(data: dict[str, Any], header: str) -> None:
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)
    REGISTER.write_text(header + body, encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def declared_branches() -> list[str]:
    """Branches that MUST appear in the register: the cross-cutting one and every level-3 app.

    This is the third sense of verification, and the only one that sees a silent defect. A
    branch with nothing open is indistinguishable from a branch nobody has looked at, and an
    empty folder cannot be committed — so only the register can carry the zero.
    """
    apps = sorted(path.name for path in DIRECTION.glob("app_*") if path.is_dir())
    return ["transverse", *apps]


def branch_entry(data: dict[str, Any], branch: str) -> dict[str, Any]:
    for entry in data["branches"]:
        if entry.get("branch") == branch:
            entry.setdefault("objects", [])
            if entry["objects"] is None:
                entry["objects"] = []
            return entry
    raise OpenError(f"unknown branch `{branch}` — declare it in {rel(REGISTER)} first")


def written_fiches() -> list[Path]:
    return sorted(
        path
        for path in DIRECTION.glob("*/open/*.md")
        if "archive" not in path.parts
    )


def verify() -> list[str]:
    faults: list[str] = []
    data, _ = load()

    seen_branches = [entry.get("branch") for entry in data["branches"]]
    duplicates = {b for b in seen_branches if seen_branches.count(b) > 1}
    for branch in sorted(duplicates):
        faults.append(f"{rel(REGISTER)}: branch `{branch}` declared twice — one list is invisible")
    for branch in declared_branches():
        if branch not in seen_branches:
            faults.append(
                f"{rel(REGISTER)}: branch `{branch}` has no entry — "
                "absent is indistinguishable from nothing open; declare it with `objects: []`"
            )

    # sense 1 — every declared address resolves.
    declared_paths: set[str] = set()
    count = 0
    for entry in data["branches"]:
        branch = entry.get("branch")
        for obj in entry.get("objects") or []:
            count += 1
            for field in ("id", "species", "subject", "fiche", "triggers"):
                if field not in obj:
                    faults.append(f"{rel(REGISTER)}: `{branch}` object missing `{field}`")
            if obj.get("species") not in SPECIES:
                faults.append(
                    f"{rel(REGISTER)}: `{branch} #{obj.get('id')}` species "
                    f"`{obj.get('species')}` outside {SPECIES}"
                )
            fiche = obj.get("fiche")
            if not fiche:
                continue
            declared_paths.add(fiche)
            target = DIRECTION / fiche
            if not target.is_file():
                faults.append(f"{rel(REGISTER)}: `{branch} #{obj.get('id')}` addresses a missing fiche: {fiche}")
                continue
            head = "\n".join(target.read_text(encoding="utf-8").splitlines()[:5])
            expected = f"**Open** — `{branch} #{obj.get('id')}`"
            if expected not in head:
                faults.append(
                    f"{rel(target)}: opening line does not carry its declared identity "
                    f"({expected}) — the register and the fiche name different objects"
                )

    # sense 2 — every written fiche is declared. A fiche nobody declared is never found.
    for path in written_fiches():
        address = path.relative_to(DIRECTION).as_posix()
        if address not in declared_paths:
            faults.append(f"{rel(path)}: written but absent from {rel(REGISTER)} — unfindable")

    if faults:
        return faults
    return [
        f"open register: {count} object(s) over {len(declared_branches())} branch(es), three senses OK"
    ]


def flatten(text: str) -> str:
    """Lowercase, accent-free, punctuation collapsed — so a trigger matches how a task is typed."""
    import unicodedata

    lowered = unicodedata.normalize("NFKD", text.lower())
    stripped = "".join(c for c in lowered if not unicodedata.combining(c))
    return " " + re.sub(r"[^a-z0-9]+", " ", stripped).strip() + " "


def incident(task: str) -> list[tuple[str, int, str, str]]:
    """Open objects a task touches — their identity, never their content.

    This is the READ half of the gate, and the direction of the question matters: we ask
    whether a DECLARED trigger appears in the task, because the trigger is the thing that was
    written in order to be recognised. Asking the reverse — whether words of the task appear
    in the fiche — matches on incidental prose.

    Only the address is emitted. An open object carries what is NOT settled, and loading it
    into an ordinary mission would serve it as if it were direction.
    """
    if not task:
        return []
    haystack = flatten(task)
    data, _ = load()
    found: list[tuple[str, int, str, str]] = []
    ordered = sorted(data["branches"], key=lambda e: (e.get("branch") != "transverse", e.get("branch") or ""))
    for entry in ordered:
        branch = entry.get("branch") or ""
        for obj in sorted(entry.get("objects") or [], key=lambda o: int(o.get("id", 0))):
            triggers = obj.get("triggers") or []
            if any(flatten(t).strip() in haystack for t in triggers):
                found.append((branch, int(obj["id"]), obj.get("species", ""), obj.get("subject", "")))
    return found


def next_number(entry: dict[str, Any]) -> int:
    used = [obj.get("id", 0) for obj in entry["objects"]]
    return max([int(n) for n in used if isinstance(n, int)], default=0) + 1


def create(branch: str, species: str, subject: str) -> int:
    if species not in SPECIES:
        raise OpenError(f"species must be one of {SPECIES}")
    data, header = load()
    entry = branch_entry(data, branch)
    number = next_number(entry)
    slug = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")[:48] or "object"
    address = f"{branch}/open/{number:03d}-{slug}.md"
    target = DIRECTION / address
    if target.exists():
        raise OpenError(f"{rel(target)} already exists")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        TEMPLATE.format(subject=subject, branch=branch, number=number, species=species),
        encoding="utf-8",
    )
    entry["objects"].append({
        "id": number,
        "species": species,
        "subject": subject,
        "triggers": sorted({w for w in flatten(subject).split() if len(w) > 3}),
        "fiche": address,
    })
    save(data, header)
    print(f"opened `{branch} #{number}` → {rel(target)}")
    return 0


def close(branch: str, number: int) -> int:
    data, header = load()
    entry = branch_entry(data, branch)
    match = next((obj for obj in entry["objects"] if int(obj.get("id", -1)) == number), None)
    if match is None:
        raise OpenError(f"no object `{branch} #{number}` in the register")
    source = DIRECTION / match["fiche"]
    archive = source.parent / "archive"
    archive.mkdir(parents=True, exist_ok=True)
    destination = archive / source.name
    if destination.exists():
        raise OpenError(f"{rel(destination)} already exists")
    source.rename(destination)
    entry["objects"].remove(match)
    save(data, header)
    # Closure MOVES; it does not annotate. Marked done in place, an object is re-read forever,
    # and the mark is the cheapest thing in the file to get wrong.
    print(f"closed `{branch} #{number}` → {rel(destination)}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    action = result.add_mutually_exclusive_group(required=True)
    action.add_argument("--verify", action="store_true", help="check the register in three senses")
    action.add_argument("--new", action="store_true", help="open an object and write its fiche")
    action.add_argument("--close", action="store_true", help="archive an object's fiche and drop its line")
    result.add_argument("--branch", help="branch of the object, e.g. app_notes or transverse")
    result.add_argument("--species", choices=SPECIES, help="what would end it")
    result.add_argument("--subject", help="one line: the unsettled question")
    result.add_argument("--id", type=int, help="object number within its branch")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.verify:
            faults = verify()
            if len(faults) == 1 and faults[0].startswith("open register:"):
                print(faults[0])
                return 0
            for fault in faults:
                print(f"  ✗ {fault}")
            return 1
        if args.new:
            if not (args.branch and args.species and args.subject):
                raise OpenError("--new needs --branch, --species and --subject")
            return create(args.branch, args.species, args.subject)
        if not (args.branch and args.id is not None):
            raise OpenError("--close needs --branch and --id")
        return close(args.branch, args.id)
    except OpenError as exc:
        print(f"open: ERROR — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
