# Capability 4: Search Consoles

Verify the site in Google Search Console and Bing Webmaster Tools, and submit
the sitemap. This is the **crawl-side** telemetry — what an analytics beacon
structurally cannot see.

## Why Both, And Why Now

A beacon only fires in a real browser that runs JavaScript. Every crawler is
therefore invisible to it. Search Console answers the questions the beacon
cannot: *is the site indexed at all, which queries surface it, at what position,
and did anything break during crawling.*

**Do this while traffic is still zero.** Search Console history begins at
verification and is never backfilled. Two minutes of work now buys months of
history later; skipping it is a permanent loss, not a delay. When a user asks
whether it is "necessary", that is the honest argument — not that it is urgent.

Both consoles are **free** and need only an existing Google / Microsoft account.

## Preconditions

- The site is on a custom domain (cap2) — verify the domain, not a platform
  hostname you do not control.
- Cloudflare credential exported (see SKILL.md); `cf.sh whoami` succeeds.
- A `sitemap.xml` exists (cap5) — or expect to come back after cap5.

## What The Agent Can And Cannot Do

**Cannot**: log into the user's Google or Microsoft account. Never ask for those
credentials and never attempt the sign-in flow.

**Can**: everything on the DNS side, and every verification afterwards.

So the split is:

1. **User** opens the console and starts a *Domain* property → the console shows
   a TXT value.
2. **User** hands over that value — it is a public verification string, not a
   secret, so it is fine in chat.
3. **Agent** adds the DNS record and confirms it resolves.
4. **User** clicks Verify.
5. **Agent** confirms and submits the sitemap.

Tell the user exactly this split up front, so they know which two clicks are
theirs.

## Workflow

### 1. Point the user at the right property type

- Google: <https://search.google.com/search-console> → Add property →
  **Domain** (not "URL prefix").
- Bing: <https://www.bing.com/webmasters> → Add site. Bing can **import from
  Google Search Console**, which skips its own verification entirely — offer
  that first, it is usually one click.

"Domain" property is the right choice: it covers every subdomain and both
protocols with one DNS record, and it is what a DNS-verification flow expects.

### 2. Add the verification TXT record

Read the existing TXT records first — a zone often already carries SPF or other
verification strings, and TXT records must be **added, never replaced**:

```bash
<skill-dir>/scripts/cf.sh get "zones/<ZONE_ID>/dns_records?type=TXT&name=example.com"
```

If the listing already shows the value, **the record is done** — the user may
have added it themselves. Say so and move on; do not create a second one.

Otherwise create the record at the **zone apex**:

```bash
<skill-dir>/scripts/cf.sh post "zones/<ZONE_ID>/dns_records" \
  '{"type":"TXT","name":"example.com","content":"google-site-verification=XXXX","ttl":300}'
```

Bing's value looks like `MS=msXXXXXXXX` and is added the same way, as a separate
record.

Confirm it is visible before telling the user to click Verify — DNS propagation
is the usual cause of a failed verification. **Query a public resolver, not the
local one**: a local resolver can still be serving a cached negative answer for
a record that is already live worldwide, which reads as "the record is missing"
and invites adding a duplicate.

```bash
dig +short TXT example.com @8.8.8.8      # what the verifying service sees
dig +short TXT example.com               # local view; may lag, and that is fine
```

Judge from the public resolver. A record visible there is ready to verify even
while the local one is still empty.

### 3. Submit the sitemap

After the user reports the property verified:

- Google: Search Console → Sitemaps → submit `https://example.com/sitemap.xml`.
- Bing: Sitemaps → submit the same URL.

Both are UI actions in the user's account. Confirm the sitemap is actually
served (`curl -sI https://example.com/sitemap.xml` → 200) before asking them to
submit it, so a failed submission is never our fault.

### 4. Set expectations, explicitly

- **Verification is instant; data is not.** Expect **2–3 days** before impressions
  appear, and longer before position data is meaningful. A user who checks the
  next morning and sees an empty report will think it is broken — say this
  before they look.
- A brand-new site with no backlinks may show almost nothing for weeks. That is
  the site's reality, not a setup failure.

### 5. Verify from our side

The one thing we can check without their account:

```bash
python3 <skill-dir>/scripts/readiness_audit.py https://example.com | grep -i verified
```

The audit reads the DNS TXT records, so a PASS here proves the record we added
is live. It does **not** prove the user clicked Verify — ask them to confirm.

## Traps

- **Replacing instead of adding TXT records.** Overwriting an existing TXT can
  break SPF/DKIM and silently kill the domain's email. Always list first, always
  create a new record.
- **Verifying a platform hostname** (`*.azurecontainerapps.io`,
  `*.vercel.app`). You do not control that domain, the data is not portable, and
  it may already be verified by the platform. Verify the custom domain.
- **Proxy status is irrelevant here.** Unlike cap3, a TXT record works
  identically whether the host is proxied or DNS-only — do not touch the cloud
  setting.
- **Ownership.** The property lives in the user's Google account. If they later
  want a teammate to see it, that is a sharing setting inside Search Console,
  not something to re-verify.
