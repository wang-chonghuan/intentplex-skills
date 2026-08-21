# Capability 1: Status

One picture of the project: every service, whether it is live, and what it last
deployed. Read-only — safe to run any time.

## Run

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"

render services --output json --confirm | python3 -c "
import sys, json
rows = json.load(sys.stdin)
for r in rows:
    s = r['service']
    print(f\"{s['id']}  {s['type']:<8} {s['suspended']:<9} {s['name']}\")
"
```

`suspended: not_suspended` is the healthy value. A `suspended` service is not
running and will not run on schedule either.

## Then look at the thing itself

A service list says a service exists, not that it works. For the web service,
the authoritative check is the page:

```bash
URL=<the production URL>
body=$(mktemp)
code=$(curl -s -o "$body" -w '%{http_code}' "$URL/")
bytes=$(wc -c < "$body" | tr -d ' ')
rm -f "$body"
echo "$code  $bytes bytes"
```

A server-rendered page is comfortably over 4 kB. **200 with 1 kB is a shell that
failed to render, and it is the failure this check exists to catch** — the
status API reports that service as perfectly healthy.

## Cron jobs

A cron job is "live" between runs while doing nothing, so its status tells you
almost nothing. What matters is whether its **last run** succeeded, and that is
capability 2 — read its logs.

## Reporting

Report per service: type, name, suspended state, and for the web service the
status code and byte count you actually observed. Never report "all healthy"
from the service list alone.
