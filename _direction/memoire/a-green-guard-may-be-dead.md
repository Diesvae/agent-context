---
name: a-green-guard-may-be-dead
description: A rule that has never been seen red proves only that it does not false-positive.
metadata:
  type: feedback
---

Writing a guard, running the suite, and seeing green proves that the guard does not
false-positive. It says nothing about whether the guard can fire. Three mechanisms produce a
green dead guard: the pattern matches nothing (a marker was respelled, a path literal was
moved by a rename), the guarded path is never executed, or the file list is built by a filter
that drops the very files the rule was written for.

**Why:** all three present the identical symptom — green — and green is the one result nobody
investigates. The error is asymmetric: a false positive is noisy and gets fixed within the
hour, while a dead guard is silent and survives for as long as the repository does.

**How to apply:** before trusting a new rule, break it on purpose, confirm the run goes
non-zero *and names that rule*, then restore. Commit the script that does it. When a surviving
mutation appears, do not assume a missing test — check first whether the witness discriminates
at all, because a dead guard and a test that misses the path look the same and need opposite
remedies. See [[declared-beats-derived]] for the rename mechanism specifically.
