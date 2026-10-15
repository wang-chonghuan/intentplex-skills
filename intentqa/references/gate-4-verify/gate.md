# Gate 4: Complete Current Evidence

Purpose: could a release operator follow this report and release a candidate whose
approved user behavior was not actually proved by the complete current run?

Blocking invariants:

- The responding build/environment is the stated candidate, with no relevant
  edits or target changes after the evidence was collected.
- `.intentgurad/` is committed, clean, and unignored; `check.py sources` passed
  before and after the run. Runtime evidence and auth state are outside the repo.
- Catalog and matrix match approved intent; drafts, unexplored baseline gaps, or
  unjustified deletions/retirements were not used to exclude required behavior.
- `check.py report` passed on an unedited fresh native report with the actual
  runner exit, and gate3 covers the current translation. No missing, skipped,
  flaky, blocked, expected-failing, or cleanup-failing case is called a pass.
- The summary accurately limits its claim to this candidate, environment, and
  approved scope, including unassessed generated-content quality, and does not
  imply deployment authorization. Such declared limitations are not missing tests.

Run inline against raw evidence, not a second full suite. One targeted repair for
a reporting defect; missing/invalid execution evidence returns to cap4's full-run
step. If a real blocker remains, report BLOCKED rather than weakening the gate.
