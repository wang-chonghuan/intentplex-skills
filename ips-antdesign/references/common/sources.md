# Sources and Tools

## Version Selection

At cap1 bootstrap and cap3, query registry `dist-tags.latest`, publication metadata and peer dependencies for the packages actually needed. Reject prerelease releases unless explicitly approved. Do not hard-code a research-date version into this skill.

Resolve a compatible stable set; "all newest" is not valid if peers conflict. Do not force peer resolution or add beta ProComponents merely to use advanced forms/tables. Use core Ant equivalents when practical; otherwise surface the compatibility decision.

Use the existing package manager, exact direct dependency versions and its committed lockfile. Verify installed versions and lock resolution agree, deduplicate shared style packages, and run the package manager's peer checks. Ordinary cap2 work uses these versions, not a new registry lookup followed by an unrequested upgrade.

Record package versions, selection date, relevant peer decisions and official skill/source refs in the existing evidence manifest. Save only decisions and sources actually used, not a second dependency lockfile.

## Official Entry Points

| Need | Primary source |
| --- | --- |
| Core components, props, demos, tokens, semantic slots, diffs | `@ant-design/cli`, https://github.com/ant-design/ant-design-cli |
| Core decisions and supplementary skill guidance | https://github.com/ant-design/antd-skill |
| Official agent entry | https://ant.design/docs/react/for-agents |
| Tokens and themes | https://ant.design/docs/react/customize-theme |
| SSR | https://ant.design/docs/react/server-side-rendering |
| X components / Markdown | https://github.com/ant-design/x/tree/main/packages/x-skill/skills and https://x.ant.design |
| Charts React APIs | https://ant-design-charts.antgroup.com and https://github.com/ant-design/ant-design-charts |
| Underlying G2 concepts, only when needed | https://github.com/antvis/chart-visualization-skills |
| Enterprise page patterns / Pro template | https://preview.pro.ant.design and https://github.com/ant-design/ant-design-pro |
| Optional higher-level ProComponents | https://github.com/ant-design/pro-components |

Treat links to moving branches as discovery, then resolve matching release/tag/commit or installed types for implementation. Record the ref consulted. CLI historical snapshots can fall back by minor; a version flag is not proof of patch-exact data.

When a Pro preview or ProComponents is in scope, read [Ant Design Pro usage](ant-design-pro.md).
Pro is a reference application built around Umi; it is not authority to replace the target
framework. A user-supplied local clone may be inspected read-only, but its machine-specific path
must not enter the skill or target repo.

Follow any repo-required documentation service, including Context7, first where mandated; then use CLI queries for concrete Ant APIs. If a service fails, report it and use a verified official alternative. Never silently fall back to remembered props.

## Read-Only CLI Workflow

Install `@ant-design/cli` as an exact local devDependency only within the authorized change. The helper also requires `antd` as an exact local direct dependency matching its installed release. Do not globally install or auto-upgrade. Before installation, use verified official docs rather than inventing local results.

From the frontend package directory:

```bash
node "$SKILL_ROOT/scripts/antd.mjs" info Table
node "$SKILL_ROOT/scripts/antd.mjs" demo Table
node "$SKILL_ROOT/scripts/antd.mjs" token Table
node "$SKILL_ROOT/scripts/antd.mjs" semantic Table
node "$SKILL_ROOT/scripts/antd.mjs" doc Table --lang zh
node "$SKILL_ROOT/scripts/antd.mjs" lint ./src
```

Use `demo <Component>` to discover demo names, then retrieve the selected demo. Query once per component/version need and reuse its verified result within the task. Do not flood context by dumping every component's docs.

The helper accepts `--project <frontend-dir>` before the command. It resolves packages locally, adds `--version <installed-antd>` and `--format json`, and forbids setup, upgrade, bug submission, arbitrary options and caller version overrides. Its output envelope contains package versions, command and official CLI data.

It assumes locally resolvable Node packages. If the package manager uses an unsupported resolution mode, use that manager's project Node runtime or a repo-local adapter with equivalent version/output validation. Do not globally install or fabricate successful helper output.

For CI, place the required guard/adapter in the repo under its normal tool ownership, with tests and attribution if copied. CI must not rely on a developer's global skill path. Keep one active implementation, not drifting global and project copies.

## Important Boundaries

- `antd migrate` is an Ant-to-Ant upgrade guide, not a converter from arbitrary UI libraries. Treat `--apply` as vendor-version-dependent; this helper does not expose it.
- Ant CLI lookup does not cover X or Charts APIs. Prefer X's `x-components` / `x-markdown` skills for UI; do not load request/provider SDK skills unless that layer is explicitly changing.
- `antd mcp` is an optional interface to the same knowledge. Do not install duplicate MCP servers or assume MCP exposes project lint/doctor. Choose one primary query path.
- Do not blindly install a whole vendor skill bundle. Its global install, auto-upgrade, SDK replacement and styling examples can conflict with the project contract.
- AntV `chart-visualization` and `mcp-server-chart` can send data to remote services and return chart images. They are not the development path for the app's React charts.
- Ant Design Pro examples can contain Umi runtime code, local components and demo services alongside official packages. Classify imports before reuse; never copy the whole page or scaffold into a non-Umi app.
- Library lint can report no issues in a project with no Ant imports. The helper validates the lint report, not adoption coverage.
- `doctor`, `usage` and `env` are diagnostic outputs. A zero process exit code is not a quality verdict; interpret their actual data separately.
