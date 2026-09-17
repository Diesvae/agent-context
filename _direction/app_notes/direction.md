# Notes — direction

**Invariant** — Notes exists to **show** levels 3 and 4 of this system rather than describe
them. It is small on purpose: every rule in the repository must have something real to be
checked against, and a worked example that is too large stops being read.

**Scope** — this app.

## State

Two domains, and the boundary between them is the interesting part: `platform/` owns
everything that persists, `catalog/` owns what a reader browses. Nothing outside `platform/`
touches the filesystem, so the rule holds by construction instead of by discipline.

One contract, `CONC_account-api`, is the **only** surface another app may read. It has its own
fiche rather than a section in the platform README, because a contract that lives inside a
module's README gets rewritten during refactors and the other side of the seam never hears.

No divergence from level 2 is declared. If one becomes necessary it is written **here**, next
to what it affects.

## Links

- Level 4: [`../../app_notes/_technique/README.md`](../../app_notes/_technique/README.md).
- Consumer of its contract: [`../app_ledger/direction.md`](../app_ledger/direction.md).
- Open objects on this branch: [`open/`](open/).
