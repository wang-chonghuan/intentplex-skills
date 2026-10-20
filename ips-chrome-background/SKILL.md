---
name: ips-chrome-background
description: Load when the user wants webpage work through the official Chrome extension in dedicated background tabs without taking over their mouse, keyboard, foreground window or current tab, or asks to reuse logged-in Chrome without desktop automation.
---

# ips-chrome-background

Operate the user's existing Chrome through its official extension using DOM
reads and Playwright locators. Keep the user's foreground activity untouched.
This is a browser interaction method, not permission to submit, send, delete,
change accounts or run a project's tests.

## Start

Use `mcp__cua_repl.js`. On a fresh runtime, the first call is only
`await cua.getState();`. Inspect the returned browser inventory and select
Chrome with `type: "extension"` through the documented browser entrypoint.
Do not select a native Chrome app, the in-app browser or a CDP connection.
After a context summary, use `await cua.rewriteDocumentation();` before
continuing. Reuse a valid existing browser binding.

Read the effective browser documentation. When it exposes the native
`browser.tabs` interface, use that documented `browser` handle. Do not assume
the generic `cua.getBrowser()` facade has the same methods.

Before opening or claiming tabs, name the session as its documentation requires.
Create a dedicated task tab with **`await browser.tabs.new()`**. This was
verified to create a background tab on the connected Chrome extension.
The generic `cua.createBrowserTab(..., { visible: false })` failed there with
an unsupported visibility capability; that is not evidence that background
extension operation is unavailable.

For setup and working examples, read [references/background-tabs.md](references/background-tabs.md).
The examples use the host runtime, not a terminal Playwright installation.
Follow newly returned API documentation if the available surface changes.

## Work

Navigate only the task tab. Read its DOM, then use `taskTab.playwright`
locators such as `getByRole`, `getByLabel`, `getByTestId`, `click` and `fill`.
Inspect the resulting DOM or the relevant control state before the next
decision. For a contenteditable textbox, verify `innerText()` rather than
`.value`; clear only text this task entered, never an existing draft.

Reuse Chrome's current login, but verify the required account before an
account-specific action. Being signed in is not evidence of the right identity.
Never export cookies or tokens to emulate the session elsewhere.

## Do Not Take Over

- No `@Computer`, native app actions, coordinate clicks, system typing,
  clipboard input, AppleScript, or OS input automation.
- No window activation, tab selection, `bringToFront`, focusing management
  updates, or switching a user-owned tab.
- Do not use generic native-input wrappers such as `tab.click`,
  `tab.typeText`, `tab.pressKey` or `tab.paste`; use the extension's DOM locators.
- No fallback to desktop input, another browser, CDP or a separately launched
  Playwright browser when the extension cannot finish a step.

Check at setup that creating and navigating the task tab did not activate it.
The documented `management` capability's read-only tab/window queries can
verify this requested boundary; do not organize or modify the user's tabs.
If foreground behavior is uncertain or changes unexpectedly, stop and explain.
Never "repair" it by switching the user's tab back. A human may change tabs
while the task runs; do not mistake that for permission to seize focus.

If a method is missing, inspect `browser-troubleshooting` and the effective
documented alternatives. If no allowed DOM method completes the step, stop
that browser step, preserve progress and report the specific missing capability.
Do not claim that a full native Playwright test ran when only its UI actions
were explored through the extension.

Leave user-owned tabs alone. Let routine task tabs close automatically at turn
end; use `markHandoff()` only for an unfinished live workflow that must continue,
or `markDeliverable()` for a user-requested live output.
