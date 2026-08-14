# Capability 3: Analytics

Give a site real traffic measurement through Cloudflare Web Analytics, and prove
it works with data rather than with a dashboard screenshot.

## When To Use

- "I want to see this site's traffic"
- "add analytics / 装个统计"
- "the Cloudflare traffic dashboard is empty for my domain"
- "do I need Google Analytics?"

## The Decision That Governs Everything: Proxied Or Not

**Check this first — it determines the only correct install mode.**

```bash
dig +short <hostname> A          # Cloudflare IPs (104.x / 172.67.x) => proxied
curl -sI https://<hostname>/ | grep -i cf-ray   # a cf-ray header => proxied
```

| Served hostname | What Cloudflare sees | Install mode |
|---|---|---|
| **Proxied (orange)** | every request | `auto_install: true` is available; CF injects the beacon itself |
| **DNS only (grey)** | nothing | **`auto_install: false` + a manual beacon `<script>` in the app** |

A grey-cloud hostname is common and often mandatory — most importantly, a host
fronted by an **origin-issued managed certificate (e.g. an Azure Container Apps
managed cert)** must stay DNS-only or the certificate stops validating and
renewing. Do **not** propose turning the apex orange to make analytics work: that
trades a working certificate for a dashboard.

The failure this prevents: on a grey apex, Cloudflare's dashboard traffic
analytics is **permanently empty** no matter how long you wait, because no
request ever reaches Cloudflare. Users read that as "analytics is broken" when
it is really "analytics was never wired". Say this out loud before installing.

## Preconditions

- The credential from the skill's Preconditions section is exported (`cf.sh whoami` succeeds).
- The zone exists in the account (`cf.sh zones <domain>` resolves it).
- You can edit and redeploy the site's HTML. If the site is a repo running a
  ticket-governed loop (n-prodfarm), the code edit needs a ticket — see
  "Handoff" below.

## Workflow

### 1. Resolve account and zone

```bash
<skill-dir>/scripts/cf.sh accounts
<skill-dir>/scripts/cf.sh zones example.com
```

Keep the account id and zone id; both are needed below.

### 2. Reuse or create the RUM site

List first — creating a second site for a host that already has one splits the
data silently.

```bash
<skill-dir>/scripts/cf.sh get "accounts/<ACCOUNT_ID>/rum/site_info/list?per_page=50"
```

If the host is absent, create it. For a grey-cloud host, `auto_install` **must**
be `false`:

```bash
<skill-dir>/scripts/cf.sh post "accounts/<ACCOUNT_ID>/rum/site_info" \
  '{"zone_tag":"<ZONE_ID>","auto_install":false}'
```

**If the site already exists, check `auto_install` — do not just take the
token.** A site created earlier (often by clicking "Add a site" in the
dashboard, which defaults to auto-install) will carry `auto_install: true`. On a
grey-cloud host that is not merely inert: **the manual beacon fires correctly in
the browser and Cloudflare records nothing.** Fix it in place — the `site_token`
is preserved, so no code change and no redeploy:

```bash
<skill-dir>/scripts/cf.sh put "accounts/<ACCOUNT_ID>/rum/site_info/<SITE_TAG>" \
  '{"zone_tag":"<ZONE_ID>","auto_install":false}'
```

Note the verb: this endpoint takes **PUT**. `patch` returns 405.

The response carries `site_tag` (identifies the site to the API) and
`site_token` (identifies the site to the beacon). **`site_token` is a public
site identifier, not a credential** — it is meant to sit in shipped HTML and may
be committed. Do not treat it as a secret; do not put it in an env var and
pretend it is one.

### 3. Install the beacon in the app

One deferred `<script>`, no npm dependency:

```html
<script defer src="https://static.cloudflareinsights.com/beacon.min.js"
        data-cf-beacon='{"token": "<SITE_TOKEN>"}'></script>
```

Rules:

- **Add no dependency.** There is no package to install; a plain tag is the
  whole integration. A repo with a no-gratuitous-dependency rule would reject
  anything more.
- **`defer`** so it never blocks first paint.
- Place it in the document body (or head) of the app's root document. In a
  framework that renders the whole document (TanStack Start, Next, Remix), put it
  in that root document component so every route inherits it.
- In JSX, pass the config as a real attribute value, e.g.
  `data-cf-beacon={JSON.stringify({ token: SITE_TOKEN })}`.
- Keep the token in one named constant next to the site's other public
  site-level constants, not inline in markup.
