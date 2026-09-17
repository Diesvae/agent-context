# Documentation naming

**Invariant** — a documentation tree is filed on **one axis**, and the code a folder covers is
**declared**, never derived from its name. A name that encodes a correspondence does not
guarantee it: rename the folder and the derivation still resolves — to nothing, silently.

**Scope** — every app's level-4 tree.

## State

The single axis is the **business sub-system**, plus three fixed names that are not business
domains and would corrupt the axis if treated as such: `orchestration/`, `platform/` and
`archive/`. Any second axis — front/back, layer, workstream — produces a tree where the same
concept has two plausible homes, and the answer to "where does this go?" becomes a matter of
who is filing.

A domain README binds its code with a `**Code** :` line listing paths. That line is what the
guards read, in both directions: a declared path that no longer exists is documentation about
vanished code, and a symbol under a declared path that no fiche mentions is code nobody
documented. The two failures look nothing alike and need separate checks — the first is found
by walking the docs, the second only by walking the code.

Fiche prefixes mark a fiche's **kind**, so a reader knows what they are opening before they
open it: `CONC_` for a contract, `SYS_` for a sub-system, `CMP_` for a component, `REF_` for
a reference table. A prefix is not an address: `CONC_<name>.md` written as a template names no
file, and a guard that treats templates as references reports dead links that are not dead —
or, far worse, is loosened until it reports nothing at all.

## What a name may not carry

Not a date, not a status, not a workstream. Each of those changes while the concept does not,
so each of them turns a rename into the price of telling the truth — and the truth then waits.
Status belongs in the fiche's opening line, where a guard can read it; the workstream belongs
in the journal, which is the only text organised by *when*.

## Links

- Sibling: [`module-boundaries.md`](module-boundaries.md) — when one fiche becomes two.
- Example: [`../../app_notes/_technique/README.md`](../../app_notes/_technique/README.md).
