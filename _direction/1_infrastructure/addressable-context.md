# Addressable context

**Invariant** — the YAML map **routes**; the Markdown it points at is **authoritative**. The
map carries addresses, kinds and relations so a mission can compile the subgraph it needs.
The moment it carries meaning, that meaning is a second writing of a fact already written in
a fiche, and the two will diverge — silently, because nothing compares them.

**Scope** — the whole repository.

## State

The map is [`cartes/system-map.yaml`](../cartes/system-map.yaml), validated against
[`cartes/schema.yaml`](../cartes/schema.yaml) with `additionalProperties: false` at every
level. A closed schema is the cheap half of the guarantee: it stops a field being invented,
which is how a map starts holding meaning.

The expensive half is that the map is checked against the **disk**. Four properties, each of
which has failed somewhere before being checked:

- **Every path resolves.** A node whose `docs` names a moved fiche routes a mission to
  nothing, and the mission proceeds without the rule it was supposed to load.
- **Every node is reachable from `system.root`, through exactly one containment parent.** Two
  parents make "which app owns this?" unanswerable; zero makes the node unreachable while
  still passing schema validation.
- **Every required surface is mapped.** Each cross-cutting invariant fiche, each app root and
  each active domain README must appear in some node's `docs`. Without this, adding a fiche
  and forgetting the map is invisible: the fiche exists, nothing points at it, and it is never
  loaded again.
- **Selection is deterministic.** The compiler runs sentinel tasks twice and compares. A
  ranking that depends on dict order is right in testing and wrong once, later, for one user.

The grain is the **domain**, never the fiche. At fiche grain the map becomes a table of
contents that must be maintained in lockstep with the corpus — the maintenance cost is
permanent and the routing gain is nil, because a domain README already names its fiches.

## Why a compiler rather than a convention

Reading order can be written down. Written down, it is followed by whoever remembers it. The
compiler makes the same order **produce an artefact**: a selector that names which sources
were chosen, why each was chosen, and what the estimated budget is. A selector that cannot
explain its own choice is indistinguishable from a guess, and it is trusted anyway.

Its output is a **selector, never a new source of truth**. It concatenates or lists Markdown
that already exists; it never paraphrases it. A compiler that summarised would produce a
third writing of every fact, refreshed on each run, authoritative-looking and stale.

## Links

- Code: [`scripts/context-compile.py`](../../scripts/context-compile.py).
- Guard: R13 in [`scripts/doc-lint.sh`](../../scripts/doc-lint.sh) runs `--check`.
- Below: [`proof-of-guards.md`](proof-of-guards.md) — why `--check` is itself proven.
