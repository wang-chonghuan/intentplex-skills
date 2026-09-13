# Observed Lessons

These are historical examples from TroveStep work through September 13, 2026.
They explain decisions, not current population sizes, API prices, platform
limits, or universal project requirements. Reverify operational facts at use.
Original evidence lives in the named project's ticket records and execution
logs; those files are not required to use this skill.

| Observation | Transferable lesson |
|---|---|
| 185 found new Top membership, older data owners, unknown specifications, and dataset-specific gaps mixed together. | Membership, dataset coverage, freshness, and successful emptiness need separate accounting. A label is not a collection receipt. |
| 191/204 expanded into retrieval, semantic review, persistence, historical repair, and many closure dependencies. A later compact catalog-based approach simplified ordinary matching. | Test the simplest adequate semantic path first. Do not assume a catalog with hundreds of labels needs embeddings and several judges; keep historical cleanup separate from ordinary admission. |
| 212 replaced roughly one expensive population scan per market with one grouped calculation. | Look inside helpers called from loops. A small output can hide work proportional to the entire corpus multiplied by every row. |
| 215 obtained useful population-wide fields from bulk endpoints, but a large observation write caused database memory pressure. Smaller commits allowed continuation. | Provider batch size and database commit size need not match. Measure persistence, not only HTTP speed. |
| 215 retained one paid Domain Rank failure without a recoverable response, rather than pretending success or silently buying again. | Billing settlement and data completeness differ. A known charge does not prove a usable result; disclose the gap and respect repurchase authority. |
| 217 froze new Top members against a specified metric operation. Statistics maintenance alone did not repair an unbounded page query. | Bind samples to evidence snapshots. Fix query shape when statistics are not the actual bottleneck. |
| 224's first cleanup encountered an unindexed foreign-key dependency. A later full read-model rebuild failed, although replacement acquisition would rebuild those models anyway. | Check deletion dependencies and separate required cleanup from redundant publication. Do not pay the same recomputation cost twice. |
| 219's handoff was explicitly code-only; 226 owned acquisition and live delivery. | State the finish boundary. Build/PR success is not evidence that a single paid row has arrived. |
| 226 initially confused queued responses with failures and had independent parsing/persistence recovery work. | Save provider task identity and complete raw independently. Poll/replay the same work instead of resetting requests. |
| Two paid responses in 226 were recovered from the supplier and imported without another purchase. | A missing local response is a recovery problem first, even when rebuying would cost only cents. |
| Retrieval concurrency was raised to 24, but the runner also wrote to a small shared database; public pages failed. Serial continuation completed the backlog quickly. | Optimize the measured bottleneck. "Read-only supplier call" does not mean read-only execution. The concurrency values are observations, not defaults. |
| A publication guard rejected a cache changing to newer authoritative standard metrics. The transaction rolled back even though the new values matched their authority. | Preserve invariant facts, not stale cache bytes. Verify a mismatch's meaning before treating it as regression. |
| After a successful full publication, the final product added 50 external links. Another full refresh timed out on unchanged keyword data. | Publish the affected dependency closure through the existing publisher; do not rebuild unrelated datasets to release a tiny delta. |
| A ten-minute statement limit aborted a progressing maintenance query. The scoped final run was allowed to finish with observation and completed successfully. | Forecast overruns are not correctness failures. Distinguish Web deadlines from maintenance policy; fix cancellation policy before repeating useful work. |
| One target repeatedly returned a zero-cost internal error, then succeeded after a recorded bounded request adjustment. | Retry exhaustion is not proof of permanent unsupported status. Keep recovery scope honest and preserve each actual request specification. |
| Final delivery required all 12,823 requests, raw persistence, typed facts, publication, and nine active services on one revision. Two old paid cron jobs remained intentionally suspended. | End-to-end completion is a set of concrete consumer outcomes, not "every service exists" or "the process exited." Do not reactivate retired purchasing to satisfy a cosmetic service count. |
| Supervision risked prolonging the job through repeated checks, small-tail perfection, and successive direction changes. | The monitor must also converge. Correct a demonstrated fault once, preserve the worker's progress, and stop monitoring when the user's outcome is met. |

## Do Not Turn An Incident Into A Platform

A useful lesson removes a recurring failure with the smallest sufficient change.
It does not imply every project needs a new ledger, vector store, versioned copy
of every table, shadow billing system, all-service deployment, or permanent
supervisor. Existing components and the current authorization remain the default.

## Recognize These False Finish Lines

- "The request was submitted" while its result is still in the provider queue.
- "Raw row count increased" while every new row is a not-ready polling reply.
- "The parser works" while purchased responses are still only in memory.
- "The data is modeled" while the required public view is stale.
- "All pages return 200" while they show the old snapshot.
- "The Goal ended" while an unaccounted failed target was relabeled or omitted.

Recognize the opposite failure too: all material outcomes are already verified,
but the agent invents another audit, export, refactor, or optimization before
closing. That is unfinished coordination, not higher data quality.
