"""Listing and rendering the notes a reader browses."""

from __future__ import annotations

from .platform import NoteStore


def list_notes(store: NoteStore, prefix: str = "") -> list[str]:
    """Slugs under an optional prefix, in a stable order.

    The order is stable because an unstable listing makes every downstream diff unreadable,
    and a reviewer then stops reading diffs at all.
    """
    return [slug for slug in store.slugs() if slug.startswith(prefix)]


def render_note(store: NoteStore, slug: str) -> str:
    """The note's body with its title line promoted to a heading, if it has none."""
    body = store.read(slug).strip()
    if body.startswith("#"):
        return body
    return f"# {slug}\n\n{body}"
