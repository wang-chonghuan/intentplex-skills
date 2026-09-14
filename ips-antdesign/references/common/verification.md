# Verification Contract

## Build the Checks in the Target Repo

No global skill can mechanically prove arbitrary application parity. Cap1 must implement/adapt repo-owned checks against actual routes, imports, theme sources and tests. Do this before broad migration. Cap2/3 reuse them; do not replace them with prose.

Use the existing AST/type/lint and CSS parsers. Do not substitute a broad regex or a hand-maintained second route list for structured analysis. Test intentional violations and legitimate uses before trusting a check.

Keep one evidence bundle in the repo's normal artifact location:

- Baseline identity: original commit plus relevant dirty-file snapshot identity, inventory extraction source/command, fixture identities and capture conditions.
- Derived inventory: UI routes, variants/states, displayed fields/units/sources, actions, charts and protected server behaviors. Each item links to old source/UI evidence.
- Mapping and progress: old item -> new component/presentation -> test/observation. Keep missing items visible; record approved scope changes separately.
- Current evidence: code revision, command, environment/viewport, actual result and output location. Stale or absent results cannot certify current code.

Derive coverage targets from router manifests, module graphs, existing schemas and observed behavior. Semantic observations supplement these sources; they must not pretend to be an automatically complete inventory. Empty targets fail. New routes must also be accounted for.

Derive applicability from the baseline and explicit requirements. SSR, charts, AI and hosted-auth checks may be `not applicable` only with evidence that the capability is absent and not requested. This is not a scope exclusion or permission to label an existing but untestable feature N/A. CSR-only apps keep CSR; apps without charts need no invented chart page.

Freeze the pre-migration baseline. Do not update it from the new interface. Compare important dirty-tree content too, not only HEAD. Use reproducible fixtures or authorized read-only captures so changing live data cannot masquerade as UI loss.

## Required Checks

| Check | What defeats a pass |
| --- | --- |
| Versions | Missing pins/lock evidence, peer conflicts, unexpected installed releases, duplicate incompatible style runtimes |
| Coverage | Empty discovery, missing routes/states/actions, baseline mutation, unreviewed exclusions, new untracked surfaces |
| Old UI | Residual runtime imports, aliases/re-exports, retired component implementations, CSS, assets needed only by them, build plugins or dependencies |
| Official components | Handwritten supported primitives, disguised local replacement frameworks, undocumented library internals |
| Tokens | Unregistered design values in CSS/JS/SVG/inline styles, invented variables hiding literals, broad internal selector overrides |
| API | Type errors, lint findings/skips/partial scans, suppression directives or casts masking incompatible props |
| Data parity | Lost fields/units/provenance, changed zero/null/error meaning, missing series or silently changed chart transforms |
| Behavior | Broken query URLs, pagination/filter/sort, navigation, access enforcement, forms, chat lifecycle, citations or actions |
| Rendering | Regressed existing SSR/public information, blank shells, hydration errors where applicable, FOUC, missing streaming styles or request cache leakage |
| Visual/access | Clipping, overlap, inaccessible hidden information, broken keyboard/focus/touch, unlabeled controls, chart/rendering failures |

Scope old-UI checks to the approved migration boundary; frozen independent artifacts and hosted UI require explicit treatment. Do not hide active app dependencies under blanket exclusions.

Component equivalence and meaningful information preservation need semantic review in addition to AST checks. Record and inspect dynamic renderers, computed styles, spread props and wrapper escape paths rather than claiming static analysis sees everything.

A narrow lint scan (`--diff`, `--staged`, `--only`) is development feedback, never a whole-app gate. Completion requires all production UI source roots, not an arbitrary hard-coded `src` when the app uses multiple packages.

## Browser and User-Task Evidence

Use the repo's browser tooling and viewport contract. If absent, cover desktop, 390px mobile and 320px narrow mobile. Assert content/controls and interactions, not just pixel differences. The new layout may legitimately differ.

Verify cold direct navigation and client transitions, slow-JS first paint, runtime console, real overlays/portals, delayed content, errors and retry. For SSR routes, also verify initial server HTML and hydration. Do not test only a component gallery.

For charts, inspect nonblank canvas/SVG output, series/tooltip values, container sizing, resize, tabs/drawers and touch alternatives. For X, replay deterministic stream/tool fixtures including cancellation, error and follow-up turns; do not spend model/API quota unless authorized.

Compare meaningful tasks with baseline: users must still find the same evidence, compare the same data, and perform the same actions. Do not substitute a successful tool response for a correct, useful answer.

Capture before/after representative screenshots and inspect them, then run route/state coverage assertions. One screenshot per route is not proof that all states work.

## Anti-Vacuity and Evidence Rules

Test each guard with a planted violation: forbidden import through an alias, raw design literal, skipped parser input, empty route discovery, missing mobile field, or removed chart series. Verify a documented component composition passes too.

Gate failures must exit nonzero in CI. Do not use advisory-only workflows, `continue-on-error`, empty snapshots or newly weakened expectations as the acceptance standard.

Missing credentials/fixtures or unsafe production access are blockers for the affected claim, not permission to fake evidence. Continue safe independent work and state exactly what remains unverified. Do not mark a full migration complete while a required check is unavailable.

Final output: scope completed, named approved exceptions, factual changes, tests actually run, evidence links and remaining blockers. Merge and deploy only through separately authorized project workflows.
