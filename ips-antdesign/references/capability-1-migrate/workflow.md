# Cap1: Full Migration

## Bootstrap and Baseline

Apply the hub bootstrap and shared contract. Resolve the existing framework and frontend package rather than scaffolding a new app. A named ticket or checkout must resolve unambiguously before edits.

Read the old theme, component boundaries, routes, forms, charts, AI UI, auth, SSR/build configuration and checks. Identify protected business modules and frozen/hosted UI. Preserve existing user edits.

Capture the immutable baseline and derive the inventory described in [verification](../common/verification.md). Record all old libraries/plugins to retire. Map every user-visible item to an Ant component or documented composition; keep unresolved gaps explicit.

Record the approved scope and evidence in existing ticket artifacts. If old charter rules forbid the proposed UI system, obtain the required charter authorization before crossing that boundary. Do not silently treat a broad migration request as permission to edit human-owned governance.

## Establish the Foundation

1. Resolve and pin a compatible stable ecosystem using [sources](../common/sources.md). Retain the framework, routing and protected data/AI layers. If Ant Design Pro is a reference, apply [the Pro boundary](../common/ant-design-pro.md): reuse design patterns selectively, never its Umi scaffold.
2. Set one Ant token authority and the appropriate Ant/X provider and feedback context. Adapt build and styling setup; do not preserve the old styling framework merely by habit.
3. Implement/adapt the repo's official-component, token, coverage and old-system guards with failing fixtures. Put them in the ordinary check/CI command.
4. Select real representative pages from the inventory that exercise the shared foundation and riskiest existing interactions. Include data/chart and AI pages when present, and validate SSR/streaming only where present or required. Cover portals, direct navigation and mobile. Record evidence-backed N/A for absent capabilities; do not invent new ones. A button demo is insufficient.
5. Establish the coherent visual baseline from these pages: typography, density, surfaces, brand and touch behavior. Use explicit brand choices if supplied; otherwise choose restrained Ant defaults and document them.

These representatives establish the foundation, not a reduction of the full scope. Continue autonomously unless the user requested a review checkpoint or a substantive unresolved decision blocks progress.

## Migrate in User-Task Slices

Replace primitives and page compositions together where needed. Preserve data inputs, calculations, source/time/coverage labels, permissions and actions. Change layout to match Ant capabilities rather than reproducing unsupported old shapes.

For each slice: query APIs, implement, run targeted checks and user-task tests, inspect desktop/mobile views, update mapping with current evidence. Verify views, overlays and states before calling a route complete.

Temporary old/new coexistence is a work-in-progress state. Track outstanding imports/components and prevent new old-system uses. Never call a pilot or partially migrated shell a full migration.

## Finalize

After all items are mapped and validated, remove unreachable old UI, obsolete demo/prototype implementations, dependencies, CSS, plugins and superseded rules. Preserve functional routes or their approved replacements. Do not delete assets shared by frozen artifacts or unrelated features.

Run every required full-scope check against the final tree, inspect the final dependency/import graph and review baseline-to-new information parity. Prepare the scope/exception/evidence handoff.

Run [gate 1](../gate-1-migrate/gate.md). Fix identified substantive failures without changing the baseline or diluting assertions. A required failed/missing check means incomplete, not "done with caveats."

## Long-Running / Goal Execution

A goal is only a wrapper around cap1. Resolve repo, package, ticket, authorized paths, evidence location, scope and baseline before acting; no new goal is required for an ordinary request.

Final state: in-scope UI is Ant-first, protected behavior/info remains, old runtime UI is removed, required repo checks pass and gate 1 passes. Evidence is the current inventory mapping, version/lock decisions, test outputs and browser/task observations, not goal status.

Work slice by slice. On resume, read the persisted scope, original baseline, current git state and completed evidence before continuing; do not restart or regenerate a convenient baseline. Invalidate evidence affected by new code.

Continue repairable work. Stop the affected action for unresolved authority, incompatible required dependencies, an unrepresentable information requirement or unavailable safe verification. Report the precise missing decision/evidence while keeping the run incomplete. Time/budget exhaustion never changes the acceptance bar.
