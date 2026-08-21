# Capability 5: Database

Connect to the managed Postgres, measure it, and check it — without writing.

## Before anything: external access is closed by default

A newly created Render Postgres refuses every connection from outside Render's
own network, and the refusal looks like this:

```
psql: error: connection to server at "dpg-….frankfurt-postgres.render.com",
port 5432 failed: SSL connection has been closed unexpectedly
```

**That message is about the IP allow list, not about TLS.** It will send you
chasing `sslmode`, client versions and URL encoding for as long as you believe
it. The tell is that TCP connects — `nc -z <host> 5432` succeeds — and the
session then dies during the handshake.

Check it. `null` means **closed**, not open:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
curl -s "https://api.render.com/v1/postgres/<id>" -H "Authorization: Bearer $RENDER_API_KEY" \
  | python3 -c "import sys,json;print(json.load(sys.stdin).get('ipAllowList'))"
```

**Do not try to learn which IP to allow by asking the database.**
`inet_client_addr()` returns Render's internal proxy address — a `10.x` address —
never your public one. And a home or mobile connection's public IP rotates: a
`/32` pinned from `api.ipify.org` works once and fails an hour later from a
different address, with the same misleading SSL message.

So for a bounded task such as a data migration, open it wide, do the work, close
it again:

```bash
# open — say in the description that it is temporary, so a later reader knows
curl -s -X PATCH "https://api.render.com/v1/postgres/<id>" \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
  -d '{"ipAllowList":[{"cidrBlock":"0.0.0.0/0","description":"TEMPORARY: migration window"}]}'

# … work …

# close: an empty list denies all external access
curl -s -X PATCH "https://api.render.com/v1/postgres/<id>" \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" \
  -d '{"ipAllowList":[]}'
```

Changes take a minute or two. Poll until a query succeeds rather than sleeping a
fixed amount.

**Closed is the correct end state for an application.** Services on Render reach
the database over the private network using the *internal* connection string;
nothing in production needs the external hostname at all.

## Connect

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
render psql <postgresID>          # interactive; needs a real terminal
```

For scripted work, fetch the credentials and keep them out of stdout:

```bash
curl -s "https://api.render.com/v1/postgres/<id>/connection-info" \
  -H "Authorization: Bearer $RENDER_API_KEY" -o /tmp/ci.json
```

**Never print that response.** It carries `password`, and a `psqlCommand` that
embeds `PGPASSWORD=<value>` in the clear — a redaction that only handles the
`://user:pass@host` form will miss it and put the password in your transcript.
Parse it into environment variables instead, and print only lengths if you need
to prove it parsed.

## The checks worth having ready

```bash
# Size, biggest tables first
psql "$DATABASE_URL" -At -F$'\t' -c "
SELECT relname, pg_size_pretty(pg_total_relation_size(c.oid))
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = current_schema() AND c.relkind = 'r'
 ORDER BY pg_total_relation_size(c.oid) DESC LIMIT 10"

# Row counts per table — the check after any data migration
psql "$DATABASE_URL" -At -F$'\t' -c "
SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC"

# Connections in use against the plan's limit
psql "$DATABASE_URL" -At -c "SELECT count(*) FROM pg_stat_activity"
```

`n_live_tup` is an estimate maintained by the statistics collector. **After a
restore it can be stale or zero until `ANALYZE` runs.** For a migration check,
count for real:

```bash
psql "$DATABASE_URL" -At -c "SELECT count(*) FROM <table>"
```

## Moving data in

```bash
pg_dump "$SOURCE_URL" --schema='<schema>' --no-owner --no-privileges -Fc -f /tmp/db.dump
. /tmp/pgenv.sh
pg_restore --no-owner --no-privileges --clean --if-exists \
  -d "$PGDATABASE" -h "$PGHOST" -U "$PGUSER" /tmp/db.dump
```

A PostgreSQL 18 `pg_dump` writing for a PostgreSQL 16 server emits
`SET transaction_timeout = 0`, which 16 rejects:

```
pg_restore: error: could not execute query: ERROR: unrecognized configuration
parameter "transaction_timeout"
```

**Harmless** — one statement, no data involved. `errors ignored on restore: 1`
with that as the only error is a clean restore.

Then verify with real counts, on both sides, table by table:

```sql
SELECT 'tbl_a', count(*) FROM tbl_a UNION ALL SELECT 'tbl_b', count(*) FROM tbl_b ORDER BY 1;
```

**Do not verify with `n_live_tup`.** It is an estimate kept by the statistics
collector, and on a freshly restored database it reads stale or zero until
`ANALYZE` has run — it will tell you a perfect restore lost everything.

## Writing

Read-only is the default posture. A schema change belongs in a numbered
migration applied by the project's own migration job, not typed into psql — a
statement run by hand exists in no file and will not be applied to the next
database anyone creates.

## Reporting

Numbers, and what they were compared against.
