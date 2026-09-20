# Gate 3: Faithful Execution

Purpose: could another agent run these tests and get a pass while the approved
user behavior is still wrong because the translation changed or omitted meaning?

Review the approved cases, actual sources of authorization, changed tests/fixtures,
and repeatability evidence. Check only the changed semantic boundary.

Blocking invariants:

- When really uses the user's surface; setup has not already performed the action
  or replaced the system with an unapproved fake.
- Every Then has an awaited, nonvacuous assertion that preserves its quantities,
  negations, permissions, persistence, and visual/interaction meaning. A named
  empty step or digest match is not evidence. Expected values come from the catalog,
  not observations of the running product; limitations are not secretly counted as passes.
- Cases may share the approved account, but establish their own premises and recover
  without deleting unrelated data or depending on order. Real reruns and account
  coordination support this; anonymous journeys do not inherit authentication.
- Cases and matrix remain approved; failures did not authorize changed expectations.

Run inline for narrow changes. For a substantial downstream test contract or risky
shared fixture, prefer an independent authorized reviewer with the raw context.
One targeted repair for a blocking defect, then stop if it remains. Formatting
and optional improvements do not block a faithful implementation.
