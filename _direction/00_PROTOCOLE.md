# Protocol — the directing context

`_direction/` holds the **direction** — why, and the rule that was decided — not the
implementation. Its purpose: that an agent arriving **cold** rebuilds the frame before acting,
and cannot break an invariant in silence.

## What is true is read; how we got there is searched

Founding rule of **reading**. A context that its own size makes unreadable protects nothing.
Every fiche therefore separates two natures, and **only one is read**:

| | **State** — the fiche | **Journal** — `journal/YYYY-MM.md` |
|---|---|---|
| Content | what is true today | the dated entry, in full, verbatim |
| Read at boot | **yes** | no — reached by `grep` |
| Reversals | **resolved**: the state says the last word only | **kept**: that is its purpose |
| Size | **capped at 25 KB** | unbounded |

A third nature lives apart from both: the **open** — what is not settled. It is no more read at
boot than the journal, and it belongs in no state fiche. See
[`1_infrastructure/open-register.md`](1_infrastructure/open-register.md).

A state fiche carries **no dated entry**, anywhere: not "fixed on…", not "reversed on…", not
struck-through text. If the state changed, it is **rewritten**, and the previous wording goes
to the journal.

It carries **nothing** of the journal: no entry, no summary, no index, **not even the
pointer**. The value of a history is **situational**; its cost in a fiche is **permanent**. The
pointer itself is **unique** — the `## Journal` section of [`00_CARTE.md`](00_CARTE.md), which
is always loaded. A sentence repeated in every fiche makes nothing more findable; it is paid
for every time and it diverges. R7 guards both halves: no fiche reopens a journal section, and
the central declaration neither omits nor invents a journal.

## Triage — where what you just learned goes

A piece of work produces **four** natures. Mixing them in one paragraph is what makes a system
swell; separating them **at the moment of writing** is what stops it. The fourth is the easiest
to forget, because it does not present itself as an acquisition: what you did **not** settle
gets written down, or it disappears.

| Nature | Destination |
|---|---|
| **The rule now in force** | the **state**: `**Invariant**` (levels 0–3) · the module's `README.md` or `CONC_` fiche (level 4) |
| **The measurement that justified it** — numbers, counter-examples, what was broken then restored | the **journal** |
| **The transferable lesson** — method, verification trap, pattern reusable elsewhere | **memory** (`memoire/`, one fact per file plus an index) |
| **What is not settled** — work to continue, or a decision to make | the **open**: `<branch>/open/`, **one fiche per object**, plus its register line. Never in a state fiche |

**Memory template** — `memoire/<slug>.md`, **one fact per file**. Frontmatter: `name` (the
slug, kebab-case) · `description` (one line — this is what judges relevance at recall) ·
`metadata.type` among `user` · `feedback` · `project` · `reference`. The body carries the fact;
for `feedback` and `project` it continues with `**Why:**` then `**How to apply:**`. A pointer
between memories is written `[[name]]`, and a **dangling link is legal**: it marks a memory
still to be written. Every memory carries **one line** in `MEMORY.md` — `- [Title](<slug>.md)
— hook` — an index that says **when to open**, never what the memory contains; R11 keeps it
exact in both directions. Before writing: look for the memory that already covers the fact and
update it, rather than creating a twin.

**Corollary that bounds growth**: an entry with nothing to put in the first row is **not** a
direction decision — it is a session report, and it belongs in the journal alone.

## Direction versus technical

| | Direction (`_direction/`, levels 0–3) | Technical (in-app `_technique/`, level 4) |
|---|---|---|
| Object | why, plus the decided rule | how, exhaustively |
| Stability | invariant, never changes in silence | volatile |

The direction **points at** the how; it does not copy it. A fiche that starts detailing code
has spilled into level 4.

## The five levels (general → local)

| Level | Folder | Scope | Answers |
|---|---|---|---|
| 0 | `0_spirit/` | everything | in what spirit all of this is designed |
| 1 | `1_infrastructure/` | everything | the invariants that keep the frame stable and safe |
| 2 | `2_app-conventions/` | every app | how an app's design is normalised |
| 3 | `app_<name>/` | one app | what is specific to that app |
| 4 | `<app>/_technique/` | one **module** | how the module is built, concept by concept |

Each level inherits the ones above. An app does not restate a level-2 rule: it follows it, or
declares its divergence explicitly in its own `direction.md`.

## Start of a mission — reading

