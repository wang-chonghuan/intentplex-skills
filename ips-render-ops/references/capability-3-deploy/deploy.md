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

One command. It asks the platform what exists, deploys every one of them, polls
until they agree, and **exits non-zero unless every service is live on the
target commit**:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
python3 <skill>/scripts/release.py                  # release git HEAD
python3 <skill>/scripts/release.py --dry-run        # show the targets, touch nothing
python3 <skill>/scripts/release.py --commit <sha>
python3 <skill>/scripts/release.py --only <substr>  # one service, or a subset
```

**Start with `--dry-run`.** It prints exactly which services a real run would
touch, and it is the cheapest way to notice that the workspace is not the one
you thought.

### Why a script and not a command to retype

Because the release is the one operation where the failure is silent. Ten
services update, one does not, and every observable signal says success. Nobody
verifies eleven services by hand every time; an exit code does it every time.

An earlier version of this file asked you to retype a loop. The first person to
follow it — the author — got it wrong in three separate ways on the first real
release. That is the argument.

### What it refuses to do

Each of these exits non-zero rather than proceeding:

- **The target commit is not the tracked branch head.** Services that cannot be
  pinned to a commit deploy their branch head, so pinning some services while
  others take a different head is not one release. Push first, or pick the
  commit that is actually the head.
- **No deployable services matched.** A release that targets nothing must not
  report success — that is how a wrong workspace or a typo'd `--only` looks.
- **`RENDER_API_KEY` is unset.**

### The Render behaviour it encodes, so you do not have to

All three were observed on a real release, and all three produce a *silent
partial release* when you get them wrong:

**1. Datastores appear in the services listing and have no `type` field.** A
Postgres entry deserializes as `{'environment', 'postgres', 'project'}`. Writing
`s['type']` raises `KeyError` **mid-iteration** — the loop does not fail loudly,
it emits some services, dies, and leaves a truncated list. The datastore can
sort ahead of the web service, so the one service you actually care about is the
one silently missing. The script treats *having a `type`* as the definition of
deployable, which is also why adding a background worker or a static site needs
no change here.

**2. Cron jobs reject a commit reference.** `POST /deploys` with `commitId`
answers `400 … cannot deploy cron job service … by commit reference ID`. The
script tries with the commit and retries without on exactly that rejection,
rather than carrying a list of which types can be pinned.

**3. `--wait` on a cron job can latch onto the wrong deploy and hang.** Observed:
`render deploys create <cron> --wait` printed `Waiting for deploy dep-XXXX…` for
over ten minutes while the API reported that service's newest deploy already
`live` — a different id. The script polls the API instead.

### Deploying by hand

If you need to do it without the script — one service, or the script is
unavailable — it is `render deploys create <serviceID> --commit <sha> --wait`
for a web service, and a plain `POST /v1/services/<id>/deploys` with `{}` for a
cron job. Then verify, below.

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
