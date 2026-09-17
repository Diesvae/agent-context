# platform — the ledger's future seam

**Status** — SKELETON. Declared before any code exists, so the dependency on the Notes
account API is visible in the map today rather than discovered at integration.

## State

This module will consume [`contract.notes.account-api`](../../../app_notes/_technique/platform/CONC_account-api.md)
and nothing else of the Notes app. The map already records that edge; the code does not exist.

Declaring a consumer before writing it is what makes the contract's blast radius honest. A
consumer that appears only in code is invisible to impact analysis until it breaks.

## Renvois

- Contract consumed: [`../../../app_notes/_technique/platform/CONC_account-api.md`](../../../app_notes/_technique/platform/CONC_account-api.md).
