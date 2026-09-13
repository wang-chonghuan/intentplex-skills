---
name: ips-dataist
description: Load when the user wants to execute, recover, supervise, or finish a substantial data acquisition, ETL, backfill, classification, or analytical publication job; asks to collect a corpus into the authoritative database, resume paid requests without rebuying, or keep a data agent on track. Use for operational delivery across collection, modeling, computation, and publication. Do not load for a simple SQL question, one-off chart, or a purely conceptual data discussion.
---

# ips-dataist

Deliver the approved data into the system where it will actually be used, without
losing purchased results, spending twice, destabilizing the database, or turning
the last few records into another project.

Optimize for **useful, persisted progress per unit of time and money**, not the
number of checks, documents, retries, or agent turns. Correctness protects that
outcome; ceremony does not.

## Start At The Existing Checkpoint

Read the user's latest instructions, the project's entry instructions, the live
ticket when one exists, and its latest execution record. Identify:

- The approved population, datasets, observation periods, and completion scope.
- The authoritative database/schema and the actual runtime connection target.
- The remaining spending authority, including costs already incurred.
- The existing runner, writer, request ledger, saved raw, and publication path.
- The current owner, active process/job, deployed code, and first unfinished stage.

Resolve these from existing evidence before asking. Ask only for a consequential
missing decision. A skill invocation does not authorize purchases, destructive
cleanup, production writes, deployment, or a new Goal.

**Take the shortest path from the durable checkpoint to the requested result.**
Do not restart planning, classification, procurement, or acceptance because the
agent, branch, session name, or context window changed.

## One Workflow

```text
Freeze scope -> Acquire and preserve raw -> Model -> Publish -> Close
                    ^                       |
                    +-- recover only what is missing
```

1. **Prepare once.** Reconcile current coverage and request identity; inspect
   only the prerequisites for the next consequential action. Put a concise run
   contract in the existing ticket/run record, not a parallel documentation tree.
2. **Prove the risky boundary once.** Use the smallest representative authorized
   slice that exercises response persistence, parsing, and writing. Keep that
   slice as part of the real run. Reuse unchanged passing evidence.
3. **Collect durably.** Commit raw before downstream work can fail. Cheap
   incremental parsing may follow; defer expensive whole-corpus computation
   until acquisition is complete.
4. **Recover in place.** Use the original request/task IDs, budget, and saved
   results. Fix a blocking defect through the existing path, then resume only
   unfinished work.
5. **Publish the affected data.** Use the existing dependency graph and writer.
   Preserve unrelated facts and the last committed usable publication.
6. **Finish once.** Check the requested outcome against persisted facts and its
   actual consumer. Complete the authorized deployment/ticket/Goal steps; do
   not start another optimization pass.

Code-only delivery, investigation, and production execution are different scopes.
Do not silently turn one into another, or call code completion data completion.

## Always-On Decisions

- **SSOT is authority, not one physical table.** Raw is source evidence; typed
  facts and read models are derived. Give each fact one authoritative definition,
  writer, and current-selection rule. History is not a second current truth.
- **Preserve expensive work before improving its shape.** A parser, model,
  aggregate, or page failure must not require buying the response again.
- **Keep the machinery proportional.** Reuse the current runner and ledger.
  Add a table, state, index, or flag only for a demonstrated requirement. Do not
  introduce a universal orchestration, approval, or billing platform.
- **Separate semantics from mechanics.** Use the host LLM for meaning,
  classification, and synthesis; use deterministic code for identity, schemas,
  exact comparisons, money, state transitions, and API transport.
- **Forecasts are not kill switches.** A task exceeding its ETA is not itself
  stalled. Budget caps remain hard; time estimates do not become arbitrary
  database cancellation thresholds.
- **Observe the bottleneck before intervening.** More concurrency can slow a
  shared database down or crash it. Repeated full validation can cost more than
  the work being validated.
- **Protect the core, release the rest.** Missing paid raw, duplicate-charge
  risk, incorrect facts, and a broken required consumer are material. Optional
  polish and unrelated historical anomalies are not automatic closure gates.
  Record genuine exceptions; do not relabel failures as success.

## Read Only What This Stage Needs

| Situation | Reference |
|---|---|
| New acquisition, coverage, pricing, batching, or raw design | [Acquisition](references/acquisition.md) |
| Interrupted calls, billing uncertainty, parser failure, or restart | [Recovery](references/recovery.md) |
| Taxonomy, sampling, ETL, cleanup, aggregates, or slow publication | [Compute And Publish](references/compute-and-publish.md) |
| Long-running Goal, handoff, monitoring, intervention, or closure | [Supervision And Closure](references/supervision.md) |
| Why these rules exist; recognizing a repeated failure | [Observed Lessons](references/observed-lessons.md) |

Use the project's existing ticket and deployment workflows for those operations.
Use `ips-data-loop`, when available, for an explicitly requested semantic-quality
experiment, not as an automatic outer loop around deterministic collection.
Do not import its full versioning/experimentation machinery into an ordinary ETL
run. Use platform documentation for current provider and database behavior;
historical examples in this skill are not current API specifications.

## Minimal Handoff

Report the target system, completed/remaining scope, raw and modeled coverage,
actual cost and unresolved charges, publication/deployment state, and any real
exception. Include the exact existing resume entry only when work remains.

If the requested outcome is satisfied, close the work. If the user changes what
counts as sufficient, update the same execution contract and supervising task
once. Do not keep enforcing a superseded requirement from an old prompt.
