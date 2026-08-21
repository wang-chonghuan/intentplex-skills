# Capability 6: Environment

See and change a service's configuration.

## The rule that governs everything here

**`render.yaml` is the source of truth.** A value changed in the dashboard
survives until the next Blueprint sync and then silently reverts. So:

- A setting that should persist → change it in `render.yaml`, push.
- A secret → declared in `render.yaml` as `sync: false`, typed into the
  dashboard once by a human. The file never learns the value.
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

**Never enter a credential on the human's behalf.** Supplier passwords, API
keys, payment details: state which key is missing and let them type it into the
dashboard. Non-secret configuration (a batch size, a feature switch) belongs in
`render.yaml` with a literal `value`.

## Removing

Update semantics are usually a merge: not sending a key does not delete it. To
actually remove one, use the explicit delete — then read the key list back and
confirm it is gone. **A key you believed you removed is worse than one you never
added**, because the next person will not think to look for it.

## Every change here is a deploy

Changing an environment variable restarts the service. Treat it as a deploy: run
the post-deploy check (capability 3) afterwards.
