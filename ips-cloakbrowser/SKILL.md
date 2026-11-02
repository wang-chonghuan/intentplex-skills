---
name: ips-cloakbrowser
description: Install, repair, update and use CloakBrowser — the stealth Chromium (github.com/CloakHQ/CloakBrowser) that Claude Code and Codex use as their web browser on this Mac, through the `cloakbrowser` MCP server and the `cloak-fetch` command. Load when the user says "ips-cloakbrowser", "安装 cloakbrowser", "用 cloakbrowser 访问网页", "cloakbrowser 坏了 / 更新 cloakbrowser", when a site blocks the agent's browser as a bot, or when the cloakbrowser MCP tools or `cloak-fetch` are missing or failing. Do not load for driving the user's own signed-in Chrome, previewing a local dev server, or Playwright test suites a project already owns.
---

# ips-cloakbrowser

CloakBrowser is a Chromium build with fingerprint patches compiled into the binary, wrapped as a drop-in Playwright launcher. On this machine it is the agents' browser for the public web: sites see a normal Chrome, not an automation tool. This skill sets it up once, keeps it current without anyone thinking about it, and says how to use it.

## What gets installed

`scripts/install.sh` (macOS; needs `uv`, `npm`, `python3`) is idempotent. Every piece it puts down:

| Piece | Where | Role |
|---|---|---|
| `cloakbrowser` wrapper | `uv tool` env, CLI in `~/.local/bin` | Python launcher plus `install / update / info / login` CLI |
| Stealth binary | `~/.cloakbrowser/chromium-<version>/` | The patched Chromium the wrapper downloads (signature-verified) |
| `@playwright/mcp` | global npm | The MCP server that gives agents browser tools |
| `cloak-mcp` | `~/.local/bin` | Starts Playwright MCP on the current CloakBrowser binary with its stealth args |
| `cloak-fetch` | `~/.local/bin` | One-shot rendered page read from a shell |
| `cloak-update` | `~/.local/bin` | The refresh job below |
| launchd job | `~/Library/LaunchAgents/com.intentplex.ips-cloakbrowser.update.plist` | Runs `cloak-update` daily at 09:30 and at login |
| MCP registration | `~/.claude.json` (user scope) and `~/.codex/config.toml` | Server name `cloakbrowser` in both agents |
| Agent rule | `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` | Block between `<!-- ips-cloakbrowser -->` markers, text from `references/agent-instructions.md` |

The script copies its Python and shell sources to `~/.local/share/ips-cloakbrowser/`, so the installed commands do not depend on this repo checkout staying where it is. After editing anything under `scripts/` or `references/`, rerun the installer to apply it.

Never store anything in `~/.cloakbrowser` besides what the wrapper writes: `cloakbrowser clear-cache` deletes that whole directory, license key included.

For a script-only repair on an already-installed machine, run
`bash <this skill>/scripts/install.sh --scripts-only`. It synchronizes the
authoritative scripts without upgrading dependencies, browser binaries or registrations.

## Install or repair

```bash
bash <this skill>/scripts/install.sh
```

It ends by fetching example.com through `cloak-fetch`; `Status: 200` there means the browser works. MCP tools appear only in agent sessions started after registration.

Repair is the same command. Diagnose first with `cloakbrowser info` (runs a launch test) and `tail -50 ~/Library/Logs/ips-cloakbrowser-update.log`.

## Use it

**Browser tools (interactive).** The `cloakbrowser` MCP server exposes Playwright MCP's tools: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_evaluate`, `browser_take_screenshot`, and the rest. Each agent session gets its own headless browser with a fresh in-memory profile and a fresh fingerprint; it closes after 3 idle minutes, losing its page state, and relaunches on the next call. Call `browser_close` when done (see the seat rules below). Auto-named snapshots go to `~/.local/share/ips-cloakbrowser/output/`, not into the repo.

**One-shot read (shell).** `cloak-fetch <url>` prints title, final URL, HTTP status and the visible text. `--html` prints rendered HTML, `--screenshot <file>` saves a full-page PNG, `--wait 8` gives a challenge page time to clear, `--headed` opens a real window, `--seat-wait <sec>` sets how long it queues for a license seat (default 90). Exit code 75 means no seat came free in time. Codex's sandbox blocks network and Chromium, so in Codex run `cloak-fetch` with escalation outside the sandbox; MCP servers are not sandboxed.

**Scripts.** For a crawl or a multi-step job, write Python against the wrapper rather than driving MCP step by step. Run it with the wrapper's interpreter, `"$(uv tool dir)/cloakbrowser/bin/python"`:

```python
from cloakbrowser import launch_context
ctx = launch_context(headless=True)          # Playwright BrowserContext
page = ctx.new_page(); page.goto("https://example.com"); print(page.title())
ctx.close()
```

`launch_persistent_context("<dir>")` keeps cookies and one fingerprint across runs; `humanize=True` adds human-like mouse and typing; `proxy=` and `geoip=True` route through a proxy with matching timezone and locale.

**Redirect experiments.** `cloak-fetch <url> --redirect-only --wait 8` uses a real
Chromium navigation and prints JSON with `url`, `status`, and only `location`,
`cf-mitigated`, and `retry-after` response headers. It stops an HTTP redirect
before the destination is requested, retaining the original status and raw
Location. Non-redirect pages can render during the bounded wait; this is not a
header-only HTTP client. It uses the browser's own user agent, not a bot UA.
`--headed` is optional. Cookies and license keys are never output. Do not use
`route.fetch()` for this experiment: it is an API request, not browser navigation.

