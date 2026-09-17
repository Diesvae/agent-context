#!/bin/bash
# Guard of the directing context — mechanically proves what 00_PROTOCOLE.md prescribes.
#
# A doc that describes code IS code: it expires in silence, and nothing turns red. This guard
# is the only way to notice. Run it at the end of a mission.
#
# Usage : bash scripts/doc-lint.sh [--verbose]
# Exit  : 0 if everything passes, 1 otherwise. Every violation is named with its file.
#
# Every rule here has been broken on purpose and seen red — see scripts/prove-guards.sh. A
# rule that has only ever been green proves that it does not false-positive, and nothing else.
set -uo pipefail

ROOT=${ROOT:-$(cd "$(dirname "$0")/.." && pwd)}
VERBOSE=${1:-}
FAILURES=0
RULES_OK=0
WAIVERS=0
EXEMPT="$(dirname "$0")/doc-lint.exemptions"

# A waiver is a NAMED debt: it does not fail the run, but it is counted and printed. A rule
# that can be silenced by editing a filter is a rule with an undocumented off switch.
exempt() {  # $1 = rule (R1…), $2 = relative path
  [ -f "$EXEMPT" ] || return 1
  grep -qE "^$1[[:space:]]+$(printf '%s' "$2" | sed 's/[.[\*^$]/\\&/g')([[:space:]]|#|$)" "$EXEMPT"
}

red()   { printf '  \033[31m✗\033[0m %s\n' "$1"; FAILURES=$((FAILURES+1)); }
green() { printf '\033[32m✓\033[0m R%s — %s\n' "$1" "$2"; RULES_OK=$((RULES_OK+1)); }
title() { printf '\n\033[1mR%s — %s\033[0m\n' "$1" "$2"; }
waive() { printf '  \033[33m~\033[0m %s\n' "$1"; WAIVERS=$((WAIVERS+1)); }
rel()   { realpath --relative-to="$ROOT" "$1"; }

# STATE fiches: every .md of the directing context, minus journals, archives and generated files.
state_fiches() {
  find "$ROOT/_direction" "$ROOT"/app_*/_technique -name '*.md' 2>/dev/null \
    | grep -v '/journal/' | grep -v '/journal\.md$' | grep -v '/archive/' | grep -v '/memoire/' \
    | grep -v '/open/' | grep -v '/_[a-z-]*\.md$' | sort
}

# OPEN fiches: what is not settled. They live OUTSIDE state_fiches() and that is an arbitration,
# not an oversight — the size ceiling targets a STATE resuming its growth, and the ban on dates
# targets a fiche that says only what is true. An open fiche MUST date its measurements: that is
# what makes it re-examinable, and its bound against accumulation is that it disappears at
# closure. STRUCTURAL guards (R3, R9) do apply here.
open_fiches() {
  find "$ROOT/_direction" -path '*/open/*.md' -not -path '*/open/archive/*' 2>/dev/null | sort
}

# ─────────────────────────────────────────────────────────────────────────────
# R1 — size ceiling of a state fiche (25 KB). Catches growth resuming.
title 1 "no state fiche exceeds 25 KB"
n=0
while read -r f; do
  [ -z "$f" ] && continue
  o=$(wc -c < "$f")
  if [ "$o" -gt 25600 ]; then
    r=$(rel "$f")
    if exempt R1 "$r"; then waive "$r — $((o/1024)) KB (waived)"
    else red "$r — $((o/1024)) KB"; n=$((n+1)); fi
  fi
done < <(state_fiches)
[ "$n" -eq 0 ] && green 1 "no state fiche exceeds 25 KB"

