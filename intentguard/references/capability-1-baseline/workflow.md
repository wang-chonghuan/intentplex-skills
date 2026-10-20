# cap1: Establish The Baseline

Input: a target repository/product, accessible test environment when one exists,
and product intent or a designer available to settle ambiguous expectations.
Output: a designer-reviewable catalog, proposed execution matrix, and explicit gaps.

1. Read the repository's instructions and existing requirements/test inventory.
   Find whether a behavior catalog already exists. Reuse it or agree on migration;
   do not create a second authoritative list.
2. Derive the exploration scope from actual navigation, frontend/backend route
   manifests, access controls, roles, feature states, and documented journeys.
   Browse as the approved fixed test user and anonymously where available. Include
   meaningful empty, invalid-input, denied-access, success, and persistence states.
   Consider harmful user paths such as deletion, expired sessions, repeated or
   concurrent submission, and money only where the product offers them. Include
   client-callable API/MCP inputs even when undocumented or prevented by the UI;
   distinguish them from private calls behind the actual user entry point.
   Code helps locate surfaces and data setup; it does not define correct outcomes.
   Do not perform risky writes during discovery without authorization.
3. Group observations by CUJ and draft atomic cases using the
   [case contract](../common/case-contract.md). For a new product, draft from its
   approved design and explicitly mark that no runtime exploration occurred.
   Apply the shared boundary/harm criteria, not a per-field coverage matrix.
   Propose only the relevant executions/projects; share Then where applicable.
   If an expected result is unknown or observed behavior conflicts with design,
   state the discrepancy and ask the designer instead of copying the bug.
4. Create `.intentgurad/e2e.json` from
   [the JSON example](../../assets/e2e.json). Do not leave the example as an actual
   product case. Generated-content cases may have modest observable assertions and
   explicit unassessed limitations; do not invent a quality rubric as a prerequisite.
   Explain each proposed case/matrix in user language. Leave unconfirmed cases
   and scope unapproved; confirmation may already exist in an explicit design.
5. Run `check.py catalog` as documented in the shared contract. Present the CUJs,
   proposed behavior list, uncertain expectations, unassessed content qualities,
   and unexplored roles/surfaces. Keep limitations distinct from missing cases.
   The catalog is not complete while discovery gaps remain. Ask only the decisions
   needed to establish the baseline, then apply the user's actual confirmations.

Stop here unless implementation was also requested. A draft catalog is a valid
cap1 output, but neither a release gate nor a claim that the current product passes.
Keep the catalog as source to commit through the normal repository workflow; do
not add `.intentgurad/` to ignore rules or create a test runner during baseline-only work.
There is no separate semantic gate: the designer directly reviews this output.
