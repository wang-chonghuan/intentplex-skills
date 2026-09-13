# Compute And Publish

## One Meaning For Each Fact

Record the source, effective period, units, geography, method/spec version, and
collection time. A retrieval timestamp is not the month a metric describes.
Do not turn a monthly estimate into a daily observation or fill missing history
with today's value.

If two endpoints return a similarly named field, designate its business
authority by meaning, not arrival order. Preserve both raw responses where
purchased, but do not expose two competing current metrics.

Keep these dimensions separate:

- Entity identity and eligibility.
- Taxonomy membership.
- Selected sample/Top membership.
- Dataset coverage, freshness, and collection status.

Zero, missing, failed, empty, unsupported, and "outside this sample" are different.
Do not infer missing status from an internal zero sentinel or infer an AI
recommendation/ranking from absence in a few sampled answers.

## Use The LLM Where Meaning Is The Work

For mapping an item into a manageable taxonomy, first try a compact full catalog:
stable IDs, names/slugs, and tree structure, plus a concise product description.
Measure actual prompt size and representative behavior. Hundreds of categories
are not, by themselves, a reason to build a vector-retrieval system.

Use definitions/examples to resolve ambiguous boundaries, or retrieval when the
catalog genuinely does not fit or measured quality/latency improves. Do not omit
needed semantics merely to reduce tokens. Do not require full definitions for
every obvious match, nor add a second LLM judge to every item by default.

Validate returned IDs and output shape deterministically. Prefer an existing
market when the buyer's task genuinely matches; insufficient evidence is pending,
not permission to invent a market. New markets need novelty/boundary evidence and
deduplication. Do not force genuinely different products into old categories,
target a historic category count, or merge whole groups without item-level
evidence.

Start with a small representative set including obvious, neighboring, novel,
and insufficient-evidence cases. Record evidence-backed reference judgments and
the fit-for-purpose acceptance rule before scaling; judge buyer-task meaning,
not just schema validity, old assignments, or the model's self-confidence.
Use the task's existing quality bar and review authority, not an invented large
benchmark or additional approval round.

Keep accepted unchanged results; do not rerun semantic evaluations just because
code persistence changed. Expand evaluation only for observed risk. A requested
quality experiment may use `ips-data-loop`; ordinary execution must still converge.

## Sampling And Analysis

Define eligibility, ranking metric/period, tie-breaks, and activation once. Use
the simplest sample answering the user's question; do not invent median,
percentile, or special "sixth member" machinery without a measured benefit.
Top-N is not a representative estimate of the entire market.

Freeze membership for downstream procurement. After taxonomy or metric repair,
invalidate/recompute the affected selection before buying against it. Do not
rerank continuously during a purchase run or infer that underfilled markets have
exactly N credible players.

Market growth needs comparable periods and populations; report actual coverage,
overlap, and concentration. Name time windows correctly. A newly tracked product
is not necessarily newly launched. A daily insight publication does not make
monthly source metrics daily or guarantee a new signal every day.

For AI/search evidence preserve prompts, engines/models, geography, collection
time, returned answers/results, and citations. Few samples are snapshots, not a
stable share-of-market rank. Absence in a truncated response is not a negative
fact about the whole market.

## Keep Heavy Work Out Of The Item Loop

Select and validate batches with set operations. Avoid a full eligibility view,
taxonomy scan, or corpus aggregate once per product or category. A harmless
helper called N times can hide the real N-by-corpus cost.

Reuse prepared catalog/materials per run when semantically valid. Update only
affected subjects after a local change. Do not rebuild every materialized view,
recalculate all history, or export/synchronize the entire database after each
batch.

Use constraints/indexes and fresh query-plan evidence where relevant. For mass
deletion, inspect referencing foreign keys and their indexes before blaming the
number of deleted rows. A targeted statistics refresh may help a demonstrated
planner problem; it is not a substitute for fixing an unbounded query.

## Publication Is A Dependency Operation

Map canonical facts to projections and actual consumers. Use the smallest
dependency closure that makes the changed data visible. If a full publication
already succeeded and one product later gains external-link data, unrelated
keyword views should not be rebuilt merely because a generic helper defaults
to "all."

Reuse one publisher with explicit scope when needed. Do not create a separate
publication framework. Audit helper side effects: a convenient general refresh
may also retire overlays or overwrite unrelated current facts.

Keep purchased raw outside the publication transaction. Choose an existing
atomic transaction, concurrent refresh, or build-and-switch pattern according
to dependencies, database capacity, and availability requirements. None is a
universal default. A committed prior publication remains the baseline when a
later attempt rolls back.

Compare against the correct invariant. Refreshing an old cache from authoritative
facts is supposed to change it. Do not require its old digest to remain equal.
Instead preserve unrelated source facts and verify the rebuilt affected values
against their authority. Explain a mismatch before changing a guard; do not
remove a valid correctness check merely to pass.

## Timeouts And Resource Pressure

Web latency limits, lock-acquisition limits, provider request limits, and batch
maintenance duration are different policies. Do not apply a short Web timeout to
a long analytical refresh or treat an ETA as a correctness invariant.

Give approved maintenance sufficient time. With reliable existing observation
and cancellation, a job-specific unset statement timeout can be appropriate;
otherwise use a generous operational limit. Do not disable every timeout
globally. Align client/job timeouts too: losing the client does not prove the
server-side transaction stopped.

Observe phase changes, committed outputs, locks/waits, resource pressure, and
available database progress evidence. A running process or CPU usage alone is
not proof of progress; elapsed time alone is not proof of a stall.
Do not cancel useful work because a forecast expired. Intervene on a concrete
fault, persistent blocked dependency, resource danger, or user instruction.
If a statement has actually failed and aborted its transaction, roll it back;
do not try to commit partial corrupt state to avoid the word "rollback."

## Cleanup And Compatibility

Destructive cleanup needs exact authorized IDs/cutoff and preserved identities,
billing evidence, and unrelated facts. Use the existing migration/writer path.
Do not delete history merely because SSOT was requested.

If an approved replacement will immediately rebuild the read models, an agreed
maintenance window may defer their refresh until replacement. Mark old
projections stale and exclude them from purchase/coverage decisions; do not
silently serve stale data as fresh or invent this downtime permission.

Resolve the application's actual logical database, not the resource's convenient
default connection. Confirm required migrations and old/new code compatibility.
Do not apply every pending migration or upgrade services as a side effect of
running one data job.
