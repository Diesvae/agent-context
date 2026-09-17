# Module boundaries

**Invariant** — one fiche per **concept**, never per workstream. A fiche split because it grew
is split at a **joint**, and the joint is the unit judged — not the byte count that triggered
the split.

**Scope** — every app's level-4 tree.

## State

A tree filed by workstream is readable for one quarter. After that, the concepts a reader
needs are spread across the three chantiers that happened to touch them, and there is no
fiche that answers "how does this work" — only three that answer "what did we do in March".
The rename cost of fixing it later is what stops it being fixed.

The size ceiling is 25 KB, and it is a **trigger**, not the criterion. When a fiche reaches it,
the question is *where are the seams* — which halves could be read independently, each with
its own opening invariant. A cut made to get under the ceiling, at the nearest paragraph
break, produces two fiches that both have to be read to understand either one: the ceiling is
respected and the reason for the ceiling is defeated.

If no joint exists, the fiche is not too long — the concept is genuinely that size, and the
right move is an explicit, named exemption rather than a cut that damages it.

## A fiche states its identity in its first line

A level-4 fiche opens with `# <filename-stem> — <readable title>`, then `**Purpose**`. The stem
in the title is redundant on purpose: it is what makes a rename visible in the diff of the
file itself, instead of only in the diff of whoever cited it.

## Links

- Sibling: [`documentation-naming.md`](documentation-naming.md) — how the tree is filed.
- Above: [`../1_infrastructure/addressable-context.md`](../1_infrastructure/addressable-context.md).
