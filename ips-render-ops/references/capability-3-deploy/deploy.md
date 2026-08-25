# Capability 3: Deploy

Put a specific commit into production, and prove that is what is running.

**Find out which mode the project is in before anything else.** Render has two
completely different deploy stories, and which one you are in is not visible
from the repository:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
render services --output json --confirm | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    s = s.get('service', s)
    if not s.get('type'): continue          # datastores carry no type — see trap 1
    print(f\"{s['name']:<30} {s['type']:<12} autoDeploy={s.get('autoDeploy')}\")
"
```

- **`autoDeploy=yes`** — merging to the tracked branch publishes. Your job is
  the *verify* section below and nothing else.
- **`autoDeploy=no`** — merging changes nothing that runs. Publishing is the
  explicit act described here.

A project can be mixed, and mixed is the worst case: the web service updates on
merge and the cron jobs silently do not, or the reverse. Read the whole list,
not the first row.

## The manual release

A release is **one commit across every service**, not a deploy of the one you
were thinking about. Cron jobs each run their own image; deploying only the web
service leaves them on old code — and they keep exiting 0 while doing it, which
is the failure that looks like nothing at all.

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
SHA=$(git rev-parse HEAD)          # confirm this commit is actually on the tracked branch

# `.get('type')`, never `['type']` — see the listing trap below.
render services --output json --confirm | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    s = s.get('service', s)
    if s.get('type') in ('web_service', 'cron_job'): print(s['type'], s['id'], s['name'])
" > /tmp/svc.txt

# Web services take an explicit commit. Cron jobs do not — see below.
awk '$1=="web_service"{print $2}' /tmp/svc.txt | while read -r id; do
  render deploys create "$id" --commit "$SHA" --wait --output text --confirm || echo "FAIL $id"
done
awk '$1=="cron_job"{print $2}' /tmp/svc.txt | while read -r id; do
  curl -s -o /dev/null -w "%{http_code} $id\n" -X POST \
    -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
    "https://api.render.com/v1/services/$id/deploys" -d '{}'
done
```

Then **poll until every service reports `live` on the commit you meant** — the
verify section below is not optional here, because the cron half of this ran
without `--wait`.

### Three traps in that loop, all of which produce a silent partial release

**1. The services listing contains datastores, and they have no `type`.** A
Postgres entry deserializes as `{'environment', 'postgres', 'project'}` — no
`type`, no `name`. Writing `s['type']` raises `KeyError` **mid-iteration**, so
the loop does not crash loudly at the start; it emits some services, dies, and
leaves you with a truncated list. Worse, the datastore can sort ahead of the web
service, in which case the one service you actually care about is the one
silently missing. Always `.get('type')`.

**2. Render refuses `--commit` for cron jobs.** The API answers
`400: cannot deploy cron job service <id> by commit reference ID`. Only web
services can be pinned to a commit; a cron job deploys the tracked branch's
head. So a "release one commit everywhere" loop **cannot** be uniform — pin the
web service, and make sure the branch head *is* that commit before firing the
crons.

**3. `--wait` on a cron job can latch onto the wrong deploy and hang forever.**
Observed: `render deploys create <cron> --wait` sat printing
`Waiting for deploy dep-XXXX to complete...` for over ten minutes while the API
reported that service's newest deploy already `live` — a different id. Do not
use `--wait` for cron jobs; fire them and poll the API.

A single service — a rebuild after an env change, or re-running an
infrastructure failure — is one `render deploys create`, no loop.

## The trap: `autoDeploy: false` does not mean "nothing happens on push"

If the project has a Blueprint with `autoSync: true`, then **configuration still
applies on push** even with every service set to `autoDeploy: false`. Change an
env var, a plan, a schedule or a start command in `render.yaml`, merge it, and
Render syncs it and redeploys the service it belongs to.

So the honest statement is: **config changes deploy themselves, code changes do
not.** Both are true at once. Anyone who simplifies it to "pushing does nothing
now" will eventually push a `render.yaml` change expecting nothing to happen.

Turning the Blueprint's `autoSync` off as well is a different and much larger
decision — it takes `render.yaml`'s authority over the infrastructure away. Do
not do it as a side effect of wanting manual deploys.

## Changing render.yaml

Validate before pushing, because the push is what applies it:

```bash
render blueprints validate render.yaml --output text --confirm
```

`need_payment_info` in the result is a **billing state, not a file defect** — it
means the workspace has no payment method for the paid resources the file
declares. Every other error is yours.

`totalActions` in the plan says how many resources this file would touch. Read
it. A change you believed was one field reporting eleven actions is the file
telling you something you did not know.

## Verify — this is the part that counts

One service:

```bash
render deploys list <serviceID> --output json --confirm | python3 -c "
import sys, json
d = json.load(sys.stdin)[0]['deploy']
print(d['status'], d['commit']['id'][:7] if d.get('commit') else '-', d['finishedAt'])
"
```

Every service at once, which is what a release needs — repeat until the count
reaches the number of services, because the cron deploys were fired without
`--wait`:

```bash
SHA=$(git rev-parse --short HEAD)
awk '{print $2, $3}' /tmp/svc.txt | while read -r id name; do
  curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services/$id/deploys?limit=1" | python3 -c "
import json, sys
d = json.load(sys.stdin)[0]; d = d.get('deploy', d)
print(f\"$name {d['status']} {(d.get('commit') or {}).get('id','-')[:7]}\")"
done
```

Then confirm the commit that is live is the commit you meant, and hit the site:

```bash
git rev-parse HEAD
curl -s -o /dev/null -w '%{http_code}\n' <production URL>/
```

**A `live` deploy of the wrong commit is a failed deploy.** So is a `live`
deploy that serves a 1 kB shell. Check both.

For a manual release, verify **every** service you deployed, not a sample. One
of eleven silently staying behind is the whole failure mode, and sampling is
exactly how it stays hidden.

## Reporting

Deploy status per service, the commit hash live on Render, the commit hash in
the repo, and the status code and byte count from the running site. All
observed, none inferred. If any service was skipped or failed, name it — a
release reported as done with one cron still on last week's image is worse than
one reported as failed.
