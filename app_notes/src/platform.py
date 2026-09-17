"""Storage and identity for the Notes example app.

This module exists so that the documentation rules of this repository have real code to be
wrong about. A doc that describes code IS code: it expires in silence, and nothing turns red
unless something checks. R14 checks, in both directions, against the symbols defined here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class NoteStore:
    """A directory of Markdown notes, addressed by slug."""

    root: Path
    _index: dict[str, Path] = field(default_factory=dict)

    def refresh(self) -> int:
        self._index = {path.stem: path for path in sorted(self.root.glob("*.md"))}
        return len(self._index)

    def read(self, slug: str) -> str:
        try:
            return self._index[slug].read_text(encoding="utf-8")
        except KeyError as exc:
            raise KeyError(f"unknown note: {slug}") from exc

    def slugs(self) -> list[str]:
        return sorted(self._index)


def open_store(root: str | Path) -> NoteStore:
    """Open a store and index it once, so callers never see a half-built index."""
    store = NoteStore(root=Path(root))
    store.refresh()
    return store
