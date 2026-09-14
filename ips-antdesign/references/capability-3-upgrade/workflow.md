# Cap3: Stable Ecosystem Upgrade

## Resolve the Upgrade

Apply the hub bootstrap. Preserve the adoption contract and protected architecture. Capture currently installed and locked versions and the working pre-upgrade UI/behavior baseline.

Resolve fresh stable tags, publication dates and peer ranges for the actual core/X/Markdown/Charts/icons/style-runtime packages in use. Use [sources](../common/sources.md). A stable version of one package does not make an incompatible set acceptable.

Read matching changelogs and API migrations. Use the CLI's Ant-to-Ant guide where relevant, but inspect X/Charts release changes separately. Identify SSR, tokens, semantic slots, chart behavior and AI lifecycle risks.

If newest releases conflict, use a compatible stable set that satisfies the request, recording any deferred optional package. If the user requires incompatible newest packages, surface the conflict; do not force peers or silently install beta.

## Implement and Verify

Update exact declarations and lockfile using the existing package manager. Update the CLI and official reference refs deliberately, not from an update notice. Check resolved versions and style-runtime deduplication.

Make the smallest necessary API/provider/theme changes. No opportunistic route, backend, layout or data-semantic redesign. Re-query changed APIs and retain documented component usage.

Test the helper/output schema against the selected CLI release. Schema drift is a tooling incompatibility to fix and test; never bypass a failed parser by accepting process exit 0.

Run the repo's complete component/token/version checks, relevant UI coverage, type/build and regression suites. Repeat cold rendering, overlays and mobile checks; repeat SSR/hydration, charts and AI streaming where present and affected. Use baseline-backed applicability, not invented features. Broaden tests for shared or major upgrades.

Prepare old/new versions, source refs, changes, retained/deferred dependencies and actual verification evidence. Run [gate 3](../gate-3-upgrade/gate.md) before final handoff.

## Goal / Resume

Goal mode uses this same workflow and acceptance bar. Resolve the repo, package, ticket, old/new version set, baseline and evidence location first.

Final state: compatible pinned stable dependencies, required API fixes, unchanged product meaning, current evidence and gate 3 pass. On resume, inspect lock/diff/evidence; do not reselect latest mid-run. Continue repairs, but stop for unresolved compatibility/authority or unavailable required verification. Do not declare completion because a dependency install succeeded.
