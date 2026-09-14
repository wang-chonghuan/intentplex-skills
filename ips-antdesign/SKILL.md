---
name: ips-antdesign
description: Load when the user wants to migrate a whole React app to Ant Design, enforce Ant-first components and design tokens, develop consistently with Ant Design X or Ant Design Charts, upgrade the Ant ecosystem, or explicitly invokes ips-antdesign. Use for full replacement and ongoing Ant UI engineering, not screenshot-faithful restyling, standalone chart images, deployment, or unrelated business logic.
---

# ips-antdesign

Make Ant Design the application's actual UI system, not a skin over a second component library. Preserve the user's information and capabilities while allowing presentation to follow documented Ant components.

## Route

| Capability | User intent | Read |
| --- | --- | --- |
| cap1: migrate | Replace an existing UI system across the app | [Migration](references/capability-1-migrate/workflow.md), then [gate 1](references/gate-1-migrate/gate.md) |
| cap2: develop | Build or fix Ant UI without drifting from the adopted system | [Development](references/capability-2-develop/workflow.md) |
| cap3: upgrade | Adopt a newer stable Ant ecosystem release | [Upgrade](references/capability-3-upgrade/workflow.md), then [gate 3](references/gate-3-upgrade/gate.md) |

If the user requests only research, a plan, or a review, provide that output without installing or migrating. If asked to implement, continue through verification; do not stop at a plan. Resolve an ambiguous capability from the current request before changing anything.

Always read [shared contract](references/common/contract.md). Before component code, read [sources and tools](references/common/sources.md). Before declaring implementation complete, read [verification](references/common/verification.md). These are conditional references, not a request to load every file every turn.

## Bootstrap

1. Resolve the target repo/workspace, frontend package, package manager, current branch, local instructions, and authorized ticket/workflow. Preserve unrelated work.
2. Read the actual routes, UI imports, build setup and relevant tests. Do not infer the framework from a vendor example.
3. Establish what may change: UI dependencies, styling and build configuration versus protected framework, routing, auth, transport, server functions and data semantics.
4. Respect the repo's charter-edit authority. Report conflicting old UI rules; do not silently rewrite them. This skill neither creates a ticket automatically nor bypasses an existing ticket requirement.
5. Use the repo's existing ticket/artifact location for evidence. Without one, use a single repo-local `artifacts/antdesign/` directory. Keep baselines, manifests and reports there, not inside this global skill.

`SKILL_ROOT` in commands means the directory containing this loaded `SKILL.md`; resolve it from the skill's actual location. Run project commands from the frontend package directory. Never bake one user's home path into project artifacts.

## Non-Negotiables

- Preserve information, actions, states and data meaning, not the old pixel layout. Never delete a field or interaction to fit a component.
- Prefer official components, then documented composition. Do not recreate Button, Input, Modal, Table or chat primitives behind local wrappers.
- Consume Ant tokens; maintain only approved overrides and necessary application extensions. Do not rename and transplant the old design system.
- Keep the user's requested framework and rendering contract. For TanStack Start, preserve Router, server functions and existing SSR/hydration guarantees; adapt frontend setup, not the application backend.
- Treat core Ant, X and Charts as separate APIs. A CLI miss is not proof that X lacks a component.
- Lock a compatible stable stack at adoption/upgrade; do not auto-upgrade during normal development.
- Do not send app data to chart-rendering services, buy data, run paid model calls, deploy, or write production state merely to validate UI.
- A clean Ant lint result, a rendered screenshot, or a completed goal is not proof of full migration.

## Completion and Review

The host agent owns semantic mapping, presentation decisions and user-task assessment. Deterministic tools own version/schema checks, route/import coverage, design-value checks and repeatable assertions.

Cap1 and cap3 must pass their matching gate before final handoff, merge or publication. Gates do not forbid reversible edits and tests needed to create evidence. Fix substantive findings, rerun affected checks and gate once; if a real blocker remains, report incomplete instead of weakening requirements. Do not polish already passing work.

For cap2, perform the scoped inline review and checks in its workflow. Any request expands neither merge nor deployment authority.

## Supplied Helper

[scripts/antd.mjs](scripts/antd.mjs) runs only local, explicitly pinned Ant CLI knowledge/analysis commands. It sets the target from installed `antd`, disables update notices, emits a versioned JSON envelope and fails on lint findings, skipped scans or malformed results. It does **not** certify route coverage, component compliance, token compliance, peer compatibility or business parity.

```bash
node "$SKILL_ROOT/scripts/antd.mjs" info Table
node "$SKILL_ROOT/scripts/antd.mjs" lint ./src
```

Maintainers: run `node --test "$SKILL_ROOT/tests/antd.test.mjs"` and apply [routing and scenario evaluations](tests/evaluation.md) after changing this skill. Do not confuse those tests with testing the target application.
