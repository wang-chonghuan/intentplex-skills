# Cap2: Consistent Development

Read the hub bootstrap and shared contract. Use current installed/locked versions; this is not an upgrade request.

1. Read the requested flow, neighboring Ant compositions, token authority and repo guards. Verify the app's adopted contract exists. If adoption is incomplete, scope this task explicitly; do not quietly run a whole migration.
2. Select an official component before writing a local abstraction. Query matching API and demos through [sources](../common/sources.md); route X/Charts queries to their own docs. For an Ant Design Pro reference or ProComponent, read [the Pro boundary](../common/ant-design-pro.md), classify the example's imports and preserve the current framework.
3. Reuse business compositions when they fit. Keep data and transport unchanged. New behavior must derive from this task, not from a vendor demo.
4. Implement using documented props/tokens/semantic slots. Preserve all pre-existing information and states. A missing component triggers a presentation/composition decision, not silent data loss.
5. Run types, local Ant lint, repo component/token guards and affected behavior tests. Inspect changed UI at supported desktop/mobile sizes, including states and overlays. Changes to shared providers/tokens/layouts require broader regression.
6. Review against the actual user task: can users still understand the data and complete the action? Check the diff for hidden old-library imports, suppression casts, direct navigation reloads and missing states.

If the repo lacks adoption guards, do not claim enforcement. Add the narrowly necessary guard within authorized scope or state the missing prerequisite; a small unrelated fix does not authorize full migration.

When safe code can be completed but a required test cannot run, report the implementation and the exact unverified boundary. Never label verification passed. Follow the repo's handoff rules.

No separate gate document is needed for an ordinary reversible edit: this inline review and the repo checks are the completion mechanism. Escalate to the matching migration/upgrade workflow when that is the actual request. No automatic merge or deployment.
