# Capability 2: Custom Domain

Take a service that is already deployed and reachable at a machine-generated
hostname, and put it on a custom domain with a valid, auto-renewing HTTPS
certificate — plus the `www` → apex redirect. This is the first step that makes
a deployment feel like a product.

**Implemented provider: Azure Container Apps, with DNS in Cloudflare.** The
procedure below is that path, followed exactly; it takes minutes rather than the
multi-hour cert-stuck detour it replaces. For another origin (Vercel, Fly, a VPS
behind nginx) the shape is the same — point DNS at the origin, prove ownership,
let the origin issue the certificate — but the commands differ, and the
proxied/DNS-only rule below still decides everything. Do not assume a different
provider's managed certificate tolerates a proxied host; check its docs first.

(This capability moved here from `n-azure` cap3, which now delegates to it.)

## First cause

The service works at its Azure default URL (`<app>.<region>.azurecontainerapps.io`).
The user wants it reachable at `example.com` (and usually `www.example.com`) over
HTTPS. Azure Container Apps custom domains are more manual than Vercel/Netlify:
the domain must be **added and bound with a certificate** before ingress will
even route it. The whole job is: point Cloudflare DNS at the app, add + bind the
domain on Azure, verify.

## Who does what (decide the boundary deliberately)

- **User (Cloudflare UI only — the agent cannot do this without a Cloudflare API
  token):** add the DNS records and, for a root domain, create the `www → apex`
  redirect rule. Toggling a record's grey/orange (proxy) state is user-side too.
