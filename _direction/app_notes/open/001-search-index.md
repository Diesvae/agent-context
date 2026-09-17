# Search over note bodies — index shape not chosen

**Open** — `app_notes #1` · workstream

## What is not settled

Searching note **bodies** needs an index. Three shapes are plausible and the choice is not
made: scan on read, a prefix trie built at `refresh()`, or an inverted index persisted beside
the notes. Nothing in the app depends on the answer yet, which is exactly why it is written
here rather than decided in passing.

## Measured so far

**2026-09-17** — on the 41 notes of the local corpus, a naive scan of every body answers in
about 6 ms. At that size the question is not performance, so any measurement arguing from
speed today is arguing from the one regime where all three options are indistinguishable.

**2026-09-17** — the corpus grows by roughly 3 notes a week. A linear scan stays under 50 ms
past a thousand notes, which is years away. The real constraint is therefore **not** latency
but whether `refresh()` stays the single indexing point — a persisted index adds a second
place where staleness can live, and staleness in a search index is invisible to the reader.

## What would end this

A decision, recorded as an invariant in the platform module, once either the corpus passes a
scale where a scan is felt, or a second indexing point becomes necessary for another reason.
Until then the cheapest shape holds, and this fiche is the reason that is a choice rather than
an oversight.

## Links

- Module concerned: [`../../../app_notes/_technique/platform/README.md`](../../../app_notes/_technique/platform/README.md).
- Rule: [`../../1_infrastructure/open-register.md`](../../1_infrastructure/open-register.md).
