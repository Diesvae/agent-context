#!/usr/bin/env python3
"""Compile a deterministic documentary subgraph for one task."""

from __future__ import annotations

import argparse
import math
import re
import sys
import unicodedata
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:  # hard failure: a context is never compiled halfway
    raise SystemExit(f"missing Python dependency for the context compiler: {exc}")


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = ROOT / "_direction/cartes/system-map.yaml"
DEFAULT_SCHEMA = ROOT / "_direction/cartes/schema.yaml"
REFERENCE_FIELDS = ("contains", "depends_on", "constrained_by", "consumers")
STOPWORDS = {
    "avec", "dans", "des", "les", "pour", "une", "sur", "par", "que", "qui", "aux",
    "du", "de", "la", "le", "et", "en", "un", "au", "a", "the", "to", "of", "and",
    "modifier", "ajouter", "mettre", "jour", "faire", "touche", "toucher",
    "in", "on", "for", "with", "into", "from", "add", "change", "update", "fix",
    "make", "build", "write", "this", "that", "its",
}


class ContextError(RuntimeError):
    """Map or compilation error presentable without a traceback."""


@dataclass(frozen=True)
class Selection:
    node_id: str
    reason: str
    score: float


def read_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContextError(f"file not found: {relative(path)}") from exc
    except yaml.YAMLError as exc:
        raise ContextError(f"invalid YAML in {relative(path)}: {exc}") from exc


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(raw: str) -> Path:
    path = (ROOT / raw).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ContextError(f"path outside the repository is forbidden: {raw}") from exc
    return path


def resolve_target(target_path: str) -> Path:
    raw_target = Path(target_path)
    target = raw_target.resolve() if raw_target.is_absolute() else (ROOT / raw_target).resolve()
    try:
        target.relative_to(ROOT)
    except ValueError as exc:
        raise ContextError(f"target path outside the repository: {target_path}") from exc
    if not target.exists():
        raise ContextError(f"target path does not exist: {target_path}")
    return target


def target_documents(target_path: str | None) -> list[tuple[str, str]]:
    """An explicit Markdown target, plus the README carrying its local ontology.

    The nearest README is not a courtesy: a level-4 fiche states one concept and relies on its
    module's index for everything around it. Served alone, it reads as complete and is not.
    """
    if not target_path:
        return []
    target = resolve_target(target_path)
    documents: list[tuple[str, str]] = []
    if target.is_file() and target.suffix.lower() == ".md":
        documents.append((relative(target), "exact-target"))

    start = target if target.is_dir() else target.parent
    for directory in (start, *start.parents):
        try:
            directory.relative_to(ROOT)
        except ValueError:
            break
        owner = directory / "README.md"
        if owner.is_file():
            owner_rel = relative(owner)
            if all(doc != owner_rel for doc, _ in documents):
                documents.append((owner_rel, "nearest-ontology-owner"))
            break
        if directory == ROOT:
            break
    return documents


def normalize(value: str) -> str:
    value = value.lower().replace("æ", "ae").replace("œ", "oe")
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokens(value: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9]+", normalize(value))
        if len(token) > 1 and token not in STOPWORDS
    }


def token_estimate(text: str) -> int:
    # Deliberately conservative: prose, paths and code excerpts all in one estimate.
    return max(1, math.ceil(len(text) / 3))


