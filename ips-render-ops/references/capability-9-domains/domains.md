# Capability 9: Custom Domains

Pointing a real domain at a Render service when DNS lives somewhere else —
Cloudflare, in the case this was written from.

For what Render supports, read the official **`render-domains`** skill. This
file is the sequence that actually works, and the two places it goes wrong.

## Order matters

1. Add the domain to the service **first**. It is inert until DNS points at it,
   so this is safe to do well before any cutover.
2. Change DNS.
3. Ask Render to verify.
4. Wait for the certificate.

Doing (2) before (1) gives you a window where the domain resolves to a Render
service that does not recognise it, and Render answers with an error page.

## Add

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
curl -s -X POST "https://api.render.com/v1/services/<srv-id>/custom-domains" \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
  -d '{"name":"example.com"}'
```

Adding the apex often creates the `www` record too, as a redirect. A second POST
for `www` then returns **409** — that is "already exists", not a failure.

## Point DNS at it

Render's apex address is anycast and resolves to more than one IP, so an A
record pinned to one of them is fragile. Where the DNS provider supports **CNAME
flattening** at the apex — Cloudflare does — use a CNAME for both names:

```
example.com        CNAME  <service>.onrender.com
www.example.com    CNAME  <service>.onrender.com
```

**Turn the proxy off (DNS-only / grey cloud) until the certificate is issued.**
Render validates over the same hostname it is trying to certify; a proxy in
front of it can prevent that. Turning it back on afterwards is a separate
decision.

## Verify and wait

```bash
curl -s -X POST \
  "https://api.render.com/v1/services/<srv-id>/custom-domains/<cdm-id>/verify" \
  -H "Authorization: Bearer $RENDER_API_KEY"     # -> 202

curl -s "https://api.render.com/v1/services/<srv-id>/custom-domains" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  | python3 -c "
import sys,json
for r in json.load(sys.stdin):
    c=r.get('customDomain',r); print(c['name'], c['verificationStatus'])"
```

`verified` means Render is willing to serve the name. **It does not mean the
certificate exists yet** — those are separate steps, minutes apart. Poll for the
thing you actually need:

```bash
until curl -sf -o /dev/null https://example.com/; do sleep 30; done
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -issuer -subject -dates
```

## Prove Render is the one answering

After a cutover from another host, a 200 proves nothing — caches and old records
outlive the change. The response headers name the origin:

```bash
curl -sI https://example.com/ | grep -iE '^(x-render-origin-server|rndr-id|cf-ray)'
```

`x-render-origin-server: Render` is the answer. `cf-ray` additionally tells you
which Cloudflare edge served it, which is a useful sanity check on geography.

## Before cutting over from another platform

If the old platform still runs scheduled jobs against a **different** database,
stop them before DNS moves. Otherwise both platforms write, to two databases,
and the two diverge from the moment of the switch — silently, because each looks
healthy on its own.
