## Web access: CloakBrowser

Open, read and interact with public web pages through CloakBrowser, the local stealth Chromium:

- Browser tools: the `cloakbrowser` MCP server (Playwright MCP on the CloakBrowser binary; headless, fresh in-memory profile per session).
- One-shot page read from the shell: `cloak-fetch <url>` prints the rendered text; `--html`, `--screenshot <file>`, `--wait 8` for challenge pages. In a sandboxed shell, run it with network access outside the sandbox.

Use these instead of other fetch tools or built-in browsers for web pages. A search tool may still be used to find URLs. Exceptions: the user names another browser, the task needs the user's own signed-in Chrome session, or the page is a local dev server preview.

Setup, updates and troubleshooting: the `ips-cloakbrowser` skill.
