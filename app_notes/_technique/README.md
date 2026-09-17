# Notes — technical selector

**Purpose** — route to the module that owns a concept. This file is an index, not a summary:
it says *what each domain owns* and *when to open it*, so a mission opens one README instead
of reading the tree.

Level 4 answers *how, exhaustively*. The *why* and the decided rule live one level up, in
[`../../_direction/app_notes/direction.md`](../../_direction/app_notes/direction.md). A fiche
here that starts explaining why is drifting upward; a fiche up there that starts listing
functions is drifting down.

| Domain | Owns | Open when |
|---|---|---|
| [`platform/`](platform/README.md) | storage, identity, the seam every other domain crosses | you touch persistence, accounts, or the cross-app contract |
| [`catalog/`](catalog/README.md) | listing, ordering and rendering notes for a reader | you touch what a reader browses or the order they see it in |

## Filing

One axis: the business sub-system. Folder names are free; what binds a folder is the
`**Code** :` line of its README — the code is **declared**, never derived from the name.
Deriving it reads as a guarantee and is not one: rename the folder and the derivation still
resolves, to nothing.
