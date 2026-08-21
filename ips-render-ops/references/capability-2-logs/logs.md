# Capability 2: Logs

Render collects stdout itself — no log platform to configure, no agent to
install. Retention is **7 days on Hobby**.

This is the capability that gets used most, because it is the only way to see
what a scheduled job actually did.

## Run

```bash
eval "$(grep '^export RENDER_API_KEY' ~/.zshrc)"

# The last 200 lines from one resource
render logs -r <resourceID> --limit 200 --output text --confirm

# Only the lines you care about — the way to read one structured event
render logs -r <resourceID> --text categorise.done --output text --confirm

# Follow
render logs -r <resourceID> --tail --output text --confirm

# A window, when you know when it ran
render logs -r <resourceID> --start 2026-08-21T05:00:00Z --end 2026-08-21T06:00:00Z \
  --output text --confirm
```

`-r` is **required** in non-interactive mode. It takes resource IDs, not names.

## Why `--text` matters here

A collector that prints one JSON object per line is designed to be filtered.
`--text <event-name>` pulls exactly the start or done event out of a run of
thousands of lines, which is how you answer "how many did it process" without
reading anything else.

## When there are no logs

Three causes, in the order worth checking:

1. **The run is older than retention.** 7 days on Hobby.
2. **The wrong resource ID.** A cron job and the web service are different
   resources; the job's output is on the job.
3. **The job never started.** Then there is nothing to read, and the question is
   why it did not fire — check that the service is not suspended (capability 1).

## Reporting

Quote the actual lines. A summary of a log is not evidence; the line is.