def validate_map(map_path: Path, schema_path: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    data = read_yaml(map_path)
    schema = read_yaml(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda err: list(err.path))
    if errors:
        lines = []
        for error in errors[:20]:
            location = ".".join(str(part) for part in error.path) or "<root>"
            lines.append(f"{location}: {error.message}")
        raise ContextError("map does not conform to the schema:\n  - " + "\n  - ".join(lines))

    nodes: dict[str, dict[str, Any]] = {}
    for node in data["nodes"]:
        node_id = node["id"]
        if node_id in nodes:
            raise ContextError(f"duplicate node id: {node_id}")
        nodes[node_id] = node

    for raw in data["startup_docs"]:
        path = repo_path(raw)
        if not path.is_file():
            raise ContextError(f"boot source missing: {raw}")

    for node_id, node in nodes.items():
        for raw in node["docs"]:
            path = repo_path(raw)
            if not path.is_file():
                raise ContextError(f"{node_id}: document missing: {raw}")
            if path.suffix.lower() != ".md":
                raise ContextError(f"{node_id}: `docs` must point at Markdown: {raw}")
        for raw in node.get("code", []):
            if not repo_path(raw).exists():
                raise ContextError(f"{node_id}: code path missing: {raw}")
        refs: list[str] = []
        for field in REFERENCE_FIELDS:
            refs.extend(node.get(field, []))
        if node.get("producer"):
            refs.append(node["producer"])
        for ref in refs:
            if ref not in nodes:
                raise ContextError(f"{node_id}: unknown reference: {ref}")
            if ref == node_id:
                raise ContextError(f"{node_id}: self-reference is forbidden")
        for ref in node.get("constrained_by", []):
            if nodes[ref]["kind"] != "invariant":
                raise ContextError(f"{node_id}: `constrained_by` points at a non-invariant: {ref}")
        if node["kind"] == "contract":
            if nodes[node["producer"]]["kind"] != "domain":
                raise ContextError(f"{node_id}: the producer must be a domain")
            invalid_consumers = [ref for ref in node["consumers"] if nodes[ref]["kind"] != "domain"]
            if invalid_consumers:
                raise ContextError(f"{node_id}: non-domain consumers: {', '.join(invalid_consumers)}")

    systems = [node_id for node_id, node in nodes.items() if node["kind"] == "system"]
    if systems != ["system.root"]:
        raise ContextError("the map must carry exactly one root node `system.root`")

    # `contains` is a hierarchy: a cycle makes the map impossible to explain.
    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(node_id: str) -> None:
        if node_id in visiting:
            raise ContextError(f"containment cycle detected at {node_id}")
        if node_id in visited:
            return
        visiting.add(node_id)
        for child in nodes[node_id].get("contains", []):
            walk(child)
        visiting.remove(node_id)
        visited.add(node_id)

    walk("system.root")
    orphaned = sorted(set(nodes) - visited)
    if orphaned:
        raise ContextError("nodes unreachable from system.root: " + ", ".join(orphaned))

    parents: dict[str, list[str]] = defaultdict(list)
    for parent, node in nodes.items():
        for child in node.get("contains", []):
            parents[child].append(parent)
    ambiguous = {child: owners for child, owners in parents.items() if len(owners) != 1}
    missing_parent = sorted(set(nodes) - {"system.root"} - set(parents))
    if ambiguous:
        detail = ", ".join(f"{child} ({'/'.join(owners)})" for child, owners in sorted(ambiguous.items()))
        raise ContextError(f"nodes with several containment parents: {detail}")
    if missing_parent:
        raise ContextError("nodes with no containment parent: " + ", ".join(missing_parent))

    # The map is deliberately at DOMAIN grain, not fiche by fiche. At that grain completeness
    # stays checkable: every cross-cutting invariant, app root and active domain README must
    # appear in some `docs`. `archive/` is historical, therefore outside the current map.
    mapped_docs = {raw for node in nodes.values() for raw in node["docs"]}
    required_docs = {
        relative(path)
        for level in (ROOT / "_direction/1_infrastructure", ROOT / "_direction/2_app-conventions")
        for path in level.glob("*.md")
        if path.name != "README.md"
    }
    for tech in sorted(ROOT.glob("app_*/_technique")):
        required_docs.add(relative(tech / "README.md"))
        for readme in tech.glob("*/README.md"):
            if readme.parent.name != "archive":
                required_docs.add(relative(readme))
    unmapped_docs = sorted(required_docs - mapped_docs)
    if unmapped_docs:
        raise ContextError("map surfaces not declared: " + ", ".join(unmapped_docs))

    return data, nodes


def graph(nodes: dict[str, dict[str, Any]]) -> dict[str, list[tuple[str, str]]]:
    adjacency: dict[str, set[tuple[str, str]]] = defaultdict(set)

    def connect(source: str, target: str, relation: str) -> None:
        adjacency[source].add((target, relation))
        adjacency[target].add((source, f"{relation}:incoming"))

    for node_id, node in nodes.items():
        for target in node.get("contains", []):
            connect(node_id, target, "contains")
        for target in node.get("depends_on", []):
            connect(node_id, target, "depends_on")
        for target in node.get("constrained_by", []):
            connect(node_id, target, "constrained_by")
        if node["kind"] == "contract":
            connect(node_id, node["producer"], "produced_by")
            for target in node["consumers"]:
                connect(node_id, target, "consumed_by")
    return {node_id: sorted(edges) for node_id, edges in adjacency.items()}


def lexical_score(task_tokens: set[str], node: dict[str, Any]) -> float:
    if not task_tokens:
        return 0.0
    trigger_tokens = tokens(" ".join(node["triggers"]))
    identity_tokens = tokens(f"{node['id']} {node['label']} {node['responsibility']}")
    path_tokens = tokens(" ".join(node["docs"] + node.get("code", [])))
    return (
        4.0 * len(task_tokens & trigger_tokens)
        + 2.0 * len(task_tokens & identity_tokens)
        + 0.5 * len(task_tokens & path_tokens)
    )


def app_aliases(nodes: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Tokens that NAME an application, derived from the map and never hard-coded.

    Hard-coded, this table was the one part of the compiler that knew the fleet: a repository
    adopting the tool had to edit the code to declare its applications, and forgetting was
    silent — the task "fix the Foo theme" named nothing, so it partitioned nothing. Derived,
    the table can no longer diverge from the map.
    """
    result: dict[str, str] = {}
    for node_id, node in nodes.items():
        if node["kind"] != "application":
            continue
        name = node_application(node_id)
        if name is None:
            raise ContextError(f"application node whose name cannot be derived from its id: {node_id}")
        for alias in {name, *node.get("aliases", [])}:
            for token in tokens(alias):
                previous = result.get(token)
                if previous is not None and previous != name:
                    raise ContextError(
                        f"alias d'application ambigu « {token} »: {previous} et {name}"
                    )
                result[token] = name
    return result


def node_application(node_id: str) -> str | None:
    parts = node_id.split(".")
    if len(parts) >= 2 and parts[0] in {"app", "domain", "contract"}:
        return parts[1]
    return None


def prefix_depth(target: Path, candidate: Path) -> int | None:
    try:
        target.relative_to(candidate)
    except ValueError:
        return None
    return len(candidate.relative_to(ROOT).parts)


def choose_targets(
    data: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    task: str,
    target_path: str | None,
    explicit: list[str],
    max_targets: int,
) -> list[Selection]:
    for node_id in explicit:
        if node_id not in nodes:
            raise ContextError(f"requested node is unknown: {node_id}")

    aliases = app_aliases(nodes)
    all_task_tokens = tokens(task)
    mentioned_apps = {app for alias, app in aliases.items() if alias in all_task_tokens}
    task_tokens = all_task_tokens - set(aliases)
    selected: dict[str, Selection] = {
        node_id: Selection(node_id, "explicit", 10_000.0) for node_id in explicit
    }

    if target_path:
        target = resolve_target(target_path)
        matches: list[tuple[int, float, str]] = []
        for node_id, node in nodes.items():
            depths = [
                depth
                for raw in node["docs"] + node.get("code", [])
                if (
                    depth := prefix_depth(
                        target,
                        repo_path(raw).parent if repo_path(raw).name == "README.md" else repo_path(raw),
                    )
                ) is not None
            ]
            if depths:
                matches.append((max(depths), lexical_score(task_tokens, node), node_id))
        if matches:
            most_precise = max(depth for depth, _, _ in matches)
            precise = [item for item in matches if item[0] == most_precise]
            # At equal precision a contract is a sharper frontier than a domain, and a domain
            # sharper than an application. The parent comes back through graph expansion anyway.
            for preferred_kind in ("contract", "domain", "application", "invariant", "layer", "system"):
                narrowed = [item for item in precise if nodes[item[2]]["kind"] == preferred_kind]
                if narrowed:
                    precise = narrowed
                    break
            for depth, score, node_id in sorted(precise, key=lambda item: (-item[0], -item[1], item[2])):
                selected.setdefault(node_id, Selection(node_id, f"path:{target_path}", 1000 + score))

    # A broad path (an app or layer root) gives a zone, not yet a useful target. The task may
    # then replace it with the scoring nodes of that sub-hierarchy alone. A path that is already
    # precise (domain, contract, invariant) stays sovereign and reopens no other zone.
    broad_path_targets = [
        selection for selection in selected.values()
        if selection.reason.startswith("path:")
        and nodes[selection.node_id]["kind"] in {"application", "layer", "system"}
    ]
    if broad_path_targets and task_tokens:
        scoped: set[str] = set()
        queue = deque(selection.node_id for selection in broad_path_targets)
        while queue:
            node_id = queue.popleft()
            if node_id in scoped:
                continue
            scoped.add(node_id)
            queue.extend(nodes[node_id].get("contains", []))
        scoped.update(
            invariant
            for node_id in tuple(scoped)
            for invariant in nodes[node_id].get("constrained_by", [])
        )
        ranked = sorted(
            (
                (lexical_score(task_tokens, nodes[node_id]), node_id)
                for node_id in scoped
                if nodes[node_id]["kind"] not in {"application", "layer", "system"}
            ),
            key=lambda item: (-item[0], item[1]),
        )
        refinements = [(score, node_id) for score, node_id in ranked if score > 0][:max_targets]
        if refinements:
            for selection in broad_path_targets:
                selected.pop(selection.node_id, None)
            for score, node_id in refinements:
                selected.setdefault(node_id, Selection(node_id, f"task-within-path:{target_path}", 1000 + score))

    if not selected and mentioned_apps and not task_tokens:
        for app in sorted(mentioned_apps):
            node_id = f"app.{app}"
            selected[node_id] = Selection(node_id, "task-application", 100.0)

    if not selected and task_tokens:
        ranked = sorted(
            (
                (lexical_score(task_tokens, node), node_id)
                for node_id, node in nodes.items()
                if not mentioned_apps
                or node_application(node_id) is None
                or node_application(node_id) in mentioned_apps
            ),
            key=lambda item: (-item[0], item[1]),
        )
        for score, node_id in ranked:
            if score <= 0 or len(selected) >= max_targets:
                break
            selected.setdefault(node_id, Selection(node_id, "task", score))

    if not selected:
        selected["system.root"] = Selection("system.root", "fallback-global", 0.0)

    return sorted(selected.values(), key=lambda item: (-item.score, item.node_id))[:max_targets]


def expand(
    nodes: dict[str, dict[str, Any]],
    adjacency: dict[str, list[tuple[str, str]]],
    selections: list[Selection],
    depth_limit: int,
    task_tokens: set[str],
) -> tuple[dict[str, int], dict[str, str]]:
    distances = {selection.node_id: 0 for selection in selections}
    reasons = {selection.node_id: selection.reason for selection in selections}
    queue = deque(selection.node_id for selection in selections)
    while queue:
        current = queue.popleft()
        distance = distances[current]
        if distance >= depth_limit:
            continue
        for neighbor, relation in adjacency.get(current, []):
            # A rule knows its consumers through incoming edges, but loading them all would
            # cross app boundaries. Same asymmetry for a dependency: the target loads what it
            # depends on, never everything that depends on it.
            if relation in {"constrained_by:incoming", "depends_on:incoming"}:
                continue
            if (
                relation in {"consumed_by:incoming", "produced_by:incoming"}
                and nodes[neighbor]["kind"] == "contract"
                and lexical_score(task_tokens, nodes[neighbor]) <= 0
            ):
                continue
            next_distance = distance + 1
            if neighbor in distances and distances[neighbor] <= next_distance:
                continue
            distances[neighbor] = next_distance
            reasons[neighbor] = f"{relation}:{current}"
            queue.append(neighbor)

    return distances, reasons


def document_priority(node: dict[str, Any], distance: int, reason: str) -> tuple[int, int]:
    if distance == 0 and node["kind"] in {"contract", "invariant"}:
        return (0, 0)
    if node["kind"] in {"contract", "invariant"} or reason.startswith("produced_by:"):
        return (1, distance)
    if distance == 0 and node["kind"] == "domain":
        return (1, 0)
    if node["kind"] in {"application", "layer", "system"}:
        return (2, distance)
    return (3, distance)


def open_incident(task: str) -> list[str]:
    """Open objects the task touches — their identity, never their content.

    This is the READ half of the register's gate. Without it the register is consulted only by
    whoever remembers to consult it, and so protects nothing: a session reopens an already
    settled subject and no guard sees it.

    Only the address is emitted. An open object carries what is NOT settled, and pasting its
    body into an ordinary mission would serve it as if it were direction.

    A failure here is RAISED, not swallowed. An earlier version returned an empty list on any
    exception, which made a renamed gate or a changed register field indistinguishable from
    "nothing is open" — the reassuring answer, produced by a broken read half.
    """
    if not task:
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import open_register
    except ImportError as exc:
        raise ContextError(f"open register gate unavailable: {exc}") from exc
    try:
        found = open_register.incident(task)
    except open_register.OpenError as exc:
        raise ContextError(f"open register unreadable: {exc}") from exc
    if not found:
        return []
    rows = [f"| `{branch} #{number}` | {species} | {subject} |" for branch, number, species, subject in found]
    return [
        "",
        "## Open — already engaged or arbitrated on this zone",
        "",
        "**Open before acting**, and only if the line concerns you: a subject reopened "
        "unknowingly is the defect this register exists to prevent. The matter lives in the "
        "fiche, not here — it is **not settled**, and must not be read as direction.",
        "",
        "| Identity | Species | Subject |",
        "|---|---|---|",
        *rows,
    ]


def compact_global_map(nodes: dict[str, dict[str, Any]]) -> str:
    lines = ["## Compact global map"]
    for app_id in nodes["system.root"].get("contains", []):
        app = nodes[app_id]
        if app["kind"] != "application":
            continue
        domains = [
            nodes[child]["label"].split("—", 1)[-1].strip()
            for child in app.get("contains", [])
            if nodes[child]["kind"] == "domain"
        ]
        status = "skeleton" if app.get("status") == "skeleton" else "filled"
        lines.append(f"- **{app['label']}** ({status}) : " + " · ".join(domains))
    return "\n".join(lines)


def compile_context(
    data: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    task: str,
    target_path: str | None,
    explicit: list[str],
    budget_tokens: int,
    depth: int,
    max_targets: int,
    include_bootstrap: bool,
    manifest_only: bool,
) -> tuple[str, set[str]]:
    selections = choose_targets(data, nodes, task, target_path, explicit, max_targets)
    task_tokens = tokens(task) - set(app_aliases(nodes))
    distances, reasons = expand(nodes, graph(nodes), selections, depth, task_tokens)

    candidates: list[tuple[tuple[int, int], str, str, str]] = []
    if include_bootstrap:
        for doc in data["startup_docs"]:
            candidates.append(((-1, 0), doc, "bootstrap", "startup"))
    targeted_docs = target_documents(target_path)
    required_docs = {doc for doc, _ in targeted_docs}
    for doc, reason in targeted_docs:
        candidates.append(((-2, 0), doc, "target", reason))
    for node_id, distance in distances.items():
        node = nodes[node_id]
        for doc in node["docs"]:
            candidates.append((document_priority(node, distance, reasons[node_id]), doc, node_id, reasons[node_id]))

    # A document is paid for once, with its best reason.
    best: dict[str, tuple[tuple[int, int], str, str]] = {}
    for priority, doc, node_id, reason in candidates:
        if doc not in best or priority < best[doc][0]:
            best[doc] = (priority, node_id, reason)
    ordered_docs = sorted(
        ((priority, doc, node_id, reason) for doc, (priority, node_id, reason) in best.items()),
        key=lambda item: (item[0], item[1]),
    )

    base_lines = [
        "# Compiled context",
        "",
        f"- **Task**: {task or '(not supplied)'}",
        f"- **Target path**: {target_path or '(not supplied)'}",
        f"- **Budget**: {budget_tokens} estimated tokens (conservative bound: 3 chars/token)",
        f"- **Graph depth**: {depth}",
        f"- **Boot**: {'included' if include_bootstrap else 'assumed already loaded via AGENTS.md'}",
        "",
        compact_global_map(nodes),
        *open_incident(task),
        "",
        "## Subgraph",
        "",
        "| Distance | Kind | Node | Reason |",
        "|---:|---|---|---|",
    ]
    for node_id in sorted(distances, key=lambda item: (distances[item], item)):
        base_lines.append(
            f"| {distances[node_id]} | {nodes[node_id]['kind']} | `{node_id}` | `{reasons[node_id]}` |"
        )

    implementation_paths = sorted({
        raw for node_id in distances for raw in nodes[node_id].get("code", [])
    })
    base_lines.extend(["", "## Candidate implementation", ""])
    base_lines.extend(f"- `{raw}`" for raw in implementation_paths)
    if not implementation_paths:
        base_lines.append("- none — give a task or a path")

    # Reserve the manifest and the source headers before choosing bodies. Without that
    # reserve the budget counted only the Markdown, and could be blown by its own view.
    used = token_estimate("\n".join(base_lines)) + 150 + 80 * len(ordered_docs)
    included: list[tuple[str, str, str, str, int]] = []
    skipped: list[tuple[str, int]] = []
    contents: dict[str, str] = {}
    for _, doc, node_id, reason in ordered_docs:
        content = repo_path(doc).read_text(encoding="utf-8")
        contents[doc] = content
        cost = token_estimate(content)
        if used + cost > budget_tokens:
            if doc in required_docs:
                raise ContextError(
                    f"budget {budget_tokens} too small for the mandatory target {doc}"
                )
            skipped.append((doc, cost))
            continue
        used += cost
        kind = "target" if node_id == "target" else nodes.get(node_id, {}).get("kind", "startup")
        included.append((doc, node_id, reason, kind, cost))

    def render(with_bodies: bool, total: int) -> str:
        lines = base_lines + [
            "", "## Documentary manifest", "",
            "| Estimated tokens | Kind | Source | Selection |",
            "|---:|---|---|---|",
        ]
        for doc, node_id, reason, kind, cost in included:
            lines.append(f"| {cost} | {kind} | `{doc}` | `{node_id}` · `{reason}` |")
        for doc, cost in skipped:
            lines.append(f"| {cost} | **dropped — budget** | `{doc}` | — |")
        lines.extend(["", f"**Estimated total: {total} / {budget_tokens} tokens.**"])
        if with_bodies:
            for doc, _, _, _, _ in included:
                lines.extend(["", f"## Source: `{doc}`", "", contents[doc].rstrip()])
        return "\n".join(lines) + "\n"

    def actual_estimate() -> int:
        estimate = token_estimate(render(True, 0))
        # The figure counts itself; two passes suffice, three make the intent explicit.
        for _ in range(3):
            revised = token_estimate(render(True, estimate))
            if revised == estimate:
                break
            estimate = revised
        return estimate

    actual = actual_estimate()
    while actual > budget_tokens and included:
        removable = next(
            (index for index in range(len(included) - 1, -1, -1) if included[index][0] not in required_docs),
            None,
        )
        if removable is None:
            break
        doc, _, _, _, cost = included.pop(removable)  # last non-required is lowest priority
        skipped.append((doc, cost))
        actual = actual_estimate()
    if actual > budget_tokens:
        raise ContextError(
            f"budget {budget_tokens} too small for the manifest alone ({actual} estimated tokens)"
        )

    return render(not manifest_only, actual), set(distances)


def self_check(data: dict[str, Any], nodes: dict[str, dict[str, Any]]) -> None:
    """Sentinel selections, run twice and compared.

    A ranking that depends on dict iteration order is right in testing and wrong once, later,
    for one user. Determinism is therefore asserted, not assumed. Each case also names what
    must NOT be selected: a selector that reaches the right node while dragging in another
    app's subgraph is correct and useless.
    """
    cases = [
        ("fix account storage", "app_notes/src/platform.py", "domain.notes.platform", set()),
        ("change the note listing order", "app_notes/src/catalog.py", "domain.notes.catalog",
         {"domain.ledger.platform"}),
        ("edit the context map yaml", "_direction/cartes/system-map.yaml",
         "invariant.addressable-context", set()),
        ("document the account api contract between the two apps", None,
         "contract.notes.account-api", set()),
        ("prove that a guard turns red", None, "invariant.proof-of-guards", set()),
    ]
    for task, path, expected, forbidden in cases:
        first = choose_targets(data, nodes, task, path, [], 3)
        second = choose_targets(data, nodes, task, path, [], 3)
        if first != second:
            raise ContextError(f"non-deterministic selection for {task!r}")
        selected = {item.node_id for item in first}
        if expected not in selected:
            raise ContextError(
                f"selection test failed for {task!r}: {expected} absent from {sorted(selected)}"
            )
        leaked = selected & forbidden
        if leaked:
            raise ContextError(f"partitioning test failed for {task!r}: {sorted(leaked)}")

    # Naming one app must not open the other's subgraph. This is the case that would silently
    # regress if the alias table were ever hard-coded again and left incomplete.
    _, notes_subgraph = compile_context(
        data=data,
        nodes=nodes,
        task="change the note listing order in the notes catalog",
        target_path=None,
        explicit=[],
        budget_tokens=24000,
        depth=1,
        max_targets=3,
        include_bootstrap=False,
        manifest_only=True,
    )
    cross_app = sorted(
        node_id for node_id in notes_subgraph if node_application(node_id) == "ledger"
    )
    if cross_app:
        raise ContextError("undue cross-app expansion on the notes case: " + ", ".join(cross_app))

    # Targeting one level-4 fiche must also bring its module's README: the fiche carries the
    # concept, the README carries the local ontology that makes the concept readable.
    detail = "app_notes/_technique/platform/CONC_account-api.md"
    compiled, detail_subgraph = compile_context(
        data=data,
        nodes=nodes,
        task="check the account seam",
        target_path=detail,
        explicit=[],
        budget_tokens=24000,
        depth=1,
        max_targets=3,
        include_bootstrap=False,
        manifest_only=True,
    )
    required = {detail, "app_notes/_technique/platform/README.md"}
    absent = sorted(doc for doc in required if f"`{doc}`" not in compiled)
    if absent:
        raise ContextError("target or documentary owner omitted: " + ", ".join(absent))
    if "contract.notes.account-api" not in detail_subgraph:
        raise ContextError("ontological owner of the target absent from the subgraph")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--task", default="", help="free-form description of the task")
    result.add_argument("--path", dest="target_path", help="targeted file or folder, relative to the repository root")
    result.add_argument("--node", action="append", default=[], help="explicit target node (repeatable)")
    result.add_argument("--budget-tokens", type=int, help="total estimated budget")
    result.add_argument("--depth", type=int, choices=(0, 1, 2), help="graph expansion distance")
    result.add_argument("--max-targets", type=int, choices=range(1, 6), help="maximum number of targets")
    result.add_argument("--include-bootstrap", action="store_true", help="include sources already called by AGENTS.md")
    result.add_argument("--manifest-only", action="store_true", help="do not concatenate the Markdown bodies")
    result.add_argument("--validate", action="store_true", help="validate the map only")
    result.add_argument("--check", action="store_true", help="validate and run the deterministic tests")
    result.add_argument("--map", dest="map_path", type=Path, default=DEFAULT_MAP, help="YAML map to use")
    result.add_argument("--schema", dest="schema_path", type=Path, default=DEFAULT_SCHEMA, help="YAML schema to use")
    return result


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        data, nodes = validate_map(args.map_path.resolve(), args.schema_path.resolve())
        if args.check:
            self_check(data, nodes)
            edge_count = sum(len(edges) for edges in graph(nodes).values()) // 2
            print(f"context-map: {len(nodes)} nodes, {edge_count} relations, deterministic tests OK")
            return 0
        if args.validate:
            print(f"context-map: {len(nodes)} conformant nodes")
            return 0

        defaults = data["defaults"]
        budget = args.budget_tokens or defaults["budget_tokens"]
        depth = defaults["expansion_depth"] if args.depth is None else args.depth
        max_targets = args.max_targets or defaults["max_targets"]
        if budget < 1000:
            raise ContextError("the budget must be at least 1000 tokens")
        output, _ = compile_context(
            data=data,
            nodes=nodes,
            task=args.task,
            target_path=args.target_path,
            explicit=args.node,
            budget_tokens=budget,
            depth=depth,
            max_targets=max_targets,
            include_bootstrap=args.include_bootstrap,
            manifest_only=args.manifest_only,
        )
        sys.stdout.write(output)
        return 0
    except ContextError as exc:
        print(f"context-compile: ERROR — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
