## Web access: CloakBrowser

Open, read and interact with public web pages through CloakBrowser, the local stealth Chromium:

- Browser tools: the `cloakbrowser` MCP server (Playwright MCP on the CloakBrowser binary; headless, fresh in-memory profile per session).
- One-shot page read from the shell: `cloak-fetch <url>` prints the rendered text; `--html`, `--screenshot <file>`, `--wait 8` for challenge pages. In a sandboxed shell, run it with network access outside the sandbox.

Use these instead of other fetch tools or built-in browsers for web pages. A search tool may still be used to find URLs. Exceptions: the user names another browser, the task needs the user's own signed-in Chrome session, or the page is a local dev server preview.

The license allows one open browser across all agents and sessions, so:

- Prefer `cloak-fetch` for reading a page; it opens and closes its browser and queues for the seat by itself.
- Call `browser_close` as soon as a browser-tool task is finished. An idle browser otherwise holds the seat for 3 minutes.
- A browser tool failing with `Target page, context or browser has been closed` and `exitCode=76` in its log, or `cloak-fetch` exiting with 75, means another session holds the seat. Wait a minute and retry for up to 5 minutes, then tell the user the seat is busy.

Setup, updates and troubleshooting: the `ips-cloakbrowser` skill.
