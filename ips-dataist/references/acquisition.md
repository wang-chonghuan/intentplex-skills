# Acquisition

## Freeze The Purchase, Not The Whole Product

Use an existing manifest/run record to identify the approved subjects and
datasets. Include the membership/taxonomy snapshot when selection depends on it.
Request identity must include every field that changes the purchased answer:
endpoint/spec version, target, geography/language, time window, limits, filters,
sort order, and prompt/model where applicable.

Do not regenerate a changing Top list inside a purchase loop. Freeze the
authorized population, finish it, and report later membership drift separately.
When a change invalidates the meaning or authorization of the purchase, reconcile
the affected targets before spending more; do not silently expand the manifest.

Inventory coverage separately by dataset and specification:

- Reusable successful result, including a confirmed successful empty result.
- Missing or explicitly due for refresh.
- Saved raw awaiting modeling, or a submitted task awaiting retrieval.
- Failed, unsupported, unknown specification, or uncertain charge.

Being a Top product does not prove any advanced dataset was collected. One
dataset's timestamp does not establish another dataset's freshness. Retired
members' old data is not evidence that the new members are covered.

Respect an explicitly approved fresh replacement run. Do not force an elaborate
reuse analysis when the user has chosen replacement, but reconcile in-flight
requests and prior charges so replacement does not accidentally buy twice.

## Choose Data By Its Decision Value

Identify the user decision each dataset supports before pricing it. Distinguish
cheap population-wide summaries from deeper samples; do not buy the same metric
again through a more expensive endpoint.

Preserve useful fields already included in an approved response even when they
are not modeled yet. That does not authorize additional endpoints, paid options,
pagination, models, geographies, or website crawling.

Verify current provider limits and prices at execution time. Forecast with the
actual request shape: per-task charges, row limits, empty-result charges,
asynchronous retrieval costs, and approved contingency. Do not copy a historical
ticket's price or invent a second account-balance system. A provider balance is
not the job's remaining spending authority.

Keep incurred and uncertain charges under the same cumulative budget. Use exact
decimal or integer units for arithmetic. Record actual over-quote charges
truthfully; stop additional spending when authority is exhausted.

## Raw First, Independently Durable

The recoverable unit is the supplier response, not an agent's log message.
Use the existing raw store or add the smallest missing durable store.

Preserve:

- Request ID, task ID, endpoint/spec, exact submitted parameters and targets.
- Response/task status, timestamps, effective period, cost, and payload checksum.
- The complete approved result payload, including presently unmodeled fields.

Never persist credentials or authorization headers. Store large bodies in a
bounded, suitable representation; do not truncate paid results to satisfy a
convenient column. If necessary, use exact response text/bytes or durable object
storage with an integrity-checked reference. Structured JSON can be derived.
Invalid text encoding or database JSON restrictions must not destroy the only
copy of a purchased answer.

Commit raw separately **before** modeling/publication. A rollback in either
downstream phase must leave the recoverable source intact. Record persistence
acknowledgment, not just that the HTTP response arrived in memory.

Do not hold a database transaction open while waiting for the provider. For
async services, persist the accepted task ID immediately. Submit, retrieve,
model, and publish should be resumable modes of the same runner, not unrelated
repair programs.

## Throughput Is An End-To-End Measurement

Preflight the frozen set once with set-based queries. Keep per-item checks local
to that item's claim and inputs. Do not reload the whole manifest, recount the
corpus, fetch all quotes, or rebuild an aggregate inside every iteration.

Use provider batching only within its documented limits. Measure one realistic
batch through HTTP, raw commit, and typed writes before choosing concurrency.
Network concurrency, write concurrency, and transaction batch size are distinct.
A task labeled "GET-only" can still do expensive database writes afterward.

Use backpressure: a slow raw sink throttles dispatch. Reduce write batch size or
concurrency when observed memory/connection pressure warrants it. Never increase
both blindly on the assumption that network calls are the bottleneck.

For async queues, use the existing ready-task listing or bounded retrieval
mechanism. Do not wait for every newly submitted task to finish before submitting
the next unless required by dependencies or rate limits. Do not replace a healthy
running dispatcher mid-flight for a speculative speedup.

## Two Small Checks, Not A Review Bureaucracy

Before spending or writing, ask: could this exact operation spend outside its
authority, hit the wrong target, or lose an already purchased result?

Confirm the target, scope, and durable response path in the initial preflight.
Inspect the first representative persisted result. Repair a real failure at that
boundary; do not repeat unchanged preflight or acceptance checks for every batch.

Dynamic safety is not a one-time check: the runner must atomically enforce the
remaining cumulative budget/reservations and current ownership for every
chargeable action, and fence stale owners at commit. Keep these checks scoped
to the request; do not replace them with repeated account-wide or corpus scans.

Estimate remaining work using measured throughput and queued/unfinished counts.
Separate dispatch, provider waiting, retrieval, modeling, and publication time;
provide a range. Do not guess "AI development takes N hours" from ticket size.
