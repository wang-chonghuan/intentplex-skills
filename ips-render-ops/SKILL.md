---
name: ips-render-ops
description: Load for day-to-day operation of a project already running on Render — "线上什么状态", "看一下日志", "手动跑一次那个 cron", "部署上去了吗", "回滚", "连一下生产库", "改个环境变量", or "ips-render-ops cap1..cap7". It sits on top of Render's own 21 official skills rather than replacing them: those explain how Render works, this one turns the recurring operations into one correct command each, with the non-interactive and credential-loading traps already solved. Do not load to design infrastructure (use render-blueprints), to deploy a project for the first time (render-deploy), or to debug a failed build in depth (render-debug).
---

# ips-render-ops

The operations you run on a Render project **after** it exists, and run often.

Render's official skills are the reference for what Render *is*. This skill is
the reference for what you *do* on a Tuesday: check the site is up, read what a
collector actually printed, trigger a job without waiting for its schedule, roll
back, look at the database.

```
render-blueprints / render-deploy   →   ips-render-ops   →   the product
design and first deploy                 running it
```

## This Skill Does Not Replace the Official Ones

**Always defer to the official skill for how something works.** They ship with
the CLI (`render skills install`) and they are versioned by Render:

| Question | Skill |
|---|---|
| What fields does `render.yaml` take? | `render-blueprints` |
| How does a first deploy work? | `render-deploy` |
| Why did my build fail? | `render-debug` |
| How do cron jobs behave? | `render-cron-jobs` |
| Postgres plans, limits, pooling | `render-postgres` |
| Env var strategy | `render-env-vars` |
| Domains and TLS | `render-domains` |

What this skill adds is the part those cannot know: **the shape of a running
agent session**. Every capability below is written to be run by an agent in a
non-interactive shell, which is where the official examples break.

## Three Traps, Solved Once

Everything here depends on these. They are the reason this skill exists.

**1. The API key is not in your shell.** It lives in `~/.zshrc`, and a
non-interactive zsh does not read `~/.zshrc`. Every command in this skill starts
with:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
```

Do not "fix" this by moving the key to `~/.zshenv` — that puts a secret into
every process on the machine.

**2. The CLI defaults to an interactive TUI.** Without flags it tries to open a
full-screen picker and produces nothing useful. Every invocation needs:

```bash
--output json --confirm     # or --output text --confirm
```

**3. Two subcommands crash on a non-TTY.** `render skills list` and
`render skills update` segfault before doing anything (a TUI bug — they panic
prior to any write, so nothing is damaged). `render skills install` is fine. Run
the other two from a real terminal.

## Preconditions

- `render` CLI installed and `render workspace set <id>` already done once.
- `RENDER_API_KEY` present in `~/.zshrc`.
- The project already exists on Render. Creating it is `render-deploy`'s job.

Verify all three in one line:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"; render whoami --output text --confirm
```

## Capabilities

| # | Name | Use it for |
|---|---|---|
| 1 | Status | `references/capability-1-status/status.md` — one picture of every service, its health, and its last deploy |
| 2 | Logs | `references/capability-2-logs/logs.md` — read what a service or a job actually printed |
| 3 | Deploy | `references/capability-3-deploy/deploy.md` — put one commit into production and prove it took. **Start here whenever you are about to deploy**: it decides auto vs manual by reading the platform, and a manual release is every service, not the one you had in mind |
| 4 | Run a job now | `references/capability-4-run-job/run-job.md` — fire a cron job off-schedule and watch it |
| 5 | Database | `references/capability-5-database/database.md` — connect, measure, and check without writing |
| 6 | Environment | `references/capability-6-environment/environment.md` — see and change configuration safely |
| 7 | Rollback | `references/capability-7-rollback/rollback.md` — go back to the last good deploy |
| 8 | Provision | `references/capability-8-provision/provision.md` — create a project's resources headlessly, and the three things the API will not let you do |
| 9 | Domains | `references/capability-9-domains/domains.md` — point a real domain at a service, and prove Render is the one answering |

Read the capability file at the moment you act. Do not run a command recalled
from earlier in a session; resource IDs change when a Blueprint is re-synced.

## The One Rule

**"The command exited 0" is not confirmation.** A deploy that succeeded and a
deploy that succeeded and serves a blank page look identical from the exit code.
Every capability here ends by observing the thing itself — the page's bytes, the
row count, the log line — and that observation is the result you report.

## Resource IDs

Almost every command takes a resource ID (`srv-…`, `dpg-…`), not a name. Get
them once at the start of a session:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
render services --output json --confirm \
  | python3 -c "import sys,json;[print(f\"{s['service']['id']}  {s['service']['type']:<8} {s['service']['name']}\") for s in json.load(sys.stdin)]"
```
