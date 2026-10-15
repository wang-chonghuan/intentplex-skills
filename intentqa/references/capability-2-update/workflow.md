# cap2: Update The Behavioral Contract

Input: the current catalog and a concrete ticket/approved requirement.
Output: the smallest authorized catalog change and a behavior-level change summary.

1. Read the requirement from its authoritative source using the project's required
   backend tool if applicable. Separate explicit accepted requirements from AI
   suggestions or reported symptoms.
2. Read affected CUJs and search the rest of the catalog for shared behavior:
   permissions, navigation, persistence, roles, and dependent outcomes. A filename
   or changed component alone is not the impact boundary.
3. Classify the impact as added, changed, retired, or unaffected. Add CUJs/cases for
   new behavior. Preserve IDs when the same behavior changes. Retire obsolete
   behavior with its authorization rather than erasing its history or leaving
   contradictory active cases. Do not expand the requirement into unrelated cases.
4. Present any ambiguous conflict with both expectations and their sources. Ask
   which intent prevails when the approved requirement does not settle it.
   Do not weaken a previous case because the implementation is currently failing.
   "Make all tests green" alone never authorizes a behavior change.
5. Apply only confirmed changes, record their actual source/approval, and run
   `check.py catalog`. If the human already explicitly approved the concrete
   requirement and its implications, do not ask again merely to edit JSON.
   Otherwise keep existing active cases unchanged and present the proposed diff.
6. Report the affected CUJs and IDs, old versus new observable expectations,
   retirement/replacement relationships, and tests that now need reconciliation.

Do not change Playwright or product code unless that work was also requested.
Changes belong in `.intentgurad/e2e.json` and the normal source commit, never a
second case list. Do not convert failed Then assertions into limitations.
This capability's output is reviewed directly by the designer, not approved by
an AI semantic gate. A new case digest invalidates old executable evidence.