# ─────────────────────────────────────────────────────────────────────────────
# R2 — mandatory opening: canonical title at level 4, then **Invariant** (levels 0-3),
# **Purpose** (level 4) or **Status** (a skeleton). A fiche that does not carry its identity
# in its first lines is a fiche whose kind a reader must infer from its folder.
title 2 "canonical opening (title + **Invariant** / **Purpose** / **Status**)"
n=0
while read -r f; do
  [ -z "$f" ] && continue
  case "$f" in */README.md|*/00_*.md) continue ;; esac
  case "$f" in
    "$ROOT"/app_*/_technique/*)
      stem=$(basename "$f" .md)
      if ! head -1 "$f" | grep -qF "# $stem — "; then
        red "$(rel "$f") — expected title: # $stem — Readable title"; n=$((n+1))
      fi
      ;;
  esac
  if ! head -8 "$f" | grep -qE '^\*\*(Invariant|Purpose|Status)\*\*'; then
    red "$(rel "$f") — neither **Invariant**, nor **Purpose**, nor **Status**"; n=$((n+1))
  fi
done < <(state_fiches)
[ "$n" -eq 0 ] && green 2 "canonical opening respected"

# ─────────────────────────────────────────────────────────────────────────────
# R3 — no dead pointer: every markdown link AND every backtick mention of a .md resolves.
#
# A TEMPLATE is not a pointer: `journal/YYYY-MM.md`, `CONC_<name>.md`, `<slug>.md` are name
# patterns, declared here and nowhere else. A new template turns the run red, and it is added
# knowingly. Recognised by BOTH halves of the rule — teaching it to one half only gives a rule
# that protects on one side and lies on the other.
#
# A CATEGORY PREFIX is NOT a template. Upstream it was, for a day, and that disarmed the
# markdown-link half over 248 of 462 links — two of which were dead. A substitution token
# designates no file; `CONC_account-api.md` designates one, and is checkable.
is_template() {  # $1 = cited path
  printf '%s' "$(basename "$1")" | grep -qE 'YYYY|PREFIX|NAME|<'
}
title 3 "no dead fiche pointer"
n=0
while read -r f; do
  [ -z "$f" ] && continue
  d=$(dirname "$f")
  while read -r l; do
    [ -z "$l" ] && continue
    is_template "$l" && continue
    [ -e "$d/$l" ] || { red "$(rel "$f") -> $l"; n=$((n+1)); }
  done < <(grep -oP '\]\(\K[^)#]+\.md' "$f" 2>/dev/null)
  # The corpus points mostly in backticks — the historical blind spot of this rule.
  #
  # CAPTURE FIRST, SEARCH SECOND. `find … | grep -q` was the original pattern and it is wrong
  # under pipefail: find exits 1 as soon as it meets an UNREADABLE directory, so the pipe is
  # non-zero even when the fiche exists. Measured upstream when a mode-750 data directory
  # appeared: fourteen perfectly live pointers declared dead at once, in fiches nobody had
  # touched.
  while read -r m; do
    [ -z "$m" ] && continue
    b=$(basename "$m")
    is_template "$m" && continue
    found=$(find "$ROOT" \( -name '.git' -o -name 'node_modules' \) -prune \
              -o -name "$b" -print -quit 2>/dev/null)
    [ -n "$found" ] || {
      r=$(rel "$f")
      if exempt R3 "$r"; then waive "$r -> $m (waived)"
      else red "$r -> $m (dead backtick mention)"; n=$((n+1)); fi; }
  done < <(sed 's/\[[^]]*\]([^)]*)//g' "$f" | grep -oP '`\K[A-Za-z0-9_./-]+\.md(?=`)' | sort -u)
# The boot file enters here, and only here: it is a front door, not a state fiche bound by R2/R6.
done < <(state_fiches
         open_fiches
         [ -f "$ROOT/AGENTS.md" ] && printf '%s\n' "$ROOT/AGENTS.md")
[ "$n" -eq 0 ] && green 3 "no dead fiche pointer"

# ─────────────────────────────────────────────────────────────────────────────
# R4 — every archived fiche declares its status; no fiche IN FORCE loiters under archive/.
title 4 "status declared under archive/"
n=0
found_any=0
for f in "$ROOT"/app_*/_technique/archive/*.md; do
  [ -e "$f" ] || continue
  found_any=1
  if ! head -6 "$f" | grep -qE '^\*\*Status\*\* — (ARCHIVED|ABSORBED|REVERSED)'; then
    red "$(rel "$f") — status absent or IN FORCE under archive/"; n=$((n+1))
  fi
done
# A rule with nothing to check is green for the wrong reason. Say so rather than imply a pass.
[ "$found_any" -eq 0 ] && red "no archived fiche anywhere: R4 would pass vacuously, which is not a pass"
[ "$found_any" -eq 0 ] && n=$((n+1))
[ "$n" -eq 0 ] && green 4 "status declared on every archived fiche"

# ─────────────────────────────────────────────────────────────────────────────
# R5 — no orphan fiche: every fiche is reachable from an index.
title 5 "no fiche orphaned from its index"
n=0
for tech in "$ROOT"/app_*/_technique; do
  [ -d "$tech" ] || continue
  idx=$(find "$tech" -name README.md -exec cat {} + 2>/dev/null)
  while read -r f; do
    [ -z "$f" ] && continue
    b=$(basename "$f"); [ "$b" = "README.md" ] && continue
    case "$b" in _*) continue ;; esac
    grep -q "${b%.md}" <<< "$idx" || { red "$(rel "$f") — cited by no index"; n=$((n+1)); }
  done < <(find "$tech" -name '*.md' | grep -v '/journal/' | grep -v '/journal\.md$' \
           | grep -v '/archive/' | sort)
