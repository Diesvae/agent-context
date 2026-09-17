---
name: declared-beats-derived
description: A name that encodes a correspondence does not guarantee it; renames break it silently.
metadata:
  type: feedback
---

Deriving a relation from a name — this folder documents the module of the same name, this
fiche covers the class its filename spells — reads like a guarantee and is not one. Rename
either side and the derivation still resolves, to nothing. Nothing turns red, because there was
never an assertion, only a convention that happened to hold.

**Why:** the failure is invisible by construction. A declared relation can be checked in both
directions: a declared path that no longer exists is documentation about vanished code, and a
symbol under a declared path that no document mentions is code nobody documented. A derived
relation can be checked in neither, because there is nothing to compare against.

**How to apply:** write the correspondence down as data — a `**Code** :` line, a map entry, an
explicit list — and check it against the disk in both directions. When a rename is planned,
grep for path literals in guards and CI before renaming: a guard anchored on a literal path
dies quietly, and an exemption anchored on one quietly lifts. See
[[a-green-guard-may-be-dead]].
