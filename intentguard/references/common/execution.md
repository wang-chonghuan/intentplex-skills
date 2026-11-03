# Execution Contract

## Native Playwright

Inspect repository rules, locked Playwright version, fixtures, package manager, and
authorized test environment. Confirm library syntax with Context7/current official
docs. Reuse existing dependencies and helpers. Do not add Cucumber, a BDD compiler,
a custom runner, or a private-function coverage layer. Dependency additions follow the
project's authority, not this skill's assumptions.

Keep the managed config in `.intentgurad/`; adapt the
[config example](../../assets/playwright.config.ts) to the approved matrix and
existing infrastructure. It discovers `tests/<case-id>/case.spec.*`. Shared code
belongs in `support/`; immutable case inputs/reference assets may stay in their
case's folder. Expected behavior remains in `e2e.json`.

Verify the responding application is the intended candidate. Record revision/build
identity and relevant uncommitted changes; a stale server is not release evidence.
Do not guess credentials. Client-callable APIs, including the app's own backend,
can use Playwright's request client; MCP can use the existing supported client/SDK
inside a Playwright test. Send the real HTTP/protocol request with the declared
actor's credentials (or none), including approved inputs the UI never sends.
That **is** When for an API/MCP execution. For a web execution, When uses the UI;
an HTTP shortcut cannot stand in for the clicks. API/DB setup may establish Given,
but direct DB writes or private-handler calls never substitute for When.
Check business consequences through user/client-visible results; direct DB
inspection may supplement evidence, not replace promised observable behavior.

## Shared Test Account

Default to one approved fixed test user. Sharing its userId is normal. Use fresh
browser contexts and test-scoped fixtures; anonymous cases must explicitly have
no auth state even when other cases use saved login state. A login case must
actually log in, not use an already-authenticated fixture to bypass its When.

Run shared-account mutations serially by default (`workers: 1`, `fullyParallel:
false`, no serial-mode groups that skip later cases after failure). Coordinate
exclusive account use across other suite invocations and human sessions too;
one worker does not isolate a second process. Parallelize only where the chosen
resources demonstrably cannot collide, or with an approved isolation strategy.
Unique user/tenant/run/case IDs are options, not mandatory prerequisites.

Each case establishes its own needed state without relying on an earlier case.
For example, prepare the shared user's test item as unsaved, test saving it, then
remove that saved item. Do not clear the entire account if unrelated items can
remain. Read-only cases may reuse stable data with no record cleanup at all.

Protect allocations from the start of setup, not only around `await use(...)`.
Teardown handles success, failure, and partially finished setup; release only
resources owned by or explicitly reserved for this test. Shared accounts are not
disposable. Surface cleanup errors. After a hard kill, recover safe premises on
the next run or use a bounded lease; do not claim teardown survives a machine crash.
Harmless history may remain if it does not compromise reliable reruns.

If runs interfere, first investigate fixture, account coordination, and environment
causes. Do not mislabel interference as a product defect or excuse a reproducible
user-facing defect as "flaky." Email, billing, paid models, and third-party writes
need approved sandboxes/scope/budget; an unavailable dependency is not permission
to silently mock the journey.

## Specification To Result

Keep one spec file per case, with one `test(...)` per execution. Version 2 uses
three static annotations and an awaited step for every shared Then:

```typescript
test('A saved item survives a new session [ui]', {
  tag: ['@intentguard:chromium'],
  annotation: [
    { type: 'intentguard.case', description: 'E2E-001' },
    { type: 'intentguard.execution', description: 'ui' },
    { type: 'intentguard.digest', description: '<SHA-256 from catalog command>' },
  ],
}, async ({ page }) => {
  // Establish Given, then perform When through the user's surface.
  await test.step('Then A1', async () => {
    // Await the actual assertion for the catalog's A1.
  });
});
```

This is protocol guidance, not a runnable test. Never read the digest at test
runtime: that would certify stale code against a new definition. Update its
static value only after reconciling the translation with the catalog change.

Route each execution to exactly its catalog projects using reviewed static tags
and project-level `grep` (see the config example), or the repository's equivalent
native routing. These are routing details derived from the catalog, not another
editable scope list. Do not use runtime skips to route tests. The checker requires
exactly the approved `(case, execution, project)` set, so missing, duplicate and
unapproved combinations fail. Legacy v1 retains one test per case and its two
original annotations, with no selective project routing.

Each Then step contains the real nonvacuous assertion, preserving quantities,
negations, permissions, persistence, and ordering. No empty steps, optional checks,
caught assertion failures, early returns, step skips, or fabricated success.
Use resilient user-facing locators and awaited assertions, not fixed sleeps.
The report can prove a step ran, not that it meant the right thing; gate3 checks
semantic fidelity. Test assertions use catalog expectations, never actual values
read from the running product as their own oracle.
For refused actions, assert any promised unchanged resources or absence of side
effects as well as the error response; do not "repair" the resource before checking.
Each execution independently establishes Given and cleans up its own changes.

## Full-Run Evidence

Keep **all runtime output outside the Git repository**, including traces, reports,
auth state, screenshots, and private fixtures. Use fresh external temporary
directories with restrictive access. Do not write these into `.intentgurad/` and
then add ignore rules. Approved visual baselines are source assets, but a captured
current screenshot does not become an approved baseline automatically.

Before a release run, commit maintained harness changes through the authorized
project workflow and run `check.py sources`. Use the project's package-manager
equivalent of this command, with the config path from `e2e.json`:

```bash
umask 077
export INTENTGUARD_RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/intentguard.XXXXXX")"
started_after="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
runner_exit=0
PLAYWRIGHT_JSON_OUTPUT_FILE="$INTENTGUARD_RUN_DIR/results.json" \
  npx --no-install playwright test --config .intentgurad/playwright.config.ts \
  --reporter=line,json --retries=0 --forbid-only || runner_exit=$?
python3 <skill-root>/scripts/check.py report --root .intentgurad \
  --report "$INTENTGUARD_RUN_DIR/results.json" --started-after "$started_after" \
  --exit-code "$runner_exit"
python3 <skill-root>/scripts/check.py sources --root .intentgurad
```

Set `INTENTGUARD_BASE_URL` or the existing equivalent and protected credential
environment variables before running; never commit them. Ensure custom reporters,
auth fixtures, and config also route output to the external run directory. Resolve
the real temp path and verify it is outside the repository before execution.

No ad hoc CLI filters, shards, retries, focused tests, or repeat-each for release
runs. Approved static project routing is required where execution scopes differ;
it must not omit any catalog combination. Each active execution must run once
in every assigned project. Do not merge focused
reports into an artificial full run. Separate repeatability runs use separate
reports. Preserve failed reports; rerun only after repair or verified resolution.

`report` checks the approved execution/project set, per-case test paths, static digests,
Then steps, fresh native results, first-attempt success, and actual runner exit.
It rejects missing/skipped/flaky/expected-failing/cleanup-failing executions. A
passing report does not override a failing source check or a semantic gate.

Record candidate/build identity, catalog fingerprint, environment (no secrets),
exact command, exit, timing, source commit, and evidence paths. Any relevant code,
case, config, or environment change invalidates release evidence. Rebuild/restart
and run the entire suite again after repairs.

Report CUJ/case outcomes, failed Then IDs, and unassessed `limitations`, not fixture
internals or private logs. A smaller focused suite may help development but is
never the release gate. Retire truly obsolete/redundant cases only with the
approved behavior change, never merely because they are red or expensive.
