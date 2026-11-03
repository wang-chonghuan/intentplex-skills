# Gate 3: Faithful Execution

Purpose: could another agent run these tests and get a pass while the approved
user behavior is still wrong because the translation changed or omitted meaning?

Review the approved cases, actual sources of authorization, changed tests/fixtures,
and repeatability evidence. Check only the changed semantic boundary.

Blocking invariants:

- Each When really uses its declared UI/client surface, including approved
  non-UI inputs; setup has not already performed the action or replaced the
  system with an unapproved fake. Routing matches the approved projects.
- Every Then has an awaited, nonvacuous assertion that preserves its quantities,
  negations, permissions, persistence, and visual/interaction meaning. A named
  empty step or digest match is not evidence. Expected values come from the catalog,
  not observations of the running product; limitations are not secretly counted as passes.
- Shared Then is enforced by every execution. Refusal checks include any promised
  lack of mutation or side effects, not just status codes. UI/API feedback may
  differ without weakening the underlying business rule.
- Cases may share the approved account, but establish their own premises and recover
  without deleting unrelated data or depending on order. Real reruns and account
  coordination support this; anonymous journeys do not inherit authentication.
- Cases and matrix remain approved; failures did not authorize changed expectations.

Run inline for narrow changes. For a substantial downstream test contract or risky
shared fixture, prefer an independent authorized reviewer with the raw context.
One targeted repair for a blocking defect, then stop if it remains. Formatting
and optional improvements do not block a faithful implementation.
