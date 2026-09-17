#!/bin/bash
# Proof of the guard — breaks each rule on purpose, checks it turns red, restores, checks green.
#
# A rule that has only ever been green proves that it does not false-positive. It says nothing
# about whether it can fire at all. Three mechanisms produce a green DEAD rule: the pattern
# matches nothing, the guarded path is never executed, or the file list excludes the target.
# All three show the same symptom, and green is never investigated.
#
# Usage : bash scripts/prove-guards.sh [R7]     # one rule, or all of them
# Exit  : 0 if every rule proved itself, 1 otherwise.
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
ONLY=${1:-}
PRISTINE=$(mktemp -d)
WORK=$(mktemp -d)
PROVEN=0
UNPROVEN=0

cleanup() { rm -rf "$PRISTINE" "$WORK"; }
trap cleanup EXIT

# The campaign runs on a COPY. A proof that leaves the repository dirty gets skipped after the
# second time somebody has to clean up — and a skipped proof is the state we are trying to leave.
tar -c -C "$ROOT" --exclude=.git --exclude-vcs-ignores . 2>/dev/null | tar -x -C "$PRISTINE"

lint() { bash "$WORK/scripts/doc-lint.sh" 2>&1; }

reset_work() { rm -rf "$WORK"; mkdir -p "$WORK"; cp -a "$PRISTINE/." "$WORK/"; }

# THE BASELINE MUST BE GREEN BEFORE THE CAMPAIGN STARTS. A suite already red makes every
# mutation look killed, and the whole campaign reports success while proving nothing.
reset_work
if ! baseline=$(lint); then
  printf '\033[31mbaseline is not green — the campaign would prove nothing\033[0m\n'
  printf '%s\n' "$baseline" | grep -E '✗|violation' | head -20
  exit 1
fi
printf '\033[32mbaseline green\033[0m — %s\n\n' "$(printf '%s' "$baseline" | tail -1)"

# A rule is PROVEN when the run goes non-zero AND that rule's green line disappears. Asserting
# only the exit code proves the tree is broken, not that THIS rule saw it: a mutation caught by
# some other rule reports success and leaves the intended guard untested.
prove() {  # $1 = rule number · $2 = what the mutation does · $3 = shell mutating $WORK
  local rule=$1 what=$2 mutation=$3
  [ -n "$ONLY" ] && [ "$ONLY" != "R$rule" ] && return 0
  reset_work
  ( cd "$WORK" && eval "$mutation" ) || { printf '  \033[31m✗ R%s — mutation failed to apply\033[0m\n' "$rule"; UNPROVEN=$((UNPROVEN+1)); return 0; }
  local out status
  out=$(lint); status=$?
  if [ "$status" -eq 0 ]; then
    printf '  \033[31m✗ R%s — stayed GREEN under: %s\033[0m\n' "$rule" "$what"
    UNPROVEN=$((UNPROVEN+1)); return 0
  fi
  if grep -qE "✓ R$rule —" <<< "$out"; then
    printf '  \033[31m✗ R%s — run went red, but R%s itself stayed green under: %s\033[0m\n' "$rule" "$rule" "$what"
    printf '       caught by another rule instead — this guard is still untested\n'
    UNPROVEN=$((UNPROVEN+1)); return 0
  fi
  # Restoration is asserted, not assumed: a campaign that cannot return to green has changed
  # something it did not mean to, and every later case inherits that.
  reset_work
  if ! lint > /dev/null; then
    printf '  \033[31m✗ R%s — tree not green again after restore\033[0m\n' "$rule"
    UNPROVEN=$((UNPROVEN+1)); return 0
  fi
  printf '  \033[32m✓ R%s\033[0m — red under: %s\n' "$rule" "$what"
  PROVEN=$((PROVEN+1))
}

FICHE=_direction/app_notes/direction.md   # a state fiche in no selector folder, so mutations
                                          # here do not also trip R8 and muddy the attribution

# NOT `yes ... | head -n`: head closes the pipe, yes dies of SIGPIPE, and the mutation's exit
# status is non-zero even though the file was written. The harness then reports "mutation failed
# to apply" for a mutation that applied perfectly — a false negative in the proof itself.
prove 1  "a state fiche grown past 25 KB" \
  "for i in \$(seq 1 700); do echo 'filler line to push this fiche over its ceiling'; done >> $FICHE"

prove 2  "the **Invariant** opening line removed" \
  "grep -v '^\*\*Invariant\*\*' $FICHE > .tmp && mv .tmp $FICHE"

prove 3  "a markdown link to a fiche that does not exist" \
  "printf '\n- see [ghost](ghost-fiche.md)\n' >> $FICHE"

prove 4  "an archived fiche whose status says it is still in force" \
  "sed -i 's/^\*\*Status\*\* — ARCHIVED.*/**Status** — IN FORCE/' app_notes/_technique/archive/SYS_flat-index.md"

prove 5  "a level-4 fiche no index cites" \
  "printf '# CMP_ghost — uncited\n\n**Purpose** — exists, cited by nothing.\n' > app_notes/_technique/catalog/CMP_ghost.md"

prove 6  "a dated entry left in a state fiche" \
  "printf '\n- 2026-09-17 — fixed the thing\n' >> $FICHE"

prove 7  "a journal section reopened in a fiche" \
  "printf '\n## Journal\n\nsomething\n' >> $FICHE"

prove 8  "a selector weight that no longer matches the file" \
  "sed -i -E '0,/\\| [0-9]+\\.[0-9] KB \\|/s/\\| [0-9]+\\.[0-9] KB \\|/| 9.9 KB |/' _direction/1_infrastructure/README.md"

prove 9  "a closure mark left on an open fiche" \
  "printf '\n**shipped** last week\n' >> _direction/app_notes/open/001-search-index.md"

prove 10 "a boot budget figure that no longer matches its sources" \
  "sed -i -E 's/Boot budget: [0-9]+\\.[0-9] KB/Boot budget: 11.1 KB/' _direction/00_CARTE.md"

prove 11 "a memory absent from the index" \
  "printf -- '---\nname: ghost\ndescription: never recalled\nmetadata:\n  type: feedback\n---\n\nUnindexed.\n' > _direction/memoire/ghost.md"

prove 12 "an alias replaced by a regular copy of the boot file" \
  "rm CLAUDE.md && cp AGENTS.md CLAUDE.md"

prove 13 "a map node pointing at a document that does not exist" \
  "sed -i 's|- app_notes/_technique/catalog/README.md|- app_notes/_technique/catalog/GHOST.md|' _direction/cartes/system-map.yaml"

prove 14 "a public symbol defined in declared code and named by no fiche" \
  "printf '\n\ndef reindex_everything(store):\n    return store.refresh()\n' >> app_notes/src/catalog.py"

printf '\n'
if [ "$UNPROVEN" -eq 0 ]; then
  printf '\033[32m%s rule(s) proven: each one seen red on the violation it exists for.\033[0m\n' "$PROVEN"
  exit 0
fi
printf '\033[31m%s rule(s) proven, %s NOT proven.\033[0m\n' "$PROVEN" "$UNPROVEN"
exit 1
