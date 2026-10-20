# Background Chrome Extension Pattern

Verified on 20 October 2026: a task tab was created, navigated to a signed-in
application, read through DOM snapshots, clicked through role locators, and
filled/cleared without sending a message. The task tab never became active.
The generic `visible: false` creation option was unavailable; the native
`browser.tabs.new()` interface worked.

Examples assume the official extension has been selected and its returned
documentation exposes the native handle `browser`. Substitute the actual
approved target, control labels and session name; do not hardcode browser IDs,
tab IDs, account details or application URLs from a previous session.
Run these through `mcp__cua_repl.js`, not shell JavaScript.

## Create And Check Once

```javascript
await browser.nameSession("🔎 Background task");
let management = await browser.capabilities.get("management");
nodeRepl.write(await management.documentation());
```

Read the capability's documentation before calling its methods. Use its
read-only observations only to verify the user's requested no-focus boundary.

```javascript
let activeBefore = await management.tabs.query({ active: true });
let taskTab = await browser.tabs.new();
let activeAfter = await management.tabs.query({ active: true });
nodeRepl.write({
  taskTabId: taskTab.id,
  activeBefore: activeBefore.map(tab => tab.id),
  activeAfter: activeAfter.map(tab => tab.id),
  taskActivated: activeAfter.some(tab => String(tab.id) === taskTab.id),
});
```

If the task activated or foreground behavior is uncertain, stop. Do not use
`management.tabs.update(..., { active: true })` or window focusing to restore
the user's previous state. Creating no tab is preferable to stealing focus.

## Navigate And Read

```javascript
await taskTab.goto(targetURL);
nodeRepl.write(await taskTab.playwright.domSnapshot());
nodeRepl.write({
  taskActivated: (await management.tabs.query({ active: true }))
    .some(tab => String(tab.id) === taskTab.id),
});
```

When the snapshot shows loading, use the documented locator wait for the
expected ready element or read the settled state. Do not activate the tab.
Do not reload a tab already at its intended URL unless a reload is needed.

## Click And Fill

Choose locators from the observed DOM, not guessed labels:

```javascript
await taskTab.playwright.getByRole("button", {
  name: observedButtonName, exact: true,
}).click();
nodeRepl.write(await taskTab.playwright.domSnapshot());
```

For an explicitly authorized unsent draft check:

```javascript
let textbox = taskTab.playwright.getByRole("textbox", {
  name: observedTextboxName, exact: true,
});
```

Inspect its DOM type and current text first. For `contenteditable="true"`,
check `innerText()`; for a native input/textarea, use read-only DOM evaluation
of its value. Do not overwrite nonempty existing content.

```javascript
await textbox.fill(probeText);
nodeRepl.write(await textbox.innerText());
await textbox.fill("");
nodeRepl.write(await textbox.innerText());
```

The last example is for an initially empty contenteditable textbox. It checks
fill/clear, not submission or persistence. No Send click occurs. Never use
page evaluation to mutate the DOM, dispatch input or bypass the application's
controls; use documented locator methods.

## Missing Capabilities

`taskTab.playwright` is a documented extension subset, not a full Node
Playwright `Page`. Do not invent network listeners, request contexts, browser
launchers or unsupported methods. Read the effective documentation, use an
allowed alternative if it actually proves the requested outcome, otherwise
report the gap without claiming completion.