- **`scripts/bind_cloudflare_domain.py` (deterministic):** read the Azure
  verification id / static IP / FQDN, print the exact records to add, **pre-flight
  the DNS** (catches the #1 mistake — a proxied apex), add the hostname, bind the
  managed cert with **HTTP validation**, poll to a terminal state, verify HTTPS.
- **Agent (semantic):** decide apex vs subdomain, generate/repeat the record list
  for the user, interpret failures against the Gotchas below, and explain.

## Preconditions

1. `az login` done; `az account show` succeeds; the right subscription active.
2. The target is an Azure Container App with **external ingress** enabled.
3. The domain's zone is active in the user's Cloudflare account.
4. You know: resource group, Container App name, the managed environment name,
   and the desired hostname.

## The procedure

### Step 1 — show the user what to add in Cloudflare

Run with `--print-dns-only` to compute and print the records from live Azure state:

```bash
python scripts/bind_cloudflare_domain.py --hostname example.com \
  --containerapp <app> --resource-group <rg> --environment <env> --print-dns-only
```

For an **apex/root** domain (`example.com`) the user adds, in the Cloudflare zone:

| Type  | Name          | Value / Content                     | Proxy            |
|-------|---------------|-------------------------------------|------------------|
| A     | `@`           | `<environment staticIp>`            | **DNS only (grey)** |
| TXT   | `asuid`       | `<customDomainVerificationId>`      | —                |
| CNAME | `www`         | `example.com`                       | **Proxied (orange)** |

For a **subdomain** (`app.example.com`): one `CNAME app → <app FQDN>` **grey**,
plus `TXT asuid.app = <customDomainVerificationId>`. No www redirect needed.

Then, for a root domain, the user creates a **Redirect Rule** (Rules → Redirect
Rules) so `www` folds into the apex:

- When: Hostname equals `www.example.com`
- Then: 301, dynamic → `concat("https://example.com", http.request.uri.path)`

### Step 2 — bind on Azure (agent runs this)

After the user confirms the records are in, run the script **without**
`--print-dns-only`. It pre-flights DNS, then adds + binds:

```bash
python scripts/bind_cloudflare_domain.py --hostname example.com \
  --containerapp <app> --resource-group <rg> --environment <env>
```

It defaults to `--validation HTTP`, waits for the cert (up to ~20 min, usually a
few), confirms `bindingType=SniEnabled`, and curls `https://example.com`.

### Step 3 — verify

- `curl -s -o /dev/null -w "%{http_code} verify=%{ssl_verify_result}\n" https://example.com/`
  → `200 verify=0`.
- `curl -s -o /dev/null -w "%{http_code} -> %{redirect_url}\n" https://www.example.com/`
  → `301 -> https://example.com/`.
- Cert should be DigiCert-issued, `subject=CN=example.com`.

## Gotchas (every one of these actually bit; do not relearn them)

1. **Use HTTP validation for the managed cert, not TXT.** `--validation-method TXT`
   makes the cert wait for a **validation-token** TXT record (`asuid.<host>` =
   the cert's `validationToken`, a *different* value from the
   customDomainVerificationId). If you don't add that token, the cert sits
   **Pending forever**. HTTP validation needs **no extra record** — the app is
   already reachable at the apex — so it just works. (CNAME validation is fine for
   subdomains too.) This one mistake caused ~50 minutes of dead "Pending".

2. **The served apex must be GREY (DNS only) when using the Azure managed cert.**
   If the apex A record is **orange (proxied)**:
   - cert issuance hangs — Azure can't reach the origin to validate;
   - and browsing gives Cloudflare **error 525** (Cloudflare → Azure origin TLS
     fails, because Azure has no bound cert yet).
   The pre-flight in the script flags a proxied apex (it resolves to Cloudflare
   IPs `104.x` / `172.67.x` instead of the Azure static IP). Fix = set the apex
   record to DNS only.

3. **Two different `asuid` values — don't confuse them.**
   `asuid.<host> = customDomainVerificationId` proves **domain ownership** for
   `hostname add`. The cert's `validationToken` is a **separate** value only
   relevant if you (against advice) pick TXT cert-validation. Ownership TXT stays;
   you do not overwrite it with the token.

4. **`www` must be ORANGE (proxied) for the redirect rule to fire.** Cloudflare
   Redirect Rules only run on proxied traffic. A grey `www` bypasses Cloudflare
   and hits Azure directly (which has no cert for `www`) → cert error. Orange `www`
   never reaches the origin — the 301 happens at Cloudflare's edge.

5. **`hostname add` alone does not route.** An added-but-unbound domain shows
   `bindingType: Disabled` and won't serve. Routing needs a **bound cert**
   (`SniEnabled`). The script always binds.

6. **Cert issuance is slow and macOS lacks `timeout`.** Allow up to 20 minutes;
   poll. Do not wrap `az` in the GNU `timeout` command on macOS (it's absent — use
   `gtimeout` or none). The script polls internally.

7. **A stuck (long-Pending) managed cert should be deleted and re-created**, not
   waited on, once you've fixed the root cause:
   `az containerapp env certificate delete -g <rg> -n <env> --certificate <mc-...> --yes`,
   then re-bind.

## Want Cloudflare's CDN/WAF on the served domain? (optional, advanced)

The simplest stable end state is **grey apex + Azure managed cert** (above). If the
user specifically wants Cloudflare proxying (orange) on the served host:

- **Option A — flip after binding:** issue + bind the Azure managed cert with the
  apex grey (needs grey), then set the apex to orange and Cloudflare SSL/TLS mode
  to **Full (strict)**. Now Cloudflare serves the edge cert to browsers and
  validates the Azure cert on the origin leg.
- **Option B — Cloudflare Origin Certificate (no grey step):** the user generates
  an Origin Certificate (Cloudflare → SSL/TLS → Origin Server → Create Certificate,
  hostnames `example.com` + `*.example.com`), the agent converts PEM→PFX
  (`openssl pkcs12 -export ...`), uploads it as a bring-your-own cert
  (`az containerapp env certificate create --certificate-file cert.pfx --password ...`)
  and binds it (`az containerapp hostname bind --certificate <name>`), then the
  user sets SSL/TLS mode to **Full (strict)** and keeps everything orange. Handle
  the private key via local files (keep it out of chat); the Origin Cert is
  revocable in Cloudflare at any time.

Default to grey + managed cert unless the user asks for proxying.

## Reporting

Report the final HTTPS URL, `bindingType=SniEnabled`, the cert issuer/subject, the
`www` redirect result, and the stable DNS layout (grey apex, `asuid` TXT, orange
`www` + redirect). Never print Cloudflare API tokens or a cert private key.
