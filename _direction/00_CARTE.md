# Map of the directing context

**Index and branch status — nothing else.** Read [`00_PROTOCOLE.md`](00_PROTOCOLE.md) first.
The narrative of a piece of work **never lives here**: it lives in the journal of the branch
concerned, and what is not settled lives in that branch's open register.

| Status | Meaning |
|---|---|
| **FILLED** | up to date, authoritative |
| **SKELETON** | structure posted, content to come with the app's own phase |
| **DEFERRED** | reform planned for a later phase |

## `_direction/` — shared (levels 0–3)

| Branch | Level | Status | Content |
|---|---|---|---|
| `0_spirit/` | 0 | FILLED | the spirit in which everything here is designed |
| [`1_infrastructure/`](1_infrastructure/README.md) | 1 | FILLED | **selector** — invariants of the frame |
| [`2_app-conventions/`](2_app-conventions/README.md) | 2 | FILLED | **selector** — conventions holding in every app |
| `app_notes/` | 3 | FILLED | the worked example: two domains, one contract |
| `app_ledger/` | 3 | SKELETON | second app, deliberately empty, so partitioning is testable |

## `_technique/` — in-app (level 4)

| App | Status |
|---|---|
| Notes | FILLED — filed by **domain** (`catalog` · `platform`) |
| Ledger | NORMALISED SKELETON — root selector plus `platform/`; business modules follow the first code |

## Boot (what is read at startup)

This table is the **declaration** of the budget, not a comment: R10 sums its sources and
checks the figure published below. A source added here is bytes paid on every session.

| Source | Loading |
|---|---|
| `AGENTS.md` (root) — the boot file, whatever the tool | **automatic** if the tool reads it, otherwise opened first |
| `00_PROTOCOLE.md` · `00_CARTE.md` | called by the first |
| `0_spirit/design-spirit.md` | first in the reading order |
| `memoire/MEMORY.md` — index of lessons, **when to open** and nothing else | called by the first |
| **selectors** `1_infrastructure/README.md` · `2_app-conventions/README.md` → then only the fiches on the subject | deliberate, by link |

**Declared aliases** — `CLAUDE.md`: a **symlink** to `AGENTS.md`, never a copy (R12 checks).
An alias costs **nothing**: it is the same content under the name a tool expects. Serving one
more tool is a link and a mention here — not a second boot file.

**Boot budget: 22.6 KB** — the seven sources above, summed and guarded by R10, in **decimal KB**
(bytes ÷ 1000, as in R8). The fiches behind the selectors and the **open** register are **not**
in that figure: they load only when opened.

There is no hook and no hidden injection. The boot above is universal; for a localised mission,
`AGENTS.md` explicitly calls the compiler. [`cartes/system-map.yaml`](cartes/system-map.yaml)
is not injected raw: it selects the subgraph, the contracts and the invariants whose Markdown
is authoritative. R13 guards its schema, its paths, its relations and deterministic selection.

## Open

**What is not settled is a nature of its own**, at the same rank as state, journal and memory:
**one fiche per object** under `<branch>/open/`, never in a state fiche. Two species — a
**workstream** closes by being finished, an **arbitration** by a decision being made.

**Not read at boot.** Open [`cartes/open.yaml`](cartes/open.yaml) before new work, or to learn
whether a subject has already been settled: it carries **every** object of **every** branch,
reduced to its identity, so you find it without having to decide first whether the subject is
cross-cutting or app-local — a frontier that is a property of the **object**, and getting it
wrong makes "found nothing" indistinguishable from "nothing exists".

Rule, species, identity, closure and guards:
[`1_infrastructure/open-register.md`](1_infrastructure/open-register.md).

## Journal

The narrative, **never read at boot**: reached by `grep`. A state fiche carries **no pointer**
to it — here it is, unique, and R7 keeps it exact in both directions. Only **branches** are
declared.

| Narrative of | Journal |
|---|---|
| cross-cutting reforms (levels 0–2), the protocol, the guard | [`journal/`](journal/) |
| an app — its direction **and** its `_technique/` | [notes](app_notes/journal/) · [ledger](app_ledger/journal/) |
