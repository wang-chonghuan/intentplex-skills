# Capability 8: Provision

Creating a project's resources for the first time, headlessly. Everything here
was learned by doing it and failing; each section is a trap that costs half an
hour if you meet it cold.

## Blueprint instances cannot be created from the API

```
POST /v1/blueprints        ->  405
render blueprints --help   ->  only `validate`
```

`render.yaml` can be **written and validated** headlessly, but turning it into
live resources — "New Blueprint Instance" — is a Dashboard action. An agent has
two honest choices:

1. Ask the human for that one click, and get Blueprint-managed infrastructure.
2. Create the resources through `POST /v1/services` and `POST /v1/postgres`,
   which works headlessly but leaves them **not** Blueprint-managed.

Pick deliberately and say which one you picked. Do not write "render.yaml is the
source of truth" into a project's documentation if you created the resources by
API — that sentence would be false the moment it was written.

## `validate` reports billing state as an error

```
"error": "need_payment_info"
```

One per paid resource. **This is not a defect in the file** — the workspace has
no payment method. Count the error *types* before reading them as YAML problems:
if every error is `need_payment_info`, the Blueprint itself is fine.

## A private repo fails until GitHub is connected

```
POST /v1/services -> 400
"passed in repository URL is invalid or unfetchable"
```

The message says "invalid URL" and means "I cannot see this repository." Check
visibility before believing the wording:

```bash
gh repo view <owner>/<repo> --json visibility -q .visibility
```

A private repo needs the Render GitHub app authorized for it, which is an OAuth
grant only the human can give. There is no API around it.

## Creating Postgres

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
curl -s -X POST https://api.render.com/v1/postgres \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
  -d '{"name":"...","ownerId":"tea-...","plan":"basic_256mb","region":"frankfurt",
       "version":"16","databaseName":"...","databaseUser":"...","environmentId":"evm-..."}'
```

Plan identifiers use **underscores** in the API (`basic_256mb`) and **hyphens**
in `render.yaml` (`basic-256mb`). Same plan, two spellings.

`databaseName`, `databaseUser`, `region` and the major version are **immutable**.
Changing one later means a new database and a data migration.

**The free plan expires after 30 days and takes the database with it.** It is for
experiments, never for anything meant to survive.

## Finding the environment to create into

Resources land loose in the workspace unless given an `environmentId`:

```bash
curl -s "https://api.render.com/v1/projects?limit=20" -H "Authorization: Bearer $RENDER_API_KEY" \
  | python3 -c "import sys,json;[print(r['project']['id'], r['project']['name']) for r in json.load(sys.stdin)]"
curl -s "https://api.render.com/v1/environments?projectId=prj-…" -H "Authorization: Bearer $RENDER_API_KEY"
```
