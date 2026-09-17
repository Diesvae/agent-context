# platform — storage, identity and the app's seam

**Purpose** — hold the note store and the single address by which another app reads an
account here. Everything that persists passes through this module; nothing else in the app
touches the filesystem.

**Code** : `app_notes/src/platform.py`

## State

`NoteStore` is the store itself: a directory of Markdown notes indexed by slug. It indexes on
`refresh()` and answers `read()` and `slugs()` from that index, so a caller never pays a
directory walk per note.

`open_store()` is the only constructor callers should use. It builds the store **and** indexes
it before returning, because a store handed back un-indexed answers `slugs()` with an empty
list — an empty catalog and a missing directory then look identical to the caller, and the
second is a bug while the first is a legitimate state.

The seam to other apps is not described here: it has its own fiche, because a contract that
lives inside a module README gets rewritten whenever the module is refactored, and the other
side of the seam never hears about it.

## Renvois

- [`CONC_account-api.md`](CONC_account-api.md) — the contract this module produces.
- [`../catalog/README.md`](../catalog/README.md) — the one consumer inside this app.
- Invariant above: [`../../../_direction/1_infrastructure/proof-of-guards.md`](../../../_direction/1_infrastructure/proof-of-guards.md).
