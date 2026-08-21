# Capability 7: Rollback

Go back to the last deploy that worked.

## When

**Under pressure, roll back — do not fix forward.** The previous image is
immutable and one click away; a fix is a build, a deploy and an unknown. Get the
site serving, then diagnose.

## How

Render Dashboard → the service → **Deploys** → the last successful deploy →
**Rollback**. Hobby retains the most recent 5 builds.

To find which deploy to pick:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
render deploys list <serviceID> --output json --confirm | python3 -c "
import sys, json
for d in json.load(sys.stdin)[:8]:
    x = d['deploy']
    print(x['status'], (x.get('commit') or {}).get('id','-')[:7], x.get('finishedAt'))
"
```

Pick the newest `live` entry **before** the bad one.

## What a rollback does not undo

This is the part worth knowing before you rely on it.

- **Database migrations.** The image goes back; the schema does not. If the bad
  deploy applied a migration, rolling back leaves old code against a new schema.
  Check whether one ran before assuming a rollback is safe.
- **Data a collector wrote.** Jobs write to a shared database. Rolling the image
  back does not remove rows.
- **Environment variables.** They belong to the service, not the deploy.

If a migration ran, a rollback may not be the recovery — say so rather than
performing one and reporting the site as restored.

## After

Run the post-deploy check (capability 3) against the rolled-back deploy. Then
report which commit is live, and that it is deliberately not the newest one.
