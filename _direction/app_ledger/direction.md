# Ledger — direction

**Status** — SKELETON. Structure posted, no code written. This branch is empty **on purpose**:
a system demonstrated only on its filled branch proves nothing about how it treats an empty
one, and in practice the empty branch is where a register silently holds no entry at all.

**Scope** — this app.

## State

One domain declared, `platform/`, which will consume the Notes account API and nothing else of
that app. The edge exists in the context map today, before the code, so the contract's blast
radius is honest now rather than discovered at integration.

Declaring a consumer before writing it costs one line and buys the only thing that makes an
impact analysis trustworthy: a consumer that appears only in code is invisible until it breaks.

## Links

- Level 4: [`../../app_ledger/_technique/README.md`](../../app_ledger/_technique/README.md).
- Contract consumed: [`../app_notes/direction.md`](../app_notes/direction.md).