For a batch, use `cloak-fetch --redirect-session --wait 8`. It launches one
browser and emits `{"event":"ready","protocol":1}`. Send one `{"url":"..."}` JSON
line on stdin, read its flushed response, then send the next after the desired
gap. Each request opens and closes one page in the same context. The caller owns
rate-limit backoff and handling blocks; the command never prefetches the next
URL. End stdin to close the browser; `{"event":"closed"}` confirms cleanup.
An `error` with `scope: item` reports a safe navigation error code and keeps the
context alive; the caller decides whether the link is invalid or retryable.
An error without item scope is a broken session. Close it before a paced recovery
with the same browser; never silently switch browsers. Recovery is the authorized
batch caller's responsibility, not a retry loop inside this command.

## Updates

`cloak-update` runs daily from launchd and at login. It upgrades the wrapper (`uv tool upgrade cloakbrowser`), fetches a newer binary if one exists (`cloakbrowser update`), updates `@playwright/mcp`, and deletes cached binaries that are no longer the active one and that no running browser uses. Results go to `~/Library/Logs/ips-cloakbrowser-update.log`; the job's exit code is non-zero if any step failed.

`cloak-mcp` and `cloak-fetch` set `CLOAKBROWSER_AUTO_UPDATE=false`, so a download never starts in the middle of an agent's request; updating is the job's alone. To update now, run `cloak-update` and read the log tail.

Check the job: `launchctl print gui/$(id -u)/com.intentplex.ips-cloakbrowser.update | grep -E "last exit|runs"`.

## Free binary, free key, Pro

Since wrapper 0.7.0 every launch on the host needs a key. `cloakbrowser login` gets a free key by email or saves one you already have. The key is stored in `~/.cloakbrowser/license.key`; run `cloak-update` afterwards to download the latest build, which the daily job then keeps current. Only the user runs `cloakbrowser login`, because it is their email. A paid key raises the concurrency limit. Never print or commit the key, and never request a second free key: the vendor revokes every linked one.

### The one-seat limit

The free key allows **one open browser across every agent, session and script on the machine**. Measured on Chromium 155:

| Situation | What happens |
|---|---|
| Second browser while one is open | Denied within a second. Wrapper code raises `CloakBrowserLicenseError` ("session limit reached") |
| Same denial in a browser tool | `Target page, context or browser has been closed`, with `exitCode=76` in the browser log. Retrying in the same session works once the seat is free |
| `browser_close`, idle timeout, MCP server exit, SIGTERM to `cloak-fetch` | Seat is free again within about 2 seconds |
| Browser hard-killed (SIGKILL, crash) | Seat stays taken until the server's lease expires, up to 4 minutes |

So: prefer `cloak-fetch` for reads, call `browser_close` when a browser-tool task ends, always close in a `finally` block in scripts, never `kill -9` a browser, and do not run `cloakbrowser info` (it launches a browser) while another agent may be browsing. If the seat stays busy for 5 minutes, tell the user instead of switching browsers silently.

## When the key is unavailable

`cloak-fetch` asks the license server at every start. If the key is not usable, it starts the keyless browser on Colima by itself and reads through that (`--headed` has no effect there), and it goes back once the key works. Browser tools use that browser from the next session whenever it is running. To start it for them:

```bash
colima start cloakbrowser
```

`colima stop cloakbrowser` frees it, and browser tools go back to the key.

First time on a machine:

```bash
colima start cloakbrowser --cpu 2 --memory 3 && docker run -d --init --name ips-cloakbrowser-local --restart unless-stopped -p 127.0.0.1:19222:9222 -e CLOAKBROWSER_AUTO_UPDATE=false cloakhq/cloakbrowser:0.6.5 cloakserve --idle-timeout=60
```

## When a site still blocks it

In this order, one change at a time:

1. `--wait 8` (or a longer MCP wait) so a Cloudflare-style challenge can finish.
2. Headed: `cloak-fetch --headed`, or temporarily register `cloak-mcp --headed`; some sites detect headless regardless of patches.
3. The latest binary through a key (section above).
4. A residential proxy with `geoip=True` in a script; a datacenter IP is flagged no matter how good the browser is.

CloakBrowser does not solve CAPTCHAs; it makes them less likely to appear. If a CAPTCHA or bot wall still shows, stop and tell the user rather than trying to get past it.

## Troubleshooting

| Symptom | Fix |
|---|---|
| No `cloakbrowser` tools in a session | Start a new session; if still absent, rerun the installer and check `~/.claude.json` → `mcpServers.cloakbrowser` or `codex mcp get cloakbrowser` |
| `cloak-mcp: playwright-mcp not found` | `npm install -g @playwright/mcp@latest`, then rerun the installer |
| macOS says the app is damaged | `xattr -cr ~/.cloakbrowser/chromium-*/Chromium.app` (the wrapper normally clears quarantine itself) |
| A new binary broke something | Wait for the next release; pinning an older version (`CLOAKBROWSER_VERSION`) needs a paid key |
| Update job failing | Read the log; run `cloak-update` by hand to see the failing step |
