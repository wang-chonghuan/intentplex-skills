---
name: ips-golive
description: Load when a site is already deployed (a cloud platform URL, a container app, a VPS with a public IP) and now has to become a real public product — bind a custom domain with HTTPS (ips-golive cap2, "绑定域名", "上线到自己的域名"), turn on traffic analytics (cap3, "我想看网站流量", "装个统计"), verify Google Search Console / Bing (cap4), publish robots.txt and sitemap.xml (cap5), or fix link previews and favicons (cap6). Load for "这个站上线还差什么" / "product-ready checklist" — cap1 audits a live site read-only and reports every gap. Do not load for building or deploying the app itself (n-easyapp), for ranking and content strategy (that is SEO work, decided as a product question), or for Cloudflare Workers/Pages development.
---

# ips-golive

The stretch between **deployed** and **product-ready**.

n-easyapp (or any other deploy path) leaves you with a running app on a
machine-generated hostname. ips-golive turns that into a public web property: it
has its own address, it is trusted, it can be shared, it can be crawled, and —
above all — **it is being measured**.

```
n-easyapp / your own deploy  →   ips-golive   →   SEO & content work
app runs at some URL             a real,         being found, being cited
                                 measurable
                                 web property
```

## Why This Is Its Own Skill: Data Does Not Backfill

Search Console, Bing Webmaster and analytics all start recording the day they
are verified. Nothing before that is recoverable. So the correct order is
counter-intuitive: **turn every collector on before you have any strategy**, even
while traffic is zero. A site that waits three months to install analytics has
permanently lost three months of history.

That single fact is why this work must not be deferred into "we'll do it with
the SEO push later", and why it deserves a checklist skill rather than being
remembered ad hoc.

## Preconditions

Per capability, not global — cap1 needs nothing but a URL.

- **A live, publicly reachable deployment.** Everything here is judged from the
  running site, never from a repo.
- **Cloudflare credential** (cap2 for DNS, cap3 for the analytics site, cap4 for
  verification records) exported in the user's shell. The skill reads it from
  the environment and **never prints it, writes it to a file, or puts it in a
  command line**:

  ```bash
  export CLOUDFLARE_API_TOKEN="..."                 # preferred: scoped, revocable
  # or the Global API Key (full account access; must be paired with the email)
  export CLOUDFLARE_EMAIL="you@example.com"
  export CLOUDFLARE_API_KEY="..."
  ```

  These live in `~/.zshrc`; a non-interactive Bash shell must `source ~/.zshrc`.
  Verify with `scripts/cf.sh whoami` before any Cloudflare write. If it fails,
  say which variables are missing — never ask the user to paste a key into the
  conversation.
- **Cloud provider CLI** for cap2's binding step (currently `az` for Azure
  Container Apps, already logged in).
- **A code change path** for capabilities that touch the served HTML (3, 6) or
  the repo (5). In an n-prodfarm repo that means a ticket; see Boundaries.

## Capabilities

Capability numbers are stable user-facing shortcuts. Do not renumber.
**Start with cap1** — it tells you which of the others this site actually needs.

1. `capability-1-readiness-audit`: read-only. Audit a live site across
   reachability, TLS, addressing, identity, share surface, crawl surface and
   measurement, and report every gap as PASS / WARN / FAIL. Changes nothing.
   Read `references/capability-1-readiness-audit/readiness-audit.md`.
2. `capability-2-custom-domain`: bind a custom domain to the deployment with
   auto-renewing HTTPS, plus the `www` → apex redirect. Azure Container Apps is
   the implemented provider. Read
   `references/capability-2-custom-domain/custom-domain.md`.
3. `capability-3-analytics`: real traffic measurement via Cloudflare Web
   Analytics, verified with data rather than a dashboard glance. Read
   `references/capability-3-analytics/analytics.md`.
4. `capability-4-search-consoles`: verify the site in Google Search Console and
   Bing Webmaster Tools and submit the sitemap — the crawl-side telemetry an
   analytics beacon structurally cannot see. Read
   `references/capability-4-search-consoles/search-consoles.md`.
5. `capability-5-crawl-surface`: publish `robots.txt`, `sitemap.xml` and
   `llms.txt` so crawlers and AI answer engines can enumerate the site. Read
   `references/capability-5-crawl-surface/crawl-surface.md`.
6. `capability-6-share-surface`: make a pasted link render as a card — Open
   Graph, Twitter Card, the OG image, favicons and canonical. Read
   `references/capability-6-share-surface/share-surface.md`.

## Scripts

- `scripts/readiness_audit.py <url> [--json]` — cap1. Standard library only;
  exits non-zero if any check FAILs.
- `scripts/cf.sh` — Cloudflare REST/GraphQL transport: `whoami` / `accounts` /
  `zones [name]` / `get` / `post` / `put` / `patch` / `delete` / `graphql`.
  Auto-detects the auth style; non-2xx exits non-zero. It prints
  `[VERB path -> HTTP nnn]` **on stdout**, ahead of the body, so piping straight
  into `jq` or `json.load` fails on that first line — strip it with
  `| tail -n +2`. (n-plane's helper puts its status line on stderr instead; do
  not carry one convention over to the other.)
- `scripts/rum_pageviews.py` — cap3 verification: page views per path; exits
  non-zero on a zero total so "no data" fails a check instead of passing.
- `scripts/bind_cloudflare_domain.py` — cap2 for Azure Container Apps: prints
  the exact DNS records, pre-flights them, then does the whole Azure side.

## Working Rules

- **Judge from the live site.** A repo containing a `sitemap.xml` and a site
  serving one are different facts. Every capability ends in an observation of
  production.
- **Verify with data, not with a dashboard.** An empty panel and a broken
  install look identical for the first two minutes. Prefer a query whose result
  would differ if the work had not happened.
- **Read before you write.** List the existing DNS record / analytics site /
  verification TXT first; a duplicate silently splits data or shadows a record.
- **Never print the credential**, and never put it in a file, a ticket, a commit
  message, or a command line. Public site identifiers (a Web Analytics
  `site_token`, a `google-site-verification` value) are *not* credentials — they
  are meant to be public, and hiding them in env vars is cargo culting.
- **Never flip a hostname between proxied and DNS-only to make a metric work.**
  That single change can break an origin-issued managed certificate. If
  analytics is empty because the host is grey-cloud, the answer is the manual
  beacon (cap3), not the orange cloud.
- **Destructive or externally-visible writes need explicit human approval**:
  deleting a DNS record or zone, changing SSL/TLS mode, purging cache.
- **Report what is not measured.** Beacon analytics misses crawlers, bots and
  blocked visitors; Search Console lags by days. Say so rather than implying a
  number is total traffic.

## Boundaries

ips-golive does not build or deploy the application (n-easyapp or the project's
own path), does not develop Cloudflare Workers/Pages, and does not manage the
registrar. It does not decide **content or ranking strategy** — what to publish,
which keywords to chase, where to promote. That is a product decision; in an
n-prodfarm repo it enters as a seed, not as a skill capability.

Where a capability needs a change to shipped code (caps 3, 5, 6 add tags or
files to the app), ips-golive prepares and verifies it but hands the edit to the
repo's own development loop. In an n-prodfarm repo that is a ticket — type
**enabler**, since it adds a user-invisible capability to shipped code (a *fix*
may not add a capability; a *chore* may not touch shipped code).
