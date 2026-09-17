# CONC_account-api — the only seam between the two apps

**Invariant** — one address, declared here, is the whole surface another app may read. A
second address added elsewhere is not an extension of this contract, it is a second contract
with no owner, and it will drift.

**Portée** — this app and every consumer declared in the context map.

## State

Producer: `domain.notes.platform`. Consumers: `domain.ledger.platform`, and nothing else
until the map says so. The map is what makes that sentence checkable — a consumer that reads
this API without declaring itself is invisible to every impact analysis, and the day the
payload changes, nobody knows who to warn.

The payload is deliberately not restated here. It lives with the producing code, and a
contract fiche that copies a payload becomes a second, older writing of it.

## Renvois

- Producer: [`README.md`](README.md).
- Map: [`../../../_direction/cartes/system-map.yaml`](../../../_direction/cartes/system-map.yaml).
