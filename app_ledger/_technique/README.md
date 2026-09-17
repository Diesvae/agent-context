# Ledger — technical selector

**Status** — SKELETON. The structure is posted; the business modules follow the first line of
code. This branch is empty **on purpose**: a system that only ever shows its filled branch
proves nothing about what it does with an empty one, and "no rule here" is not "nothing
anywhere".

| Domain | Owns | Open when |
|---|---|---|
| [`platform/`](platform/README.md) | where the ledger will read accounts | you wire the ledger to the Notes account API |

## Filing

Same single axis as every app: the business sub-system. A skeleton branch still declares its
domains, because a folder that does not exist is indistinguishable from a domain nobody has
thought about yet — and only one of those two is a decision.
