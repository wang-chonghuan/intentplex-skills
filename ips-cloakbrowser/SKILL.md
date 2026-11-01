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

## Install or repair

```bash
bash <this skill>/scripts/install.sh
```

It ends by fetching example.com through `cloak-fetch`; `Status: 200` there means the browser works. MCP tools appear only in agent sessions started after registration.

Repair is the same command. Diagnose first with `cloakbrowser info` (runs a launch test) and `tail -50 ~/Library/Logs/ips-cloakbrowser-update.log`.

## Use it

**Browser tools (interactive).** The `cloakbrowser` MCP server exposes Playwright MCP's tools: `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_evaluate`, `browser_take_screenshot`, and the rest. Each agent session gets its own headless browser with a fresh in-memory profile and a fresh fingerprint; it closes after 10 idle minutes and relaunches on the next call. Auto-named snapshots go to `~/.local/share/ips-cloakbrowser/output/`, not into the repo.

**One-shot read (shell).** `cloak-fetch <url>` prints title, final URL, HTTP status and the visible text. `--html` prints rendered HTML, `--screenshot <file>` saves a full-page PNG, `--wait 8` gives a challenge page time to clear, `--headed` opens a real window. Codex's sandbox blocks network and Chromium, so in Codex run `cloak-fetch` with escalation outside the sandbox; MCP servers are not sandboxed.

**Scripts.** For a crawl or a multi-step job, write Python against the wrapper rather than driving MCP step by step. Run it with the wrapper's interpreter, `"$(uv tool dir)/cloakbrowser/bin/python"`:

```python
from cloakbrowser import launch_context
ctx = launch_context(headless=True)          # Playwright BrowserContext
page = ctx.new_page(); page.goto("https://example.com"); print(page.title())
ctx.close()
```

`launch_persistent_context("<dir>")` keeps cookies and one fingerprint across runs; `humanize=True` adds human-like mouse and typing; `proxy=` and `geoip=True` route through a proxy with matching timezone and locale.

## Updates

`cloak-update` runs daily from launchd and at login. It upgrades the wrapper (`uv tool upgrade cloakbrowser`), fetches a newer binary if one exists (`cloakbrowser update`), updates `@playwright/mcp`, and deletes cached binaries that are no longer the active one and that no running browser uses. Results go to `~/Library/Logs/ips-cloakbrowser-update.log`; the job's exit code is non-zero if any step failed.

`cloak-mcp` and `cloak-fetch` set `CLOAKBROWSER_AUTO_UPDATE=false`, so a download never starts in the middle of an agent's request; updating is the job's alone. To update now, run `cloak-update` and read the log tail.

Check the job: `launchctl print gui/$(id -u)/com.intentplex.ips-cloakbrowser.update | grep -E "last exit|runs"`.

## Free binary, free key, Pro

Without a key the wrapper uses the old free build (macOS: Chromium 145, 26 patches), and new binaries rarely arrive. `cloakbrowser login` gets a free key through a GitHub sign-in: the wrapper then downloads the latest build (Chromium 155+, 87 patches) and `cloak-update` keeps it current, but the key allows **one concurrent browser session** — a second agent browsing at the same time is refused. Only the user runs `cloakbrowser login`; it opens their GitHub sign-in and waits for a key pasted from email. `cloakbrowser logout` returns to the keyless build. A paid key raises the concurrency limit.

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
