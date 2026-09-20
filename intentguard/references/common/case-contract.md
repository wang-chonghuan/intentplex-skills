# Case Contract

## One Source Of Truth

Use `.intentgurad/e2e.json` in the target Git repository. The directory spelling is
intentional. JSON is the authoritative catalog, not CSV, Markdown case files, or
generated tests. Derive readable tables/exports on demand; never maintain two
editable specifications. Migrate an existing catalog with the owner's agreement,
preserving meaning, IDs, and approval history.

```text
.intentgurad/
  e2e.json
  playwright.config.ts
  support/                    # Optional shared fixtures and client helpers
  tests/
    E2E-001/
      case.spec.ts
      fixtures/               # Optional safe inputs needed by this case
      assets/                 # Optional approved reference assets
```

Commit all maintained source material here with the product. Never ignore this
directory or place runtime output, auth state, credentials, private records, or a
nested dependency installation inside it. Use the repository's package manager
and lockfile. Each implemented case has one `case.spec.*` in its own ID directory;
do not duplicate BDD definitions in a per-case README or manifest. Case folders
are code organization, not a demand for separate accounts or tenants.

## JSON Format

Start from [e2e.json](../../assets/e2e.json), replacing the example with real cases.
UTF-8 JSON is supported; duplicate keys and non-JSON constants are rejected.

Top-level fields:

| Field | Meaning |
|---|---|
| `version` | `1` |
| `playwright_config` | Relative path inside `.intentgurad/`, normally `playwright.config.ts` |
| `projects` | Nonempty unique names of the approved Playwright execution matrix |
| `approval` | Actual confirmation of that scope, or `null` while proposed |
| `cases` | Nonempty array of atomic behavior definitions |

Each case:

| Field | Meaning |
|---|---|
| `id`, `cuj` | Stable uppercase/digit, hyphen-separated IDs, e.g. `E2E-001`, `CUJ-SAVED` |
| `title` | One independently decidable business behavior |
| `surface` | `web`, `public-api`, or `public-mcp` |
| `status` | `draft`, `active`, or `retired` |
| `source` | Product design, requirement, ticket, or conversation reference |
| `approval` | Actual human confirmation reference; `null` while unconfirmed |
| `given` | Nonempty list of actor, permissions, data, and conditions |
| `when` | Nonempty list of actions through the declared user-facing surface |
| `then` | Nonempty list of `{"id": "A1", "expect": "Observable expectation"}` |
| `data` | `setup` and `cleanup` descriptions; read-only cases may say no mutable data |
| `limitations` | Optional list of explicitly unassessed qualities, not hidden Then assertions |

Active and retired cases require real approval. A written reference cannot create
authorization. Assertion IDs match `A1`, `A2`, etc., unique within each case.
Keep the designer's language. One behavior may require several actions/assertions;
split independent outcomes, not individual clicks.

Given can name the same fixed test account in many cases. Include anonymous cases
where the product works without login. Add other actors only when a meaningful
permission/role behavior needs them; do not demand a user factory for every test.

Then contains the expected values, counts, relationships, visible states, errors,
or persistent effects. These come from the approved product definition, before
test generation. Inspecting DOM or responses can discover controls and actual
results, not justify "it currently says X, so X is correct." Do not put selectors,
private methods, database fields, or internal API contracts in Then.

## Harm And Generated Content

Consider relevant user-triggerable harm: unauthorized access, money, deletion,
expired sessions, duplicate/concurrent submission, and failed operations. Do not
invent absent product features or turn this into private-code coverage. A public
API/MCP consumer is a user; an internal endpoint used by a web page is not a
separate E2E service just because it is reachable over HTTP.

For generated output, prefer modest checks the product really promises. A daily
insight case might say: Given today's insight exists for the test account, When
the user opens insights, Then a nonempty insight body and its date are visible.
Do not assert one exact generated sentence. Where the design promises references
or actions, test their observable behavior; do not impose those promises yourself.
An empty/error case needs its own Given, not "content OR error" to mask failures.

When quality, novelty, or correctness lacks a useful stable check, record e.g.
`"Insight usefulness and factual quality are not assessed by this case"` in
`limitations`. This is not an unimplemented assertion and does not block the
approved observable scope. Show it in the result summary. Do not demand a judge,
rubric, model-internal tool trace, or a separate evaluation project. Existing
explicit expectations cannot be moved into limitations just to hide a failure.

## Lifecycle And Matrix

cap1 drafts from product intent plus exploration; current behavior is evidence,
not an oracle. cap2 changes the catalog before implementing a new requirement.
Preserve IDs for the same behavior. Retire obsolete cases with authorization and
retain their definitions as tombstones; remove their executable test when the
retirement is applied. Never reuse their IDs for unrelated behavior.

Resolve conflicts instead of keeping contradictory active cases. A proposed change
does not demote an existing approved case to draft; retain the active definition
until approval and discuss the proposal in the ordinary ticket/conversation.

Drafts belong to the candidate and block release readiness. Unrelated future ideas
belong in the backlog, not this catalog. Known unassessed generated-content quality
is a limitation, not an invented draft case.

Each active case runs once in every approved project. For a service-only product,
use a request/client-only project; a browser is not required. A mixed product may
use the same project for web and service cases. Reuse the established browser/
viewport matrix when appropriate, and agree on changes. Do not filter some cases
out of a project or shrink the matrix to make red tests disappear.

## Checks

From `<repo-root>`:

```bash
python3 <skill-root>/scripts/check.py catalog --root .intentgurad
python3 <skill-root>/scripts/check.py sources --root .intentgurad
```

`catalog` validates definitions and emits IDs, statuses, assertion IDs, limitations,
and SHA-256 digests of canonical JSON objects. Key order/whitespace do not change a
digest; a field value does. `ready` means approved nonempty scope with no drafts,
not implemented tests, a committed harness, or product correctness.

`sources` checks the on-disk layout, rejects ignored files and symlinks, and requires
the entire harness to be tracked, committed, and unchanged relative to HEAD. It
does not stage or commit anything. During cap1-cap3, pending changes are expected;
commit them through the repository's normal authorized workflow before cap4 can
claim READY. Do not force-add ignored files or alter Git's global configuration.
The checker does not detect secrets or prove approval; review both before commit.
