# Recovery Without Rebuying

## Start With The Durable State

Find the original run, request, task ID, raw response, charge, and active owner.
Do not reset a ledger, create a new budget, or discard successful siblings to make
the runner look clean.

Conceptually, a request progresses through:

```text
planned -> claimed -> submitted -> raw_saved -> modeled -> published
```

Map these phases onto existing tables and states. Do not add a table or enum for
every word. Publication often belongs to a dataset/run rather than each request.
Track submitted, raw-complete, modeled, and published separately: they are not
interchangeable counters.

| Persisted evidence | Next action |
|---|---|
| Never dispatched; no live owner | Claim through the normal runner |
| Provider accepted and returned task ID | Retrieve that task; do not POST again |
| Task still queued/not ready | Preserve submitted state and poll appropriately |
| Valid raw saved, parser/writer failed | Fix and replay raw without purchasing |
| Modeled facts exist, publication failed | Retry only affected publication |
| Response/save acknowledgment unclear | Reconcile provider task and storage first |
| Explicit success with empty result | Settle as empty, distinct from zero and failure |
| Explicit documented permanent unsupported result | Record unsupported with evidence |
| Repeated internal error/timeout | Remains a failure, not proof of unsupported |

An HTTP 200 or successful outer envelope can contain an inner task failure.
Likewise, a "not ready" response is a saved polling event, not a completed paid
result. Settle parent runs correctly when all children finish, including empty
children; a harmless empty result must not leave a parent running forever.

## Prevent Duplicate Effects, Not Just Duplicate Rows

Use the established database claim/unique identity and an owner or fencing token
where multiple processes can contend. A unique typed-row key does not stop two
processes from buying the same result.

Reclaim an expired lease only after distinguishing "not submitted" from "possibly
submitted." Reject stale-owner writes. A local lease cannot guarantee exactly-once
external billing without provider support; preserve uncertainty instead of
claiming such a guarantee.

If raw cannot be saved reliably or a charge becomes uncertain, pause **new paid
dispatch**, repair/reconcile, and continue safely retrieving accepted tasks where
their results can be durably preserved. Do not strand the whole queue.

## Bounded Recovery Means Bounded Decisions

Choose retries by provider semantics and evidence, not one global number:

- A transport error before submission differs from a lost submission reply.
- A confirmed zero-cost transient error may justify an authorized retry.
- An unknown charge must remain unresolved/reserved until reconciled.
- A paid successful task should be recovered through its original result or
  provider support, not purchased again because the amount seems trivial.

For a repeated failure class, examine a representative original failed request.
Test a minimal same-scope recovery on a small affected subset before applying it
to the rest. Preserve original parameters and any recovery override in the
request history. A different sort/filter/model can change the answer: do not call
it identical or reuse it under an unchanged specification silently.

Do not weaken limits, change endpoints, silently add paid retries, or mark
internal errors permanent to get a green status. Conversely, do not endlessly
investigate one failing target while all usable results remain unpublished.
Publish safe completed data where allowed and keep the gap explicit.

Fix recurring code defects in the canonical path, then replay saved work.
Prefer an existing targeted import/reconciliation mode over ad hoc SQL or a new
transfer service. Running an approved command on a local machine against the
explicit production connection is not the same as writing a local development
database; deployment/location restrictions still come from the actual project.

## Restart Or Handoff

Persist a compact checkpoint in the existing run/ticket record:

```text
run + manifest/spec; authoritative target; code revision
owner + process/job/task IDs; whether a process is still active
committed raw/modeled/published counts; remaining IDs or stored selector
actual/held/unknown costs; original approved cap
last concrete error; exact existing resume command; next acceptance condition
```

Exclude secrets and large raw payloads. Counts support the checkpoint; the ledger
remains authoritative. A new agent first checks the old process, then resumes.
Do not fork an active paid collector or repeatedly message an obsolete worker.

Old malformed records are not automatically this job's work. Repair, explicitly
authorized scoped deletion, or a documented nonblocking exception may be enough.
Never fabricate successful evidence, delete unresolved billing evidence, or
preserve an irrelevant anomaly as an endless release blocker.
