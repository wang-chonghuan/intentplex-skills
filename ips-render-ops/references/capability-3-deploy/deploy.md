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

render services --output json --confirm | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    s = s.get('service', s)
    if s['type'] in ('web_service', 'cron_job'): print(s['id'])
" | while read -r id; do
  render deploys create "$id" --commit "$SHA" --wait --output text --confirm || echo "FAIL $id"
done
```

Two flags carry the weight:

- **`--commit <sha>`** deploys that commit rather than whatever the branch head
  happens to be when the command reaches Render. Those differ the moment someone
  else merges while you are deploying, and "the branch head at the time" is not
  something you can report afterwards.
- **`--wait`** blocks and exits non-zero on failure. Without it the loop reports
  success for a deploy that has not finished building.

Deploying a **single** service — a rebuild after an env change, or re-running an
infrastructure failure — is the same command with one id and no loop.

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

```bash
render deploys list <serviceID> --output json --confirm | python3 -c "
import sys, json
d = json.load(sys.stdin)[0]['deploy']
print(d['status'], d['commit']['id'][:7] if d.get('commit') else '-', d['finishedAt'])
"
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
