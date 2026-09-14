# Ant Design Pro and ProComponents

Read this reference only when the user names Ant Design Pro, a `preview.pro.ant.design` page,
ProComponents, or asks to use an official Pro dashboard/application example.

## What Pro Is

Ant Design Pro is an official enterprise application template and reference implementation. Its
pages are useful evidence for information hierarchy, density, responsive composition, dashboard
patterns and component choices. It is not an extension that must be installed to make Ant Design
complete.

The current Pro application uses Umi Max for routing, runtime configuration, access, requests,
generated services, build and development commands. A preview page can also combine:

- core `antd` components;
- `@ant-design/pro-components`;
- Ant charts/plots;
- project-local business or presentation components;
- Umi-specific data, routing and service code.

Therefore, an official-looking Pro page is not evidence that every visible element is a reusable
Ant primitive or ProComponent.

## Use In A Non-Umi Application

When the target app uses TanStack Start, Next.js, Remix, React Router or another chosen framework:

1. Preserve that framework's router, loaders/server functions, SSR lifecycle, auth, query/cache and
   error handling.
2. Use the Pro page as a composition reference. Rebuild the needed result from documented Ant,
   Charts/X and, when justified, compatible ProComponents.
3. Do not copy `@umijs/max` imports, `config/routes.ts`, `src/app.tsx` runtime hooks, generated
   services, access models, mock servers, request wrappers, layout configuration or build commands.
4. Translate links, navigation, data loading and permissions into the target application's existing
   APIs. Vendor demo data and behavior never replace product requirements.
5. Verify the resulting page under the target framework's SSR/hydration and mobile contracts.

Never migrate the app to Umi merely to reproduce a Pro example unless the user separately and
explicitly changes the framework requirement.

## ProComponents Decision

`@ant-design/pro-components` can be used independently of the Ant Design Pro scaffold, but adding it
is a dependency and compatibility decision, not an automatic consequence of referencing a Pro
page.

For each proposed component:

- confirm a stable release supports the installed React and Ant versions without forced peers;
- read its current documented API and installed types;
- verify SSR, portals, token propagation and bundle impact in the target app;
- confirm it removes meaningful complexity compared with core Ant composition;
- keep the target app's data and navigation state authoritative.

Typical candidates include `ProCard`, `StatisticCard`, `ProTable`, `ProDescriptions` and `ProForm`.
Use them only when their higher-level behavior fits the product. Prefer core Ant when the Pro
component would impose a second data/request model, duplicate routing state or obscure required
information.

Be especially cautious with:

- `ProLayout`, because it often assumes Pro/Umi-style menu, routing and access configuration;
- `ProTable` request/search/persistence conventions, which can conflict with existing URL state,
  server loaders or query caches;
- generated forms or schemas that change validation, submission or error semantics.

Do not add a beta/prerelease ProComponents build, force peer resolution or import internal modules
to imitate a preview. If no compatible stable release exists, use documented core Ant composition
or report the decision.

## Reference Inspection

Primary references:

- preview pages under `https://preview.pro.ant.design/`;
- `https://github.com/ant-design/ant-design-pro`;
- `https://github.com/ant-design/pro-components`;
- matching release documentation and installed package types.

If the user supplies a local Ant Design Pro clone, inspect it read-only as a convenient source. Use
the user-provided location only for that session; never write its absolute path, username or machine
layout into this skill, project code, evidence or generated instructions.

For a specific page, classify each imported element before reusing it:

```text
core Ant | ProComponent | chart/X package | local Pro component | Umi/runtime code
```

Reuse the first three only after normal API and compatibility checks. Treat local Pro components as
examples to reinterpret, not as automatically approved primitives. Exclude Umi/runtime code unless
the target project itself is already an authorized Umi application.

## Analysis Dashboard Example

The official `/dashboard/analysis` page is a useful reference for KPI hierarchy, date controls,
responsive metric rows, chart-plus-table composition and dashboard density. It is not a drop-in
page:

- its route and request layer are Umi-specific;
- `GridContent` comes from ProComponents;
- its charts come from the Ant chart/plot package;
- cards such as `ChartCard`, plus `Trend` and `Field`, are project-local components;
- the sample values and interactions are demo behavior.

In another framework, reproduce only the approved product presentation. Use the target app's real
data contract and existing state, choose documented components, centralize tokens, and validate
desktop/mobile behavior rather than copying the page directory wholesale.
