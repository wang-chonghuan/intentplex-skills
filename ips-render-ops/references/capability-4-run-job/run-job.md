# Capability 4: Run a Job Now

Fire a cron job off its schedule — after a fix, to backfill, or to prove a
change took effect.

## Trigger

There is an API for this, and it is not the one you would guess from the service
endpoints — a cron job has a `crn-…` id but lives under `/v1/cron-jobs`, not
under `/v1/services`:

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"
curl -s -X POST "https://api.render.com/v1/cron-jobs/<crn-id>/runs" \
  -H "Authorization: Bearer $RENDER_API_KEY" -H "Content-Type: application/json" -d '{}'
# -> {"id":"crn-…-1787351330","status":"pending","triggeredBy":"…"}
```

`POST /v1/services/<crn-id>/jobs` looks like it should work and returns
`400 startCommand is a required field` — that endpoint is for one-off jobs on a
service, not for firing a cron.

The Dashboard's **Trigger Run** button does the same thing.

**If a run is already active, triggering cancels it and starts a new one.** So
check the job is idle first (capability 2 — look for its done event) unless
cancelling is what you want.

## Then watch the effect, not the status

This is the trap that makes this a capability rather than a button.

A job that exits 0 having done nothing looks exactly like a job that worked.
A collector that skips already-processed rows will exit 0 in about a second on a
second run — correct behaviour, and indistinguishable from a broken credential
if you only read the exit status.

So pick an observation that could only be true if the work happened:

| The job | What actually proves it ran |
|---|---|
| writes rows | the row count moved, measured before and after |
| skips already-done work | the count did **not** move, and the log says how many it skipped |
| calls a paid supplier | the cost field in its own done event |
| calls a model | a field that could not exist without a reply |

```bash
# before
psql "$DATABASE_URL" -At -c "SELECT count(*) FROM <table> WHERE <the condition the job changes>"
# trigger, wait, then the same query again
```

**Never prove a job by re-reading the thing it was supposed to write, when that
thing was already there before the run.** Measure the delta.

## When there is nothing for it to do

A job with an empty backlog cannot prove anything. Either accept that and say so
plainly, or create work the job's own supported flags allow — most collectors
have a redo switch. **Do not manufacture a backlog by editing production data.**

## Reporting

The observation, both sides of it: the number before and the number after.
