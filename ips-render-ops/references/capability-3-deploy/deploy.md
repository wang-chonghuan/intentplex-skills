# Capability 3: Deploy

Render deploys on push to the tracked branch when `autoDeploy: true`. So the
normal path is: merge, then **verify**. This capability is mostly the verify.

## When a manual trigger is needed

Only when there is no new commit — a rebuild after changing an environment
variable, or re-running a build that failed for an infrastructure reason.

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
render deploys create <serviceID> --output text --confirm
```

That streams build logs and blocks until the deploy finishes.

## Changing render.yaml

Validate before pushing. The push is what syncs the Blueprint:

```bash
render blueprints validate render.yaml --output text --confirm
```

`need_payment_info` in the result is a **billing state, not a file defect** — it
means the workspace has no payment method for the paid resources the file
declares. Every other error is yours.

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

## Reporting

Deploy status, the commit hash live on Render, the commit hash in the repo, and
the status code and byte count from the running site. Four facts, all observed.
