---
name: a-pipeline-status-can-lie
description: A pipe's exit status can report failure for work that succeeded, or hide work that did not.
metadata:
  type: feedback
---

`producer | head -n` exits non-zero: `head` closes the pipe, the producer dies of SIGPIPE, and
the pipeline's status reflects the death rather than the work. Under `set -o pipefail` a
successful write is then read as a failure. `find … | grep -q` fails the same way from the
other side: `find` exits non-zero as soon as it meets an unreadable directory, so a pointer
that resolves perfectly is reported dead.

**Why:** the status describes the plumbing, not the outcome. Which way the error falls decides
whether you ever find out: a spurious failure is loud and gets fixed, while a swallowed
producer status is silent and the check reports success forever.

**How to apply:** capture first, search second — assign the producer's output to a variable,
check the status, then match against the variable. When a pipeline must stay, decide
deliberately which side its status should describe, and say so in a comment. See
[[a-green-guard-may-be-dead]] for the failure this protects.
