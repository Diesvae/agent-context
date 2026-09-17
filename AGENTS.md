# Boot — the directing context

This repository carries a **directing-context system**: a way of holding decisions so that an
agent arriving cold loads the few that bind the task at hand, and cannot break one in silence.
`app_notes/` and `app_ledger/` are a worked example, not a product.

## This file has several names

`AGENTS.md` is the **only** boot file. The names tools expect — today `CLAUDE.md` — are
**symlinks** to it: one content, so no divergence is possible. Never make a regular copy: two
boot files are two directions. Serving one more tool means adding a link **and** recording it
in the alias declaration of [`_direction/00_CARTE.md`](_direction/00_CARTE.md); R12 checks
both.

## Before any mission

1. Read [`_direction/00_PROTOCOLE.md`](_direction/00_PROTOCOLE.md) — method, reading order and
   the golden rule are all there.
2. Branch status: [`_direction/00_CARTE.md`](_direction/00_CARTE.md).
3. Levels 1 and 2 **are not read in full**: their `README.md` is a **selector** carrying each
   fiche's invariant in one line. Open a fiche only to touch what it governs.
4. Read [`_direction/memoire/MEMORY.md`](_direction/memoire/MEMORY.md) — the index of
   accumulated lessons: it says **when to open** one, never what it contains.
5. For a localised mission, compile the subgraph with
   `python3 scripts/context-compile.py --task '<mission>' --path <target> --manifest-only`,
   then open the sources it selected. With no known path, omit `--path`. The YAML routes; the
   Markdown it designates is authoritative.

## The golden rule

A conflict between a request and an invariant (levels 0–2) is **reported**, not executed.
State which fiche holds the rule and what the rule is, and ask whether the direction is being
changed deliberately. A direction changes consciously — fiche updated, dated journal entry —
never by a workaround.

## At the end of a mission

Apply the protocol's **triage** (state / journal / memory / **open**), adjust
`00_CARTE.md` if a **status** changes, run `bash scripts/doc-lint.sh`, then commit.

A rule you add to the guard is not finished until it has been seen **red**: add its case to
`scripts/prove-guards.sh`. A rule that has never failed proves only that it does not
false-positive.
