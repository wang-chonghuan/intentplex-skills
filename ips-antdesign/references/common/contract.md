# Shared Contract

## Product and Scope

The goal is a complete, maintainable Ant-first application. Default to preserving all existing user-visible information, controls, states, links, units and capabilities. Presentation may change; business meaning may not. Explicitly approved functional changes need their own traceable requirements.

Protect routes and query-string behavior, server functions, auth/access enforcement, billing boundaries, AI transport/tools, calculations and data acquisition. Replacing the UI does not authorize their replacement. Never turn null, unavailable, unknown or failed into zero/empty/success.

Enumerate all shipped UI, including authenticated/admin surfaces, mobile views, dialogs, empty/error/loading states, marketing/docs and demos. API-only routes need behavior preservation, not visual migration. Distinguish dead code from unvisited code with import/route evidence.

At baseline, resolve frozen presentations, hosted auth, embedded widgets and third-party UI. Do not silently exclude them. Report any approved exceptions by name; do not claim "100% Ant" with undisclosed exceptions. A frozen artifact must not require the active app to retain the entire retired UI system.

## Component Rules

Use official Ant primitives and documented composition. A business component may group data, controls and actions; it must not duplicate a supported primitive, create an alternate theme API, or hide internal DOM coupling.

Use documented semantic `styles` / `classNames` slots only when props and component tokens are insufficient. Do not target internal `.ant-*` / `.antdx-*` selectors or use broad `!important` overrides. Do not import internal library implementation modules.

Native semantic HTML and structural containers are allowed. They are not permission to implement custom buttons, select menus, dialogs or tables when an official equivalent exists. Keep real heading, landmark, label and link semantics.

When an old layout has no direct equivalent, first change presentation, then compose documented components. If neither preserves the task and information, record the exact gap and ask for a scoped decision. Do not silently add a second UI library or drop content.

## Tokens and Frontend Foundation

- Keep one application theme authority using Ant seed/alias/component tokens. Register only overrides and genuinely missing application values; do not copy all defaults.
- Prefer official layout and component options. Use minimal CSS Modules for unsupported structural layout; consume the same theme values.
- Classify literals: business values and structural `0`, `auto`, fluid sizing or grid tracks are not arbitrary design tokens. Colors, fonts, spacing, radii, shadows, borders, breakpoints and fixed visual dimensions require the approved source or an explicit narrow exception.
- Ban pages inventing themes, duplicating token aliases or hiding unregistered values in helpers, CSS variables, SVG attributes or inline styles.
- Prefer a small coherent brand/density adjustment over per-component restyling. Compact desktop tables do not justify tiny mobile touch targets.
- Remove the old UI's source, dependencies, CSS imports, build plugins and obsolete rules at migration completion. Temporary coexistence is allowed only in migration scope with tracked remaining work, never as the final design.

With X, use its documented provider integration with Ant and the App/hooks feedback context. Without X, do not add X merely to get a provider. Verify locale, direction, portals and theme propagation. Charts and Markdown need explicit, thin theme integration; their separate styling systems are not automatically covered by Ant UI tokens.

Preserve the existing rendering contract. Where SSR is present or explicitly required, use the framework's SSR lifecycle and check style extraction timing, request-local caches, deduplicated cssinjs, streaming and hydration before choosing runtime extraction or static/zero-runtime styles. Do not disable existing SSR or turn an SSR public page into a client-only workaround. An existing CSR-only app does not gain an unrequested SSR requirement.

## AI, Charts and Mobile

Use X UI without automatically adopting X SDK. Retain an existing transport/state layer unless its replacement is explicitly in scope. Preserve message identities/history, streaming, tool status, stop/retry, citations, partial failures and safe Markdown handling. Show only legitimately exposed activity; do not invent model reasoning.

Prefer the Ant Charts React wrapper that matches the needed chart types. Its underlying G2 APIs are not interchangeable with wrapper props. Preserve every series, unit, null gap, category order, domain, legend, tooltip value and meaningful interaction. Do not replace interactive charts with remotely generated images.

Where a public chart page has an SSR contract, retain meaningful server-rendered information, not only a canvas placeholder. Validate client import boundaries, lifecycle cleanup, resizing and hidden-to-visible tab transitions for charts that exist or are explicitly requested. Do not add charts or AI features just to satisfy a representative-page checklist.

Mobile presentation may use expandable rows, drawers or sections; information cannot simply disappear at a breakpoint. Verify keyboard and touch access, focus return, accessible names, contrast, reduced motion where applicable, and non-hover affordances.

## Authority

Repo/user requirements outrank vendor examples and skills. Installed release types/source determine available APIs; matching official release docs explain intended behavior. Third-party guidance is not authority.

Never weaken assertions, regenerate the old baseline from the new UI, widen exclusions, or rewrite a charter merely to make checks pass. Record unavailable evidence as unavailable, not success. Continue independent safe work when blocked; never substitute a reduced final scope without approval.
