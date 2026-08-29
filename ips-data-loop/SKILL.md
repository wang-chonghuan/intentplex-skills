---
name: ips-data-loop
description: Load when an expensive, long-running job writes a derived dataset to a database — a classification pass, an enrichment run, a migration, a batch of model calls — and the result has to be trustworthy. Covers the loop that gets such a job right: declare invariants first, prove them against the store, run small before running long, and fix the code rather than the rows. Triggers include "ips-data-loop", "跑数据", "重跑一遍数据", "这批数据对不对", "怎么验证这次跑的结果", "改完代码要重跑吗". Do not load for reading or querying data that already exists, for schema design, or for ordinary application bugs unrelated to a batch write.
---

# ips-data-loop

A run that takes two hours and thirty dollars gets one honest verdict at the end:
the data is usable, or it is not. Everything in this skill exists to make that
verdict arrive early, cheaply, and truthfully.

The failure this guards against is not a crash. A crash is loud and free. The
failure is a run that **reports success and writes garbage** — because the check
was written to confirm what the program already believed.

## The loop

Five steps. The order is the whole point: most of the cost of getting this wrong
comes from doing step 3 before step 1.

1. **Declare the invariants.** Before writing the job, list what must be true of
   the data when it finishes. Not "it should look reasonable" — statements that
   are true or false about rows. Usually three to five, usually obvious in
   hindsight, usually never written down.

2. **Write them as assertions against the store.** Not against the program's
   variables. A `SELECT` that would fail if the invariant were violated. Give the
   assertion the power to say *do not publish this version*.

3. **Run small, for real.** Not a dry run, not a plan, not a type check — a real
   run over a small slice that exercises every write path, including the last
   one. Then look at the rows it produced.

4. **Run full.** Only after step 3 is clean.

5. **Fix the code, not the rows.** When the full run finds something, the repair
   goes where the next run will read it.

Then back to 1: what did this teach you that must now be true?

## Why invariants must come first

Written last, an assertion tends to encode what the program already thinks. It
passes, and it teaches nothing.

Written first, it is a description of the *result*, arrived at before you know
how the code will be structured — so it has no way to inherit the code's
assumptions. That independence is the whole value.

The practical test: **can this check fail?** If you cannot describe the rows that
would trip it, it is documentation, not a check.

## Ask the store, never the program

An assertion that reads the program's own memory verifies that the program is
consistent with itself. That is not what you need to know. Programs that are
perfectly self-consistent write bad rows all the time — because their picture of
the store has drifted from the store.

Ask the database. Every time. The categories of drift, all of them common:

- **Type.** The driver hands back something other than what the code's type
  annotation claims. Casts (`as number`, `cast(...)`, `# type: ignore`) do
  nothing at runtime; they only silence the checker.
- **Identity.** Two objects in memory turn out to be one row, because an upsert
  on a unique key quietly returned an existing id.
- **State.** Memory says a row is live; the store says it was retired three
  steps ago.
- **Constraints.** A foreign key or unique index the code never accounted for
  rejects a write — or, worse, would have if it existed.

A green type check says nothing about any of these. It validates the assertions
you wrote, against a database you were not consulting.

## Small runs, and the fake ones

A small run is worth it because the expensive failures live at the *end* of a
long job — after everything is computed and while it is being written. Those
paths are unreachable by anything cheaper than a real run.

The trap: a knob that shrinks a *parameter* is not a small run. Reducing the
number of clusters, or the sampling rate, or the concurrency, changes how the
same full workload is divided — the model calls, the writes, and the wall clock
all stay. What makes a run small is **fewer items**. If the job has no way to
process fewer items, add one before you need it.

Two habits that pay for themselves:

- **Late optional stages degrade, they do not kill.** Anything after the main
  write — cleanup, extra enrichment, tidying — belongs in a `try/catch` that logs
  and continues. A cosmetic step must never destroy a completed run's output.
- **Count downstream of the failure.** A counter placed before the step that can
  fail reports work that was never persisted. Count what landed, not what was
  attempted, and log the shape of the result — asked, succeeded, declined,
  failed — so an all-zero outcome announces itself.

## Fix the code, not the rows

Repairing the rows fixes today. The code runs every time.

A one-off repair script is legitimate — sometimes it is the only way to avoid
re-running an expensive job — but it is never the whole fix, and it should not be
written before the source fix. The rule that survives:

> **Fix the code first, then repair the existing rows in the same round.**

If you only have appetite for one of the two, do the code. Bad rows you know
about are a smaller problem than a generator you know is broken.

## Do not let your own threshold become the defect

Batch jobs accumulate numbers someone picked: a size cap, a similarity cutoff, a
retry count. When a report says "N items exceeded the threshold", the honest
first question is not how to fix them — it is **whether the threshold was ever
right**.

Measure the flagged population against an independent signal before acting. The
finding is often that the rule was wrong, and that enforcing it was doing damage:
splitting things that belonged together, discarding things that were fine. A
threshold you set is not evidence about the world.

## Reporting

The run's own summary is where "failure as completion" hides. Two rules:

- The summary reports what the **assertions** found, not what the code intended.
  If an invariant failed, the summary says so first and says the version must not
  be published.
- Any bound the job imposed on itself — a cap, a sample, a skipped retry — is
  logged explicitly. Silent truncation reads as full coverage.

State outcomes plainly afterward. If an invariant failed, say which and how many
rows. If a stage was skipped, say so. Never let a green log stand in for a
verified result.

## A worked example

`references/trovestep-108.md` traces one run of this loop in full: a
classification job over 29,000 records that took seven rounds to get right, what
each of the seven defects actually was, and which of them a first-round invariant
would have caught. Read it if you want the concrete shape of these failures;
skip it if you only need the method.
