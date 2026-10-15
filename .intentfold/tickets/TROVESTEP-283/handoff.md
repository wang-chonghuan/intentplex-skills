# TROVESTEP-283 Handoff

Verified on 2026-09-18. Finish: review. No merge, installation, or deployment.

## What Changed

- The single IntentGuard catalog now covers UI and client-callable API/MCP
  boundaries, including first-party endpoints and inputs the frontend cannot send.
- Version 2 shares Given/Then per case and assigns actions/projects per execution.
  The checker reconciles exact case/execution/project combinations.
- Version 1 input, original case digests, two annotations and all-project scope
  remain supported without rewriting the catalog or historical evidence.
- All four caps, both gates, shared contracts, templates and agent metadata use
  the same scope and execution semantics. No new capability, runner, coverage
  threshold, rule registry or second case catalog.
- Added focused maintenance tests for the checker, not a target-product unit-test
  requirement.

The source checkout had an untracked 13-file intentguard skill. Commit `ad893ac`
preserves that exact baseline; implementation is `4de15dc`. Review the requested
update with `git diff ad893ac..4de15dc -- intentguard`. The PR against main also
contains the previously untracked baseline. Its original source directory and
unrelated changes were not overwritten.

## Acceptance Evidence

| AC | Result |
|---|---|
| 1. Client boundary, bounded scope | PASS. Contracts and draft API example cover quantity zero, rejection and unchanged cart; exclude field permutations/private-function coverage. Independent full-skill review exercised this scenario. |
| 2. Shared rule and exact execution set | PASS. Real local Playwright ran one case through UI/chromium and HTTP/api, plus one HTTP-only refusal case: expected 3, recorded 3, passed 3. Missing, duplicate, unknown, wrong-project, stale and failed evidence are rejected by checker tests. |
| 3. Compatibility and executable proof | PASS. 11 maintenance tests passed, including v1 digest/scope preservation and v2 schema/report checks. Native Playwright 1.62.1 run passed, with clean committed fixture source before and after. |
| 4. Global consistency and no production changes | PASS. Reviewed all skill resources and ran one independent global/behavioral review: no material defects. Skill validator and whitespace checks passed. Only skill/tracking files changed. |

Commands executed:

```bash
python3 -B -m unittest discover -s intentguard/scripts -p test_check.py -v
uv run --with pyyaml python <skill-creator>/scripts/quick_validate.py intentguard
python3 intentguard/scripts/check.py catalog --root intentguard/assets
git diff --check
```

The asset catalog is valid but deliberately NOT ready: its two illustrative cases
and matrix are unapproved drafts.

Local live fixture: `/tmp/intentguard-283-live/repo`, commit
`701b19dfdceea6f56a91f84bca7e0fead9fb245a`.
Native evidence: `/tmp/intentguard-283-live/run-2/results.json`.
Catalog fingerprint:
`c0a73bdc3cc43a6420b06592293e2ee1b2d3c1c8a03c857b47f671f8f958ecd4`.
The first local invocation ran 3/3 but omitted the JSON-output environment variable;
it was not accepted as report evidence. Correcting the invocation produced the
fresh native report, which passed `check.py report` with the actual zero exit.
No product/test expectation changed to obtain a pass.

## Environment And Residual

- Loopback-only disposable fixture; all its servers closed during teardown.
- No app code, database, cron, live API, paid provider or production operation.
- No persistent environment changes or new product dependencies.
- Worktree and branch retained for review. The installed/main skill is not updated.
- After approval, land the branch and reconcile the preserved untracked source
  with the committed skill; do not blindly overwrite any new source changes.