done
[ "$n" -eq 0 ] && green 5 "no orphan fiche"

# ─────────────────────────────────────────────────────────────────────────────
# R6 — no dated entry outside the journal, and nothing struck through.
#
# A dated entry is a bullet, heading or table row carrying an ISO date ANYWHERE in it, not just
# at its start: "~~x~~ — **DONE on 2026-08-19**" is one, and that is how it escaped this rule
# upstream for months. No tolerated zone remains: a "## Journal LOG" heading starts with
# "## Journal" and disarmed the rule over a whole section.
title 6 "no dated entry outside the journal"
n=0
while read -r f; do
  [ -z "$f" ] && continue
  out=$(awk '/^```/{k=!k; next} k{next}
             $0~/^(- |#+ |\| )/ && /20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]/{c++} END{print c+0}' "$f")
  # Struck-through text is a reversal left in a fiche: a state is rewritten, not crossed out.
  # Literals inside a code span stay legal: they sometimes describe Markdown syntax itself.
  struck=$(awk '/^```/{k=!k; next} k{next}
                {l=$0; gsub(/`[^`]*`/, "", l); if (l ~ /~~/) c++} END{print c+0}' "$f")
  r=$(rel "$f")
  if [ "$out" -gt 0 ] || [ "$struck" -gt 0 ]; then
    if exempt R6 "$r"; then waive "$r — $out dated, $struck struck through (waived)"
    else
      [ "$out" -gt 0 ]    && { red "$r — $out dated entry/entries in a fiche: a date lives in the journal"; n=$((n+1)); }
      [ "$struck" -gt 0 ] && { red "$r — $struck struck-through passage(s): a state is rewritten, not crossed out"; n=$((n+1)); }
    fi
  fi
done < <(state_fiches)
[ "$n" -eq 0 ] && green 6 "no dated entry outside the journal"

# ─────────────────────────────────────────────────────────────────────────────
# R7 — the journal pointer: unique, central, exact in BOTH directions.
title 7 "journal pointer — unique, central, exact both ways"
n=0
map="$ROOT/_direction/00_CARTE.md"

# sense 1 — no state fiche reopens a journal section or points at a branch journal.
# 00_CARTE.md is named here: it IS the declaration, the only legitimate ## Journal of the corpus.
while read -r f; do
  [ -z "$f" ] && continue
  [ "$f" = "$map" ] && continue
  r=$(rel "$f")
  section=0; pointer=0
  grep -qE '^## (Journal|Decisions|Changelog)[[:space:]]*$' "$f" && section=1
  grep -qE '\]\([^)]*journal/\)' "$f" && pointer=1
  [ "$section" -eq 0 ] && [ "$pointer" -eq 0 ] && continue
  detail=""
  [ "$section" -eq 1 ] && detail="a journal section"
  [ "$pointer" -eq 1 ] && { [ -n "$detail" ] && detail="$detail and "; detail="${detail}a branch-journal pointer"; }
  if exempt R7 "$r"; then waive "$r — $detail in a fiche (waived)"
  else red "$r — $detail in a fiche: the pointer is unique, in 00_CARTE.md"; n=$((n+1)); fi
done < <(state_fiches)

# sense 2 — the table declares EXACTLY the branch journals on disk. Bounded to TABLE ROWS and
# markdown links: neighbouring prose cites `journal.md` without declaring it, and a declaration
# is read where it is structured, not where it is mentioned.
decl=$(awk '/^## Journal/{k=1;next} k&&/^## /{k=0} k&&/^\|/' "$map" \
       | grep -oP '\]\(\K[^)]+(?=\))' | sed 's:/*$:/:' | sort -u)
if [ -z "$decl" ]; then
  red "00_CARTE.md — ## Journal declares no journal: the central pointer is gone"; n=$((n+1))
fi
while read -r d; do
  [ -z "$d" ] && continue
  [ -d "$ROOT/_direction/${d%/}" ] || { red "00_CARTE.md — declared journal does not exist: $d"; n=$((n+1)); }
done <<< "$decl"
while read -r j; do
  [ -z "$j" ] && continue
  r=$(realpath --relative-to="$ROOT/_direction" "$j")
  grep -qxF "$r/" <<< "$decl" \
    || { red "_direction/$r/ — absent from the ## Journal of 00_CARTE.md: unfindable cold"; n=$((n+1)); }
done < <(find "$ROOT/_direction" -type d -name journal | sort)
[ "$n" -eq 0 ] && green 7 "no journal section or branch pointer in a fiche; $(grep -c . <<< "$decl") journal(s) declared, all live"

# ─────────────────────────────────────────────────────────────────────────────
# R8 — a SELECTOR does not lie, in either direction. An unguarded index expires in silence,
#      and a fiche missing from it becomes a rule nobody loads any more.
title 8 "selectors — every fiche cited, every citation live, weights measured"
n=0
selectors=0
for level in "$ROOT"/_direction/1_infrastructure "$ROOT"/_direction/2_app-conventions; do
  [ -d "$level" ] || continue
  selectors=$((selectors+1))
  rl=$(rel "$level")
  readme="$level/README.md"
  if [ ! -f "$readme" ]; then
    red "$rl — no README.md: the level has no selector"; n=$((n+1)); continue
  fi
  idx=$(cat "$readme")
  # sense 1 — every fiche of the folder is cited by the selector
  for f in "$level"/*.md; do
    b=$(basename "$f"); [ "$b" = "README.md" ] && continue
    grep -qF "$b" <<< "$idx" || { red "$rl/$b — absent from the selector $rl/README.md"; n=$((n+1)); }
  done
  # sense 2 — every fiche cited by the selector exists
  for b in $(grep -oE '\(([a-z0-9-]+\.md)\)' <<< "$idx" | tr -d '()' | sort -u); do
    [ -f "$level/$b" ] || { red "$rl/README.md cites $b, which does not exist"; n=$((n+1)); }
  done
  # the selector carries the INVARIANT, not just the name: one line per fiche, bounded at both ends
  for f in "$level"/*.md; do
    b=$(basename "$f"); [ "$b" = "README.md" ] && continue
    line=$(grep -F "($b)" <<< "$idx" | head -1)
    # Floor AND ceiling: under 160 chars the line is a table of contents again, over 360 it is a
    # summary — and the selector starts costing what it was built to save.
    [ ${#line} -ge 160 ] || { red "$rl/README.md — the line for $b carries no readable invariant (${#line} chars)"; n=$((n+1)); }
    [ ${#line} -le 360 ] || { red "$rl/README.md — the line for $b is a summary, not a line (${#line} chars > 360)"; n=$((n+1)); }
    # An announced weight is MEASURED. Otherwise it drifts in silence, and a selector with wrong
    # numbers is worse than one with none: it is consulted to decide what to load.
    dec=$(grep -oE '\| [0-9]+\.[0-9] KB \|' <<< "$line" | grep -oE '[0-9]+\.[0-9]')
    if [ -n "$dec" ]; then
      real=$(awk -v o="$(stat -c%s "$f")" 'BEGIN{printf "%.1f", o/1000}')
      gap=$(awk -v d="$dec" -v r="$real" 'BEGIN{e=d-r; print (e<0?-e:e)}')
      awk -v e="$gap" 'BEGIN{exit !(e>0.15)}' \
        && { red "$rl/README.md — $b announced $dec KB, measured $real KB"; n=$((n+1)); }
    fi
  done
done
[ "$n" -eq 0 ] && green 8 "$selectors selector(s) exact in both directions, weights measured"

# ─────────────────────────────────────────────────────────────────────────────
# R9 — THE OPEN REGISTER: what is not settled has a home, and it does not keep its closed.
#
# Three halves, because none of them sees what the other two see.
#
# (1) THE REGISTER, through the gate that owns it — `open_register.py --verify`. It proves in THREE
#     senses: a declared address that resolves, a written fiche that is declared, and a level-3
#     branch with NO entry — the only silent defect, since a branch without an entry is
#     indistinguishable from a branch with nothing open.
# (2) NO CLOSED POINT. A finished object is MOVED under archive/ by `open_register.py --close`; left
#     among the open, it is re-read every time. The closure vocabulary is open-ended in
#     practice: a guard greping for DONE, CLOSED and FINISHED passes green over "shipped".
# (3) THE CANONICAL OPENING. An open fiche opens on `**Open**`, as a state fiche on
#     `**Invariant**`: without it nothing distinguishes an open fiche from a state fiche
#     mislaid in the folder, and R2 no longer looks here.
title 9 "the open register — exact, no closed point, canonical opening"
n=0
if ! out=$(python3 "$ROOT/scripts/open_register.py" --verify 2>&1); then
  while IFS= read -r l; do
    [ -z "$l" ] && continue
    red "$(sed -E 's/\x1b\[[0-9;]*m//g; s/^[[:space:]]*✗[[:space:]]*//' <<< "$l")"; n=$((n+1))
  done <<< "$out"
fi
while read -r f; do
  [ -z "$f" ] && continue
  r=$(rel "$f")
  closed=$(grep -cE '~~|\*\*DONE|DONE \(|\bCLOSED\b|\bFINISHED\b|\*\*done\*\*|\*\*shipped\*\*|\*\*delivered\*\*' "$f")
  if [ "$closed" -gt 0 ]; then
    if exempt R9 "$r"; then waive "$r — $closed closure mark(s) (waived)"
    else red "$r — $closed closure mark(s) in an open fiche: close it with « open_register.py --close »"; n=$((n+1)); fi
  fi
  head -5 "$f" | grep -q '^\*\*Open\*\* — ' \
    || { red "$r — canonical opening absent: an open fiche opens on « **Open** — \`<branch> #<n>\` · <species> »"; n=$((n+1)); }
done < <(open_fiches)
[ "$n" -eq 0 ] && green 9 "$(python3 "$ROOT/scripts/open_register.py" --verify | tail -1)"

# ─────────────────────────────────────────────────────────────────────────────
# R10 — the boot budget is DECLARED, summed and verified. The "Boot" table of 00_CARTE.md is
# the declaration: what is not in it is not meant to be read at startup, and what is in it is
# measured. Without this rule the figure lied twice upstream — 21.7 KB announced for 43.9 real
# (three sources omitted), then 33.3 for 33.8 the next day, half a day after the correction.
title 10 "boot budget — declared, summed, verified"
n=0
map="$ROOT/_direction/00_CARTE.md"
if [ ! -f "$map" ]; then
  red "_direction/00_CARTE.md missing: the budget is declared nowhere"; n=1
else
  # The declaration is the TABLE ROWS, not the section: prose below cites files precisely to say
  # they are NOT in the budget, and summing the whole section put them back in.
  block=$(awk '/^## Boot/{k=1;next} k&&/^## /{k=0} k&&/^\|/' "$map")
  sum=0
  for m in $(grep -oE '`[A-Za-z0-9_./-]+\.md`' <<< "$block" | tr -d '`' | sort -u); do
    if   [ -f "$ROOT/$m" ];            then sum=$((sum + $(stat -c%s "$ROOT/$m")))
    elif [ -f "$ROOT/_direction/$m" ]; then sum=$((sum + $(stat -c%s "$ROOT/_direction/$m")))
    else red "00_CARTE.md declares $m at boot, not found on disk"; n=$((n+1)); fi
  done
  # Tolerance identical to R8: 0.15 KB. It is not laxity — 00_CARTE.md is part of the budget it
  # declares, so republishing the figure can move it. A digit change is neutral in bytes, a
  # rewording is not.
  declared=$(grep -oP 'Boot budget: \K[0-9]+\.[0-9]' "$map")
  if [ -n "$declared" ]; then
    real=$(awk -v o="$sum" 'BEGIN{printf "%.1f", o/1000}')
    gap=$(awk -v d="$declared" -v r="$real" 'BEGIN{e=d-r; print (e<0?-e:e)}')
    awk -v e="$gap" 'BEGIN{exit !(e>0.15)}' \
      && { red "00_CARTE.md — boot budget announced $declared KB, measured $real KB"; n=$((n+1)); }
  else
    red "00_CARTE.md no longer publishes « Boot budget: N.N KB »: the budget stops being checkable"; n=$((n+1))
  fi

  # THE DECLARED BUDGET IS NOT THE ONLY CEILING. A memory index is loaded by a tool that
  # TRUNCATES it past about 24.4 KB — and it truncates from the END, where nobody looks. R10
  # summed the sources and found the total correct: that is a READER's ceiling, not a
  # declaration's. 24 000 bytes, with the margin under the real bound rather than against it.
  index="$ROOT/_direction/memoire/MEMORY.md"
  if [ -f "$index" ]; then
    size=$(stat -c%s "$index")
    if [ "$size" -gt 24000 ]; then
      if exempt R10 "_direction/memoire/MEMORY.md"; then waive "memoire/MEMORY.md — $size bytes, past 24 000 (waived)"
      else red "memoire/MEMORY.md — $size bytes: past 24 000, its loader cuts the end off"; n=$((n+1)); fi
    fi
  fi
fi
[ "$n" -eq 0 ] && green 10 "boot budget matches its declaration; memory index under its reading ceiling"

# ─────────────────────────────────────────────────────────────────────────────
# R11 — the memory index is exact IN BOTH DIRECTIONS. A memory absent from the index is never
# recalled — it was written for nothing. Dangling [[links]] between memories stay LEGAL: they
# mark a memory still to be written.
title 11 "memory index — every memory cited, every citation live"
n=0
mem="$ROOT/_direction/memoire"
idx="$mem/MEMORY.md"
if [ ! -f "$idx" ]; then
  red "_direction/memoire/MEMORY.md missing: memory has no index"; n=1
else
  content=$(cat "$idx")
  for f in "$mem"/*.md; do
    b=$(basename "$f"); [ "$b" = "MEMORY.md" ] && continue
    grep -qF "($b)" <<< "$content" || { red "_direction/memoire/$b — absent from MEMORY.md: never recalled"; n=$((n+1)); }
  done
  for b in $(grep -oE '\(([a-z0-9-]+\.md)\)' <<< "$content" | tr -d '()' | sort -u); do
    [ -f "$mem/$b" ] || { red "MEMORY.md cites $b, which does not exist"; n=$((n+1)); }
  done
fi
[ "$n" -eq 0 ] && green 11 "memory index exact in both directions"

# ─────────────────────────────────────────────────────────────────────────────
# R12 — the boot file has SEVERAL NAMES and ONE CONTENT. Each tool reads the name it expects
# (CLAUDE.md, AGENTS.md, GEMINI.md…); the canonical one is AGENTS.md and the others are links.
# The failure mode this creates is precise: an agent overwriting a link with a regular copy.
# Two boot files, two directions, and nothing would turn red.
title 12 "portable boot — one content, aliases that resolve to it"
n=0
canon="$ROOT/AGENTS.md"
map="$ROOT/_direction/00_CARTE.md"
if [ ! -f "$canon" ] || [ -L "$canon" ]; then
  red "AGENTS.md — the canonical boot file must be a regular file at the root"; n=$((n+1))
else
  # The alias list is DECLARED in 00_CARTE.md, never guessed from the root's contents: one more
  # file at the root must not be able to pass itself off as a served boot file.
  decl=$(grep -oP '^\*\*Declared aliases\*\* — \K[^:]*' "$map" 2>/dev/null | grep -oE '`[^`]+`' | tr -d '`')
  if [ -z "$decl" ]; then
    red "00_CARTE.md no longer declares the boot aliases: R12 has nothing left to check"; n=$((n+1))
  fi
  for a in $decl; do
    [ "$a" = "AGENTS.md" ] && continue   # the canonical file is not an alias of itself
    if [ ! -L "$ROOT/$a" ]; then
      red "$a — declared alias, but not a link to AGENTS.md (content duplicated)"; n=$((n+1))
    elif [ "$(readlink -f "$ROOT/$a")" != "$(readlink -f "$canon")" ]; then
      red "$a — link that does not resolve to AGENTS.md ($(readlink "$ROOT/$a"))"; n=$((n+1))
    fi
  done
fi
[ "$n" -eq 0 ] && green 12 "portable boot: aliases declared, links exact"

# ─────────────────────────────────────────────────────────────────────────────
# R13 — the YAML map is only useful if it is addressable and deterministic. The compiler
# validates the schema, the references, every path, the containment hierarchy and sentinel
# cases. A dead node or an invented relation must break here, before it compiles something false.
title 13 "context map — schema, paths, graph and deterministic selection"
n=0
compiler="$ROOT/scripts/context-compile.py"
result=""
if [ ! -x "$compiler" ]; then
  red "scripts/context-compile.py missing or not executable"; n=1
else
  result=$(python3 "$compiler" --check 2>&1) || { red "context-compile.py --check: $result"; n=1; }
fi
[ "$n" -eq 0 ] && green 13 "$result"

# ─────────────────────────────────────────────────────────────────────────────
# R14 — THE MIRROR PAIR. Doc that talks about vanished code, and code no doc talks about.
#
# The first half is found by walking the docs, the second ONLY by walking the code. They look
# nothing alike and no folder-name derivation could see either: a name that encodes a
# correspondence does not guarantee it.
#
# A SKELETON module is exempt from declaring code — and says so in its opening **Status**.
# That is the honest form of the exemption: readable in the fiche, not buried in this filter.
title 14 "code and doc mirror each other — declared paths live, defined symbols cited"
n=0
modules=0
for readme in "$ROOT"/app_*/_technique/*/README.md; do
  [ -e "$readme" ] || continue
  case "$readme" in */archive/*) continue ;; esac
  r=$(rel "$readme")
  paths=$(grep -oP '^\*\*Code\*\* : \K.*' "$readme" | grep -oE '`[^`]+`' | tr -d '`')
  if [ -z "$paths" ]; then
    if head -6 "$readme" | grep -qE '^\*\*Status\*\* — SKELETON'; then
      [ -n "$VERBOSE" ] && waive "$r — skeleton module, no code declared (stated in the fiche)"
      continue
    fi
    red "$r — no « **Code** : » line: the module's code is derived from its folder name, not declared"
    n=$((n+1)); continue
  fi
  modules=$((modules+1))
  fiches=$(find "$(dirname "$readme")" -name '*.md' -not -path '*/archive/*' -exec cat {} + 2>/dev/null)
  for p in $paths; do
    # half 1 — doc about vanished code
    if [ ! -e "$ROOT/$p" ]; then
      red "$r declares $p, absent from disk: documentation about vanished code"; n=$((n+1)); continue
    fi
    # half 2 — code no doc mentions. Top-level definitions only: a private helper is an
    # implementation detail, and requiring every one of them documented makes the rule a
    # nuisance that gets switched off.
    while read -r symbol; do
      [ -z "$symbol" ] && continue
      grep -qF "$symbol" <<< "$fiches" \
        || { red "$r — $p defines $symbol, mentioned by no fiche of the module"; n=$((n+1)); }
    done < <(grep -hoP '^(?:export\s+)?(?:async\s+)?(?:def|class|function)\s+\K[A-Za-z_][A-Za-z0-9_]*' \
               "$ROOT/$p" 2>/dev/null | grep -v '^_' | sort -u)
  done
done
[ "$modules" -eq 0 ] && { red "no module declares code: R14 would pass vacuously, which is not a pass"; n=$((n+1)); }
[ "$n" -eq 0 ] && green 14 "$modules module(s) with code declared, mirrored in both directions"

# ─────────────────────────────────────────────────────────────────────────────
printf '\n'
if [ "$WAIVERS" -gt 0 ]; then
  printf '\033[33m%s named waiver(s)\033[0m — see %s\n' "$WAIVERS" "$(rel "$EXEMPT")"
fi
if [ "$FAILURES" -eq 0 ]; then
  printf '\033[32m%s rules green, 0 violation.\033[0m\n' "$RULES_OK"
  exit 0
fi
printf '\033[31m%s violation(s) over %s green rule(s).\033[0m\n' "$FAILURES" "$RULES_OK"
exit 1