- **Emit it in production builds only.** A tag placed unconditionally in the
  root document also ships in the dev server, so every `npm run dev` page load
  reports a page view into the live site's analytics. Gate it on the build
  mode — `import.meta.env.PROD` (Vite/Astro), `process.env.NODE_ENV ===
  'production'` (Next, Remix) — and verify both directions, because the
  production side passing says nothing about the dev side:

  ```bash
  curl -s https://<hostname>/          | grep -c beacon.min.js   # expect 1
  curl -s http://localhost:<devport>/  | grep -c beacon.min.js   # expect 0
  ```

  This one is worth the extra check because it is **not correctable after the
  fact**: no API removes individual page views. The only reset is deleting the
  RUM site, which throws away the real history along with the noise. On a site
  with weeks of traffic the pollution is negligible; on a site that launched an
  hour ago, local development can be most of what the dashboard shows.

Cookie-free and carrying no personal data, this adds **no consent-banner
obligation** — a genuine advantage over Google Analytics worth stating when the
user is choosing.

### 4. Deploy, then verify with data

Ship it the way that site normally ships. Then verify in this order — each step
rules out a different failure.

**(a) The tag reached production.**

```bash
curl -s https://<hostname>/ | grep -c beacon.min.js     # expect 1
```

**(b) A real browser actually fires the beacon.** Load the production page in a
browser and read the resource timings:

```js
performance.getEntriesByType('resource')
  .map(r => r.name).filter(n => /cloudflareinsights/.test(n))
```

Expect **two** entries: `static.cloudflareinsights.com/beacon.min.js` (the
script) and `cloudflareinsights.com/cdn-cgi/rum` (the upload). The second one is
the page view.

**(c) Cloudflare recorded it** — the only real proof:

```bash
python3 <skill-dir>/scripts/rum_pageviews.py \
  --site-tag <SITE_TAG> --account <ACCOUNT_ID> --hours 2
```

Visit two or three distinct paths first, then confirm those exact paths come
back. Matching paths — not merely a non-zero number — is what proves this
beacon, on this site, is reporting.

### 5. Report honestly

State what is measured and what is not (see Known Limits).

## Two False Alarms — Do Not Chase These

Both look like failures and are not. Recognising them saves a debugging spiral.

1. **`responseStatus: 0` on the beacon resources.** Cross-origin responses
   without `Timing-Allow-Origin` hide their status from the page. It is not an
   error. Judge success from step 4(c), never from a client-side status code.

2. **A hand-written `fetch()` to `/cdn-cgi/rum` fails with "Failed to fetch".**
   That endpoint does not accept an arbitrary cross-origin `fetch` with custom
   headers; the real beacon uses `sendBeacon`. A failed manual probe says
   nothing about whether the beacon works.

And one real timing trap: **ingestion lags roughly 1–2 minutes**. A `0` right
after visiting means "wait and re-run", not "broken".

**But do not keep polling past ~5 minutes.** If 4(b) passes — the browser really
fetched `cdn-cgi/rum` — and 4(c) is still 0, it is not timing. Diagnose in this
order, it takes one query each:

1. **Is the tool or the dataset at fault?** Query the account with **no**
   `siteTag` filter over a week. If other sites return rows, the transport is
   fine and the problem is this site.

   ```bash
   <skill-dir>/scripts/cf.sh graphql @/tmp/q.json   # rumPageloadEventsAdaptiveGroups, no siteTag filter
   ```

2. **Compare `auto_install` against the sites that DO report.** This is the
   usual answer on a grey-cloud host: a site left at `auto_install: true` accepts
   the beacon in the browser and records nothing. Flip it with `cf.sh put` (step
   2) and re-visit; data lands a few minutes later, and the `site_token` does not
   change.

Only after both come back clean is "wait longer" the right conclusion.

## Known Limits (state these to the user)

- Only **real browsers that execute JavaScript** are counted. **Crawlers and SEO
  bots are invisible** — for crawl and search-impression data, point the user at
  Google Search Console instead; the two are complementary.
- Visitors with an ad/tracker blocker may not report.
- It measures page views, referrers, paths, devices and Core Web Vitals — not
  conversion funnels or per-user attribution. If the user needs those, GA4 is the
  honest recommendation, together with its consent-banner cost.
- The dashboard's smallest window is 30 minutes, so this is "near real time"
  (~1–2 min), not a live ticker. If the user wants to watch a launch minute by
  minute, say so and offer GA4 Realtime or a server-side request log.

## Handoff

Steps 1–2 are Cloudflare-side and belong to this skill. Step 3 edits shipped
application code: in a repo governed by n-prodfarm that requires a ticket
(type **enabler** — it adds a user-invisible capability to shipped code; a *fix*
may not add a capability and a *chore* may not touch shipped code). File it,
develop and verify against its acceptance criteria, then close it through the
normal channel. Do not edit product code from this skill without that ticket.