In order, and only what is relevant: `0_spirit/` → **`1_infrastructure/README.md`** →
**`2_app-conventions/README.md`** (if an app) → `app_<name>/direction.md` →
`_technique/README.md` then the module concerned, via its links. Build the context before
acting.

For a localised mission, [`scripts/context-compile.py`](../scripts/context-compile.py)
materialises that walk from the task and an optional path. It traverses the canonical map
[`cartes/system-map.yaml`](cartes/system-map.yaml), adds incident contracts and invariants,
then ranks the Markdown under a token budget. Its output is an **explainable selector**, never
a new source of truth: the YAML carries addresses and relations, the Markdown carries meaning.

**Levels 1 and 2 are not read in full.** Their content is **situational**, and the
overwhelming majority of it does not concern a given mission. Each carries a **selector
`README.md`** stating **each fiche's invariant in one line**, and when to open it. Reading the
selector is enough to **know a rule exists** — therefore enough to spot a conflict and apply
the golden rule. You open the fiche only to touch what it governs.

**You cannot select what you do not know exists**: that is why the selector carries the
invariant rather than a table of contents. Fiches stay filed **by degree of generality** — the
level. Type survives as a **column** of the selector, never as a folder: a second filing axis
gives the same concept two plausible homes.

**Never a journal at boot.** A journal is read only in answer to a precise question, and by
`grep`; where to look is declared once, in the `## Journal` section of
[`00_CARTE.md`](00_CARTE.md).

## End of a mission — updating

Apply the **triage** above: the state first (the one fiche concerned), then the journal (the
full dated entry), then memory if the lesson outlives the work, and the **open** for what is
not settled — a new fiche, or an object closed with `open_register.py --close`. Adjust
[`00_CARTE.md`](00_CARTE.md) if a **status** changes — never to narrate the work, which is the
journal's job. Never let code diverge in silence: either the direction is updated (a
deliberate decision) or the code is corrected.

## The golden rule — anti-drift

A conflict between a request and an invariant (levels 0–2) is **reported, not executed**. State
it: "this conflicts with *<fiche>*, which sets *<rule>* — do you want to change that
direction, or have I misread?" A direction changes deliberately, by a fiche being updated,
never by a tacit workaround.

## Fiche template (levels 0–3)

```
# <Subject>
**Invariant** — the rule and why, dense.
**Scope** — everything / every app / this app.
## State   — what is true today, by subject. No dates, nothing struck through.
## Links   — TYPED downward pointers: lower level, _technique/, code, memories.
```

A fiche is short: an invariant fits in a few sentences. **25 KB ceiling**, guard included.
**No open section** — the unsettled has its own home. **No journal section** — not `## Journal`,
nor its old names `## Decisions` / `## Changelog`: the pointer lives once, in `00_CARTE.md`.

The **`00_`** prefix marks the fiches **read at boot**, and nothing else. A `00_` file is bytes
paid on **every** session; adding one is a budget decision, not a filing choice. The budget is
declared and measured in `00_CARTE.md` (R10).

## Level-4 template — domains and modules

`_technique/` is filed on **one axis: the business sub-system**, plus three fixed names
(`orchestration/` · `platform/` · `archive/`). A folder's name is **free**; what binds it is
the `**Code** :` line of its README — code is **declared**, never derived from the name.

Full grammar — fiche prefixes, filing cascade, split threshold, statuses:
[`2_app-conventions/documentation-naming.md`](2_app-conventions/documentation-naming.md).

## The guard

[`scripts/doc-lint.sh`](../scripts/doc-lint.sh) mechanically proves what this protocol
prescribes: size ceilings, canonical opening, no index orphan, no dead pointer — **markdown
links and backtick mentions alike** — no dated entry outside the journal and nothing struck
through (R6), status declared under `archive/`, no journal section in a fiche and a central
declaration exact in both directions (R7), selectors exact in both directions with
**measured** weights and lines bounded at both ends (R8), no closed point in the open register
(R9), boot budget declared and summed (R10), memory index exact both ways (R11), boot aliases
resolving to one content (R12), the context map conformant, addressable and deterministic
(R13). And the **mirror pair** in R14: documentation about vanished code, and code no
documentation mentions. A doc that describes code **is** code — it expires in silence, and
nothing turns red. Run it at the end of a mission; accepted debts are **named** in
`doc-lint.exemptions`, never quietly filtered out.

Every one of those rules has been broken on purpose and seen red:
[`1_infrastructure/proof-of-guards.md`](1_infrastructure/proof-of-guards.md).
