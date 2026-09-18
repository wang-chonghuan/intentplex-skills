# cap4: Verify The Release Candidate

Input: the approved current catalog, its implementation, and a specific candidate.
Output: READY or BLOCKED with complete case-level evidence. Never a deployment.

1. Read the [execution contract](../common/execution.md). Confirm authorization,
   actual application readiness/build identity, data target, catalog approval, and
   matrix. A missing/unapproved baseline is BLOCKED, not an empty passing suite.
   Check behavior/matrix changes against their approved requirement sources; a
   deleted file or changed status must not silently shrink the expected set.
   Run `check.py sources`: ignored, untracked, or uncommitted `.intentgurad/`
   material blocks READY. Coordinate shared-account use and verify anonymous
   cases have no inherited login state.
2. Confirm that tests were reconciled with current cases and passed gate3. This is
   not a demand to rereview unchanged tests on every release. Newly changed tests
   without reconciliation need cap3 before they can count as release evidence.
3. Start a fresh full run using the shared command pattern: no ad hoc CLI filters,
   shards, focused tests, retries, or synthetic success. Retain approved static
   project routing and run every active execution in its assigned projects.
   Record the actual process exit and native JSON report.
4. Run `check.py report` with the invocation's start cutoff and exit code.
   Inspect failures by case and Then ID, including fixture/cleanup/global errors.
   Report missing, skipped, flaky, and blocked separately from actual failures.
   A process exit of zero or HTML report's green headline is insufficient.
5. Repair only within the authority of this request and repository. A test fix
   must preserve approved meaning; a product fix needs the project's required
   ticket; an expected-behavior conflict goes through cap2. If authorized repairs
   were not requested, report failures instead of editing.
6. After a concrete repair or verified resolution of an environmental blocker,
   rebuild/restart if needed and rerun the full suite in a new evidence directory.
   Keep prior failures; never select only successful retries to assemble a pass.
   Stop if the same cause remains after three repair attempts, if intent is
   unresolved, or if access/safety/approval is missing. Report what must change.
7. Recheck `check.py sources` and apply [gate4](../gate-4-verify/gate.md) before READY.
   Record candidate identity and source commit,
   catalog fingerprint, execution/project matrix, total expected/executed/passed,
   all other outcomes,
   full-run command/timing, and evidence locations.

Present a concise CUJ/case result table, identifying failed executions/projects,
with failed expectations and next action
when blocked. Show unassessed generated-content qualities separately, without
treating them as skipped tests or pretending that they passed.
The user does not need to inspect generated Playwright code.
READY means this behavioral gate passed for this candidate/environment; it does
not certify undiscovered behaviors or supersede security, build, or other required
project checks. No merge, deployment, ticket closure, or production mutation is
authorized by a green suite.

Stop only services you started, unless explicitly left running for human review;
never stop an existing shared server or another task's connections.
