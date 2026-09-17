# Level 1 — infrastructure invariants

**Selector.** Read this table; open a fiche only to touch its surface. Each line carries the
fiche's **invariant**, not its summary — you cannot select what you do not know exists, and a
table of contents tells you a fiche exists without telling you whether it binds you.

Reading the line is enough to **know a rule exists**, therefore enough to spot a conflict and
apply the golden rule. Opening the fiche is for changing what it governs.

| Fiche | Type | Weight | Invariant — and when to open it |
|---|---|---|---|
| [`addressable-context.md`](addressable-context.md) | architecture | 2.9 KB | The YAML map routes, the Markdown it points at is authoritative; it is checked against the disk for resolving paths, single containment, mapped surfaces and deterministic selection. Open before touching the map, the schema or the compiler. |
| [`open-register.md`](open-register.md) | method | 2.9 KB | What is not settled is a nature of its own: one fiche per object under `<branch>/open/`, dated, never inside a state fiche, closed by moving it. Open before starting new work, or to learn whether a subject was already arbitrated. |
| [`proof-of-guards.md`](proof-of-guards.md) | proof | 2.9 KB | A static guard is worth its proof: every rule is broken on purpose, seen red, restored, and the script that does it is committed. Open before adding a guard, or when a green suite starts feeling too quiet to trust. |

## Weights are measured, not asserted

The `Weight` column is checked by R8 against the file on disk, within 0.15 KB. An announced
weight drifts the moment a fiche is edited, and a selector whose numbers are wrong is worse
than one with no numbers: it is consulted to decide what to load.
