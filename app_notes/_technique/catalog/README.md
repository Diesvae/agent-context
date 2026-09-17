# catalog — what a reader browses, and in what order

**Purpose** — turn the store's slugs into a list a reader can browse, and a note into
something rendered. It owns ordering; it owns no storage.

**Code** : `app_notes/src/catalog.py`

## State

`list_notes()` filters slugs by prefix and returns them in a **stable** order. The stability
is the point, not a detail: an unstable listing makes every downstream diff unreadable, and a
reviewer who cannot read a diff stops reading diffs.

`render_note()` returns the note body, promoting its first line to a heading when the body has
none. It reads through the store rather than the filesystem, so the "everything that persists
goes through platform" rule stays true by construction instead of by discipline.

## Renvois

- Store: [`../platform/README.md`](../platform/README.md).
- Invariant above: [`../../../_direction/2_app-conventions/module-boundaries.md`](../../../_direction/2_app-conventions/module-boundaries.md).
