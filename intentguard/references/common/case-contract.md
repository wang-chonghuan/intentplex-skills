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
| `version` | `2` for new catalogs; see legacy compatibility below |
| `playwright_config` | Relative path inside `.intentgurad/`, normally `playwright.config.ts` |
| `projects` | Nonempty unique names of the approved Playwright execution matrix |
| `approval` | Actual confirmation of that scope, or `null` while proposed |
| `cases` | Nonempty array of atomic behavior definitions |

Each case:

| Field | Meaning |
|---|---|
| `id`, `cuj` | Stable uppercase/digit, hyphen-separated IDs, e.g. `E2E-001`, `CUJ-SAVED` |
| `title` | One independently decidable business behavior |
| `status` | `draft`, `active`, or `retired` |
| `source` | Product design, requirement, ticket, or conversation reference |
| `approval` | Actual human confirmation reference; `null` while unconfirmed |
| `given` | Nonempty list of actor, permissions, data, and conditions |
| `executions` | Nonempty list of approved ways to exercise this behavior |
| `then` | Nonempty list of `{"id": "A1", "expect": "Observable expectation"}` |
| `data` | `setup` and `cleanup` descriptions; read-only cases may say no mutable data |
| `limitations` | Optional list of explicitly unassessed qualities, not hidden Then assertions |

Active and retired cases require real approval. A written reference cannot create
authorization. Assertion IDs match `A1`, `A2`, etc., unique within each case.
Keep the designer's language. One behavior may require several actions/assertions;
split independent outcomes, not individual clicks.

Each execution has exactly four fields:

| Field | Meaning |
|---|---|
| `id` | Stable lowercase/hyphenated name, unique within this case, e.g. `ui`, `http` |
| `surface` | `web`, `api`, or `mcp` |
| `when` | Nonempty list of real user/client actions at this entry point |
| `projects` | Nonempty unique subset of the top-level approved project names |

Given, Then, data and approval belong to the case once. Every Then applies to
every execution; only actions and project routing vary. Prefer one execution
unless the rule genuinely needs another entry point. Do not force API-only inputs
through UI manipulation. If expectations are genuinely different (such as a
particular UI message versus an API error code), use distinct behaviors linked to
the same CUJ/source, not copies of a shared rule or per-execution overrides.

Given can name the same fixed test account in many cases. Include anonymous cases
where the product works without login. Add other actors only when a meaningful
permission/role behavior needs them; do not demand a user factory for every test.

Then contains the expected values, counts, relationships, visible states, errors,
or persistent effects. These come from the approved product definition, before
test generation. Inspecting DOM or responses can discover controls and actual
results, not justify "it currently says X, so X is correct." Do not put selectors,
private methods or database fields in Then. A client-visible status, error code,
resource representation or persistent effect is a legitimate API expectation.

## Harm And Generated Content

Include a boundary scenario when a client can submit the input and an approved
requirement/contract defines the outcome, or a concrete harm needs a product
decision. Undocumented, first-party and "internal"-named HTTP endpoints count if
users, anonymous callers, old apps or scripts can reach them. Frontend validation
is not a server trust boundary.

Consider relevant invalid values, unauthorized access, ownership of resource IDs,
money, inventory, deletion, expired credentials, duplicate/concurrent submission
and failed operations. Zero, null or a limit value is useful when it tests an
actual rule; do not enumerate every field combination or chase coverage numbers.
Unknown expected behavior goes to the designer, not an invented assertion.

For example, **if approved**: Given a signed-in buyer with a prepared cart, When
the buyer sends `POST /cart/items` with `quantity: 0`, Then the request receives
the contract's rejection **and the cart remains unchanged**. Checking 4xx alone
does not prove the promised lack of side effects. Do not add a UI version if its
controls cannot submit zero. When both entries matter, they must enforce the same
business constraint, not necessarily identical feedback.

A genuinely service-only boundary need not get a case for every private method.
Verify its relevant business consequences through the real outer entry point.
Network isolation is not permission to ignore money, ownership or authorization
rules; if isolation itself is promised, verify denial from the relevant caller
context. Do not invent product features or add a separate security-testing program.

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

Each active execution runs once in each of its approved projects. API/MCP cases
can use one request/client-only project without launching a browser; do not repeat
them across browsers without a reason. Web executions use the approved browser/
viewport matrix. A mixed project is allowed when appropriate. Review routing
changes like scope changes; never shrink the matrix to hide red tests.

## Legacy Compatibility

The checker also reads version 1 unchanged: case-level `surface` (`web`,
`public-api`, `public-mcp`) and `when`, with each active case in **all** top-level
projects. Its original case digest and two-annotation protocol remain valid;
the summary calls that execution `default`. Reading does not rewrite approval,
definitions or historical evidence. Do not mix version 1 and 2 case shapes.

Migrate only with the owner's agreement: preserve IDs, sources, approvals,
Given/Then/data and retired history; move each old When into one execution,
map `public-api` to `api` and `public-mcp` to `mcp`, and initially copy **all** old
projects into it. Reducing that matrix or adding entries requires approval.
Retranslate static digests/annotations and routing, then obtain fresh evidence.
Old reports do not certify the migrated catalog.

## Checks

From `<repo-root>`:

```bash
python3 <skill-root>/scripts/check.py catalog --root .intentgurad
python3 <skill-root>/scripts/check.py sources --root .intentgurad
```

`catalog` validates definitions and emits IDs, executions/projects, statuses,
assertion IDs, limitations, and SHA-256 digests of canonical JSON objects.
Key order/whitespace do not change a
digest; a field value does. `ready` means approved nonempty scope with no drafts,
not implemented tests, a committed harness, or product correctness.

`sources` checks the on-disk layout, rejects ignored files and symlinks, and requires
the entire harness to be tracked, committed, and unchanged relative to HEAD. It
does not stage or commit anything. During cap1-cap3, pending changes are expected;
commit them through the repository's normal authorized workflow before cap4 can
claim READY. Do not force-add ignored files or alter Git's global configuration.
The checker does not detect secrets or prove approval; review both before commit.
