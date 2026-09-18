# Agent Context

A **directing-context system** for repositories worked on with coding agents: a way of holding
decisions so that an agent arriving cold loads the few that bind the task at hand — and cannot
break one in silence.

It is documentation infrastructure, not a prompt library and not a style guide. Four small
tools, fourteen guard rules, and a filing discipline that makes the guard rules possible.

```
python3 scripts/context-compile.py --task 'fix account storage' \
                                   --path app_notes/src/platform.py --manifest-only
bash scripts/doc-lint.sh        # 14 rules over the corpus
bash scripts/prove-guards.sh    # breaks each rule on purpose, checks it turns red
```

## The problem

A repository accumulates decisions. They end up in three bad places: nowhere, in a 300 KB
document nobody reads, or in prose that contradicts the code without anything turning red.
Agent-assisted work makes all three worse — an agent reads what you point it at, infers the
rest, and is confidently wrong in the places you did not point.

Two failures do the damage, and both are silent:

- **Context that cannot be selected.** A rule you do not know exists cannot be followed. Once
  the corpus is too large to read whole, "read the docs" stops being an instruction.
- **Documentation that has quietly expired.** A doc that describes code **is** code: it goes
  stale on its own, and nothing fails. The staler it is, the more confidently it is quoted.

## What this repository does about it

**Selectors carry invariants, not titles.** Levels 1 and 2 are never read in full. Each has a
`README.md` stating every fiche's invariant in one line, with its measured weight. Reading the
selector is enough to know a rule *exists* — therefore enough to spot a conflict — and you open
the fiche only to change what it governs.

**Four natures of text, four homes.** What is **true** (the state fiche), **how we got there**
(the journal), **the transferable lesson** (memory), **what is not settled** (the open
register). Mixed in one paragraph they grow without bound; separated at the moment of writing,
each stays the size its purpose needs. The fourth is the one that normally vanishes, because
failing to decide does not feel like something learned.

**A map that routes, and Markdown that is authoritative.** `_direction/cartes/system-map.yaml`
carries addresses, kinds and relations at **domain** grain. `context-compile.py` walks it from
a task and an optional path and emits an **explainable selector**: which sources were chosen,
why each one, and the estimated token cost. It never paraphrases — a compiler that summarised
would create a third writing of every fact, refreshed on each run and authoritative-looking.

**Every rule proven red.** The guard is 14 rules. `prove-guards.sh` breaks each one on purpose
on a copy of the tree, asserts the run goes non-zero **and that this rule's own green line
disappears**, restores, and asserts green again. That second assertion is the point: a mutation
caught by *some other* rule reports success and leaves the intended guard untested.

## The fourteen rules

| # | Rule |
|---|---|
| R1 | No state fiche exceeds 25 KB |
| R2 | Canonical opening — title plus `**Invariant**` / `**Purpose**` / `**Status**` |
| R3 | No dead pointer — markdown links **and** backtick mentions alike |
| R4 | Every archived fiche declares its status; none in force loiters under `archive/` |
| R5 | No orphan fiche — every fiche is reachable from an index |
| R6 | No dated entry and nothing struck through outside the journal |
| R7 | The journal pointer is unique and central, exact in both directions |
| R8 | Selectors exact both ways, lines bounded at 160–360 chars, weights measured |
| R9 | The open register — exact in three senses, no closed point, canonical opening |
| R10 | Boot budget declared, summed and verified; memory index under its reading ceiling |
| R11 | Memory index exact in both directions |
| R12 | Portable boot — one content, declared aliases that resolve to it |
| R13 | Context map — schema, paths, graph and deterministic selection |
| R14 | Code and doc mirror each other — declared paths live, defined symbols cited |

Two of those deserve a note, because they are the ones that catch real drift:

**R14 is a mirror pair.** One half walks the docs and finds documentation about vanished code.
The other walks the code and finds public symbols no fiche mentions. They look nothing alike
and need separate checks — and no folder-name convention could see either, because a name that
encodes a correspondence does not guarantee it. So the code a module covers is **declared**, in
a `**Code** :` line, never derived.

**R8 bounds the selector line at both ends.** Under 160 characters it degrades into a table of
contents and stops carrying the invariant; over 360 it becomes a summary, and the selector
starts costing what it was built to save.

Accepted debts go in `scripts/doc-lint.exemptions` with their reason. They do not fail the run;
they are counted and printed. A rule that can be silenced by editing a filter has an
undocumented off switch.

## The five levels

| Level | Folder | Scope | Answers |
|---|---|---|---|
| 0 | `_direction/0_spirit/` | everything | in what spirit all of this is designed |
| 1 | `_direction/1_infrastructure/` | everything | invariants that keep the frame stable |
| 2 | `_direction/2_app-conventions/` | every app | how an app normalises its own design |
| 3 | `_direction/app_<name>/` | one app | what is specific to that app |
| 4 | `<app>/_technique/` | one module | how the module is built, concept by concept |

Each level inherits the ones above. An app does not restate a level-2 rule: it follows it, or
declares its divergence in its own `direction.md`.

`app_notes/` and `app_ledger/` are a **worked example**, not a product. Notes is filled — two
domains, one contract, real code. Ledger is a skeleton **on purpose**: a system demonstrated
only on its filled branch proves nothing about how it treats an empty one, and the empty branch
is exactly where a register silently holds no entry at all.

## Adopting it

1. Copy `_direction/` and `scripts/`, and keep `AGENTS.md` at the root with your tool's
   expected name as a **symlink** to it — never a copy. Two boot files are two directions, and
   R12 exists because that failure is otherwise invisible.
2. Replace the example branches with your own. Declare each app in
   `_direction/cartes/system-map.yaml`; the compiler derives its alias table from that file, so
   nothing about your repository lives in the code.
3. Run `doc-lint.sh`. It will be red — that is the point. Every violation is named with its
   file.
4. When you add a rule, add its case to `prove-guards.sh`. A rule that has never been seen red
   proves only that it does not false-positive.

Requirements: Python 3.10+, `pyyaml`, `jsonschema`, and GNU coreutils with `bash`. No network,
no build step, no service. On this corpus the guard runs in about 2 seconds and the full proof
campaign — 14 rules, each mutated, checked and restored on a copy of the tree — in under a
minute.

## Honest limits

- **Extracted from a private monorepo**, where it runs over five applications and a corpus far
  larger than this one. The **form** is here — protocol, map, selectors, guards, worked example.
  The content is not: app fiches, the journal and the accumulated memory corpus stay private.
- **Upstream has eighteen rules; five were not carried over, and one new rule was written in
  their place.** The five bind to surfaces this repository does not have: two halves of a
  concept→class map over PHP and JavaScript, a rule against dead code paths in cross-references,
  an epistemic-substrate registry, and design-system projections. R14 here is the new one — a
  language-agnostic mirror that keeps the spirit of the first two without their coupling to one
  stack. Eighteen minus five plus one is the fourteen above. The numbering is contiguous rather
  than matching upstream, and the omission is named rather than hidden, because a reader who
  finds a gap in a numbering goes looking for the missing rule.
- **The lexical scorer is lexical.** Selection is deterministic and explainable, not clever: it
  matches task tokens against declared triggers, identity and paths. Declaring good triggers is
  the work, and the compiler cannot do it for you.
- **French is the upstream working language.** This repository is English throughout; the
  compiler's stop-word list keeps both, since the corpus it was built against is French.
- It has **one user**. If you adopt it and something is wrong, an issue is welcome.

## Licence

MIT — see [`LICENSE`](LICENSE).
