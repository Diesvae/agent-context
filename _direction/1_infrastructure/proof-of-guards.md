# Proof of guards

**Invariant** — a static guard is worth exactly its **proof**. Writing a rule, seeing the
suite green, and committing proves that the rule does not *false-positive*. It says nothing
about whether the rule can fire at all. Every rule in this repository has been **broken on
purpose**, seen red, and restored — and the script that does it is committed.

**Scope** — every guard in the repository, and every guard an adopter adds.

## State

The failure mode is specific and common: a guard that is green because it is **dead**. Three
ways it happens, all of them observed rather than imagined:

- **The pattern never matches anything.** A rule greps for a marker whose spelling changed, or
  anchors on a path literal that a rename moved. Nothing is found, so nothing is wrong.
- **The code never reaches the guard.** The rule is correct and sits behind a branch no
  execution takes. It would fire; it is never asked.
- **The scope excludes the target.** The rule walks a file list built by a filter that quietly
  drops the very files it was written for. The narrower the exclusion, the more plausible.

Each of the three shows the same symptom — green — and green is never investigated. The only
way to tell a live guard from a dead one is to make it fail.

## The procedure

[`scripts/prove-guards.sh`](../../scripts/prove-guards.sh) does it mechanically, one rule at a
time: it introduces a minimal violation, asserts the linter exits non-zero **and** names that
rule, restores the tree, and asserts the linter is green again. The restoration assertion is
not ceremony — a proof that leaves the repository dirty gets skipped after the second time
somebody has to clean up.

Two conditions make the result meaningful, and both are easy to lose:

- **The baseline must be green before the campaign starts.** A suite that is already red makes
  every mutation look killed, and the whole campaign reports success while proving nothing.
- **The mutation must target what the rule protects.** A rule proven only by a violation in a
  file it was never meant to cover is proven at a distance: the violation is caught by *some*
  rule, the report says the number, and the specific guard is still untested.

## Exemptions are named, never silent

A debt that is accepted is written in [`scripts/doc-lint.exemptions`](../../scripts/doc-lint.exemptions)
with its rule and its path. It does not fail the run; it is **counted and printed**. A rule
that can be silenced by editing a filter is a rule with an undocumented off switch, and the
next reader cannot tell a deliberate exception from an oversight.

## Links

- The linter: [`scripts/doc-lint.sh`](../../scripts/doc-lint.sh).
- The proof: [`scripts/prove-guards.sh`](../../scripts/prove-guards.sh).
- Above: [`addressable-context.md`](addressable-context.md) — the map's own check is a guard too.
