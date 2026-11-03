---
name: intentguard
description: Load when the user wants a designer-owned Given/When/Then E2E case catalog, wants a ticket's Critical User Journeys reflected in that catalog, asks to implement approved cases in Playwright, or requests full-suite release verification with intentguard. Covers UI behavior and client-callable API/MCP boundaries, including inputs the frontend never sends; not internal-function coverage or generic Playwright API questions.
---

# intentguard

The product designer owns expected user-visible behavior. The case catalog is the
contract; Playwright is its executable implementation, not another specification.
Report results in the language of cases, not selectors or fixture internals.

The target project's source directory is **`.intentgurad/`**, with that exact
spelling. Keep the single catalog in `e2e.json` and each case's implementation in
`tests/<case-id>/`. Commit this directory with the product; never gitignore it.
Keep reports, traces, credentials, and auth state outside the repository.

## Choose The Capability

| Request | Read |
|---|---|
| Establish a catalog for an existing product or an approved new design | [cap1: Baseline](references/capability-1-baseline/workflow.md) |
| Add a ticket's CUJs or change existing expected behavior | [cap2: Update](references/capability-2-update/workflow.md) |
| Implement approved cases as repeatable Playwright tests | [cap3: Implement](references/capability-3-implement/workflow.md) |
| Run the entire approved suite and handle release-blocking failures | [cap4: Verify](references/capability-4-verify/workflow.md) |

Read the [case contract](references/common/case-contract.md) for every capability.
Read the [execution contract](references/common/execution.md) only for cap3/cap4.
Run only the requested capability; confirmation of case definitions is not an
instruction to implement, release, or deploy. A request spanning capabilities may
continue through them, subject to their approval boundaries.

## Authority And Scope

- Test user-triggerable paths and their observable consequences, through both
  the UI and client-callable API/MCP entry points. A first-party or undocumented
  endpoint is not exempt because the frontend never sends that input. Select
  scenarios by product rules and meaningful harm, not field permutations or
  coverage percentages. No private-function or separate internal API test layer.
  Existing unrelated checks remain outside this skill's release requirements.
- AI may discover behaviors, draft cases, and repair test code. It may change or
  retire expected behavior only on the basis of a human-approved requirement.
  A failure, the current implementation, or "make it green" is not that approval.
- Update the catalog before implementing a changed requirement. When intent is
  unclear, leave a draft or a proposed change and ask; never invent approval.
- Default to one approved fixed test account, plus anonymous cases for public
  functionality. Shared userIds are fine. Prepare each case's premises and
  coordinate shared mutations, normally serially; no dependency on test order
  and no requirement to restore the entire system.
- Write explicit Then expectations before inspecting pages/responses for
  implementation. Exploration may find controls and actual values, never invent
  expected values. Shared business constraints have one definition; execute only
  the relevant approved entry points, not every rule through both UI and API.
- For generated content, test useful observable behavior where practical. Record
  subjective quality as unassessed when no reliable check exists; do not demand
  exact prose, an LLM judge, or a quality rubric merely to adopt this skill.
- Missing, skipped, flaky, blocked, stale, or unimplemented cases are not passes.
  Repair causes, then verify; do not rerun unchanged failures until luck produces
  a green report.
- Follow the target repository's rules, ticket requirements, and operation
  permissions. This skill is independent of IntentFold and cannot override its
  boundaries. Do not create tickets, edit charters, add dependencies, write
  production data, incur paid usage, or deploy without the applicable authority.

## Agent And Code

The host agent discovers CUJs, resolves semantic conflicts, translates assertions,
and judges whether evidence proves them. Python's standard-library
[checker](scripts/check.py) parses the catalog and native Playwright JSON reports,
checks IDs, specification digests, committed source files, and complete execution.
It cannot prove that a selector or assertion means what a designer intended.

cap1/cap2 return behavior changes directly for human review. cap3 must pass
[gate3](references/gate-3-implement/gate.md) before handing tests downstream;
cap4 must pass [gate4](references/gate-4-verify/gate.md) before claiming release
readiness. A failed semantic gate permits one targeted repair, then a concrete
blocker report. Do not reopen passing work for polishing.

Use `<skill-root>` for this directory and run project commands from `<repo-root>`.
No project names, developer home directories, providers, ticket backends, or
deployment platforms are built into the skill.
