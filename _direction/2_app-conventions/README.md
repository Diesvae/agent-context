# Level 2 — conventions for every app

**Selector.** Conventions that hold in **every** app. An app does not restate a rule from this
level: it follows it, or declares its divergence explicitly in its own `direction.md`. A rule
restated is a rule that will be edited in one place only.

| Fiche | Type | Weight | Invariant — and when to open it |
|---|---|---|---|
| [`documentation-naming.md`](documentation-naming.md) | convention | 2.2 KB | One filing axis — the business sub-system — and the code a folder covers is declared in its `**Code** :` line, never derived from the folder name. Open before creating a folder, a fiche prefix or a domain. |
| [`module-boundaries.md`](module-boundaries.md) | convention | 1.7 KB | One fiche per concept, never per workstream; the 25 KB ceiling is a trigger to look for a joint, and a cut made at the nearest paragraph defeats the reason for the ceiling. Open when a fiche approaches its ceiling. |

## Divergence is declared where it applies

A divergence lives in the app's `direction.md`, next to what it affects — not here. Collected
centrally, exceptions become a second rulebook that nobody reads alongside the first.
