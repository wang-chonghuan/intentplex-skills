# Capability 5: Database

Connect to the managed Postgres, measure it, and check it — without writing.

## Connect

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
render psql <postgresID>          # opens psql against the database
```

For scripted checks, use the connection string from the dashboard (or the one
already in `.env` locally) with plain `psql`. Note that Render Postgres requires
SSL from outside its own network.

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

## Writing

Read-only is the default posture. A schema change belongs in a numbered
migration applied by the project's own migration job, not typed into psql — a
statement run by hand exists in no file and will not be applied to the next
database anyone creates.

## Reporting

Numbers, and what they were compared against.
