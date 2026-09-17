# The open register

**Invariant** — what is **not settled** is a nature of text in its own right, at the same rank
as state, journal and memory. It lives in `<branch>/open/`, **one fiche per object**, and never
inside a state fiche. A state fiche that carries an open question has two readings — what is
true, and what is merely considered — and a reader cannot tell them apart.

**Scope** — every branch of the directing context.

## State

Two species, and the distinction is the whole taxonomy: a **workstream** closes by being
finished, an **arbitration** closes by a decision being made. Asking which one an object is
forces the question "what would end this?", which is exactly the question an untracked open
item never gets asked.

Every open fiche opens on `**Open**` — as a state fiche opens on `**Invariant**` and a level-4
fiche on `**Purpose**`. Without that marker nothing distinguishes an open fiche from a state
fiche that wandered into the folder, and the rules that check state fiches stop looking here.

An open fiche **must** date its measurements. This is the exact inverse of the state rule, and
it is not an inconsistency: a state fiche says only what is true now, so a date in it is an
un-rewritten reversal; an open fiche says what was observed and not yet concluded, and the
date is what makes it re-examinable. Its bound against accumulation is different too — it
does not get trimmed, it **disappears at closure**.

## The register is read before new work, never at boot

[`cartes/open.yaml`](../cartes/open.yaml) carries **every** object of **every** branch, reduced
to its identity. That breadth is deliberate. Split per branch, a reader must first decide
whether their subject is cross-cutting or app-local — and that frontier is a property of the
**object**, which is what they are trying to look up. Getting it wrong makes "found nothing"
indistinguishable from "nothing exists", and the subject gets reopened from scratch.

## Closure moves, it does not annotate

A finished object is **moved** under `open/archive/` by the register's own gate. Marking it
done in place leaves it to be re-read forever, and the mark is the cheapest thing in the file
to get wrong. The gate matters more than it looks: a procedure with correct state, a correct
rule and nothing joining them to the next gesture is not a procedure — it is a hope. The
vocabulary of closure is also **open-ended in practice**: a guard that greps for `DONE`,
`CLOSED` and `FINISHED` passes green over `shipped`, and passing green is the failure mode
that costs, because it is the one nobody investigates.

## Links

- Gate: [`scripts/open_register.py`](../../scripts/open_register.py) — `--new`, `--close`, `--verify`.
- Guard: R9 in [`scripts/doc-lint.sh`](../../scripts/doc-lint.sh).
- Example: [`../app_notes/open/`](../app_notes/open/) holds one live object.
