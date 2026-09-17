# Design spirit

**Invariant** — this repository is written so that an agent arriving **cold** can rebuild the
frame before acting, and cannot break an invariant without saying so. Everything else here is
a consequence of that one sentence.

**Scope** — the whole repository.

## State

Three properties follow, and they constrain each other:

**Selective, therefore bounded.** A context that its own size makes unreadable protects
nothing. Every level above the app has a selector that carries each fiche's invariant in one
line; the fiches themselves are opened only to change what they govern. Loading everything is
not thoroughness, it is the failure this system was built after.

**Separated by nature, therefore stable.** Four kinds of text, four homes: what is **true**
(the state fiche), **how we got there** (the journal), **the transferable lesson** (memory),
and **what is not settled** (the open register). Mixed into one paragraph they grow without
bound and the invariant at the top of a fiche ends up contradicted by prose underneath it.
Separated at the moment of writing, each one stays the size it needs to be.

**Mechanically proven, therefore trustworthy.** A documentation rule that only a human checks
is a rule that is true on the day it is written. Every rule here is executed by a linter, and
every linter rule has been broken on purpose to prove it can fire. A doc that describes code
**is** code: it expires in silence, and nothing turns red unless something checks.

## The golden rule

A conflict between a request and an invariant is **reported, not executed**. The wording
matters, because the useful move is not refusal: state which fiche holds the rule, what the
rule is, and ask whether the direction is being changed deliberately. A direction changes by a
fiche being updated and a dated journal entry being written — never by being worked around.

## What this is not

Not a style guide, and not a prompt. It makes no claim about how to write software; it is a
way of holding decisions so that the next reader — human or agent, weeks later — loads the few
that bind them and can see that they are binding.

## Links

- Method and reading order: [`../00_PROTOCOLE.md`](../00_PROTOCOLE.md).
- Branch status: [`../00_CARTE.md`](../00_CARTE.md).
