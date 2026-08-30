# Capability 6: Environment

See and change a service's configuration.

## The rule that governs everything here

**`render.yaml` is the source of truth.** A value changed in the dashboard
survives until the next Blueprint sync and then silently reverts. So:

- A setting that should persist → change it in `render.yaml`, push.
- A secret → declared in `render.yaml` as `sync: false`. Its value stays out
  of Git and lives in Render. A human may type it in the dashboard, or may
  explicitly authorize named keys to be synced from a Git-ignored local env
  file with the script below.
- A one-off experiment → dashboard is fine, but write it back or expect to lose it.

## Look at what a service actually has

Key names only. **Never print values** — they are secrets, and a printed secret
is in the transcript forever.

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
curl -s "https://api.render.com/v1/services/<serviceID>/env-vars?limit=50" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  | python3 -c "import sys,json;[print(' ', e['envVar']['key']) for e in json.load(sys.stdin)]"
```

## Adding a value

Without explicit authorization, supplier passwords, API keys and other
credentials remain human-entered values: state which key is missing and let the
human type it into the dashboard.

With explicit authorization for the target environment group and the exact key
names, use `scripts/sync_env_group.py`. It reads a Git-ignored env file without
sourcing it, updates only the named keys, and prints key names but never values.
It is a dry-run unless `--apply` is present:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
python3 <ips-render-ops>/scripts/sync_env_group.py \
  --env-group <env-group-id> \
  --env-file <main-checkout>/.env \
  --key FIRST_KEY \
  --key SECOND_KEY

# After the dry-run names exactly the intended keys:
python3 <ips-render-ops>/scripts/sync_env_group.py \
  --env-group <env-group-id> \
  --env-file <main-checkout>/.env \
  --key FIRST_KEY \
  --key SECOND_KEY \
  --apply
```

This authorization is narrow:

- The human must name or unambiguously approve the exact keys and target.
- The env file must be ignored by the Git repository that contains it.
- Never bulk-import every key from an env file.
- Never print request bodies, response bodies, values, or value lengths.
- A retry may repeat only the same named-key operation; adding other keys needs
  separate authorization.

Non-secret configuration (a batch size, a feature switch) belongs in
`render.yaml` with a literal `value`.

## Removing

Update semantics are usually a merge: not sending a key does not delete it. To
actually remove one, use the explicit delete — then read the key list back and
confirm it is gone. **A key you believed you removed is worse than one you never
added**, because the next person will not think to look for it.

## Every change here is a deploy

Changing an environment variable restarts the service. Treat it as a deploy: run
the post-deploy check (capability 3) afterwards.
