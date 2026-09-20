# cap3: Implement Approved Cases

Input: approved cases and matrix, repository rules, and an authorized test target.
Output: a faithful executable implementation and repeatability evidence.

1. Read the [execution contract](../common/execution.md). Validate the catalog.
   Do not translate drafts as if approved. A request for selected approved cases
   may proceed even when other candidate cases are still drafts, but report the
   remaining coverage and make no full-suite claim.
2. Inspect the actual application and existing test infrastructure. Confirm
   Playwright APIs against the locked version's current official documentation.
   Reuse the project's fixtures/configuration; obtain required approval before
   new dependencies or external operations.
3. Read each selected case's approved Then before exploring controls/actual values.
   Identify its user surface, repeatable Given setup, When, and every assertion.
   Default to the fixed test account, with explicit anonymous contexts for public
   features; public API/MCP service cases use their real consumer entry point.
   Missing access, unsafe setup, or unresolved expectations are blockers, not skips.
4. Write `.intentgurad/tests/<case-id>/case.spec.*` with the static annotation/
   digest/Then-step protocol. Keep needed fixtures/assets with that case and shared
   helpers in `support/`. Implement bounded setup/cleanup without deleting the
   shared account. Do not add subjective quality checks outside the catalog.
5. Run each new/changed case independently twice with freshly established premises;
   the account and stable seed data may stay the same. Then run it with affected
   peers, normally serially on the shared account. For a one-case suite, the two
   standalone runs suffice. Do not require fresh users, tenants, or namespaces.
   Prove cleanup/failure recovery with a safe controlled interruption/failure when
   a new fixture can leave resources behind; do not cause paid/destructive effects
   to test teardown. Explain any recovery path that cannot be safely exercised.
6. Classify failures as implementation defect, test-translation defect, data or
   environment blocker, or a requirement conflict. Fix test-translation defects
   within scope. Product fixes require the project's ticket/permission boundary.
   Requirement changes go through cap2; never update digests or assertions merely
   to conform to a failing product.
7. Apply [gate3](../gate-3-implement/gate.md). For a substantial new catalog or
   shared fixture design, use an independent reviewer when available and authorized.
   Supply the actual approved cases and sources, diff, test code, and raw results;
   do not substitute the producing agent's assurances for evidence.
8. Keep runtime artifacts outside the repo; review source files for secrets and
   commit `.intentgurad/` through the authorized repository workflow. Run
   `check.py sources`; unresolved commit authority/pending changes prevent release,
   not honest reporting of development evidence.
9. Report implemented/blocked IDs, repeatability/cleanup evidence, unassessed
   limitations, source status, and gate outcome. Full release verification remains
   cap4 and is not implied by focused tests passing.

Preserve failed-run evidence. Stop on missing authorization, unavailable premises,
or three attempts at the same unresolved failure. Do not repeatedly rerun unchanged
tests, rewrite expectations, or leave resources/services this run owns unattended.
