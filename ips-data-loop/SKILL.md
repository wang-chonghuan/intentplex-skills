---
name: ips-data-loop
description: Load when work means running an expensive job over a corpus — crawling, enriching, classifying, clustering, extracting, batch model calls — and the output has no right answer to check against, only a better or worse one. Covers iterating such a job to quality: version every run, trial-run then full-run, read the output, change the method, compare versions, and know when to stop. Triggers include "ips-data-loop", "跑数据", "重跑一遍", "这批数据质量怎么样", "怎么迭代这个方法", "结果不太对，改改再跑", "试跑一下看看". Do not load for deterministic work where correctness is decidable by a test, for querying data that already exists, or for schema design.
---

# ips-data-loop

## What kind of problem this is

Two kinds of job write data, and they need opposite disciplines.

**Deterministic.** There is a right answer. Did the migration move every row? Did
the parser handle the escape sequence? You write a test, the test passes, you are
done. Iteration ends.

**Optimization.** There is no right answer, only a better one. Is this taxonomy
good? Is this summary faithful? Did the crawler find the right pages? No test can
tell you, because the thing you want is not a property of any single row — it is
a judgement about the whole output, and it is partly aesthetic.

This skill is for the second kind. Its method is not "make it correct"; it is
**make each version better than the last, cheaply enough that you can afford many
versions, and honestly enough that you can tell which way you moved.**

The mistake that costs the most is treating an optimization problem as a
deterministic one: writing the job, running it once, checking it does not crash,
and shipping. The output will be plausible and mediocre, and nothing will tell
you so.

## Two loops, nested

The inner loop is about **correctness**: does the run produce structurally sound
data? It is cheap, mechanical, and must close before the outer loop means
anything — you cannot judge the quality of output you cannot trust.

The outer loop is about **method**: is this the right way to do the job? It is
expensive, slow, and driven by judgement. It is where the value is.

Do not spend the outer loop's money on inner-loop failures. A full run that dies
on a null pointer taught you nothing about your method.

---

# The inner loop — earning the right to judge

## Declare invariants before writing code

List what must be true of the output when the job finishes. Three to five
statements, true or false about rows, not "it should look reasonable".

Write them **first**. An assertion written afterwards tends to encode what the
program already believes, so it passes and teaches nothing. Written before the
code exists, it cannot inherit the code's assumptions — that independence is the
entire value.

The test of a real check: **can it fail?** If you cannot describe the rows that
would trip it, it is documentation.

## Ask the store, never the program

An assertion that reads the program's own variables proves the program is
consistent with itself. Programs that are perfectly self-consistent write bad
rows constantly, because their picture of the store has drifted from the store.

Query the database. The drift is always one of four kinds:

- **Type** — the driver returns something other than the annotation claims. Casts
  do nothing at runtime; they only silence the checker.
- **Identity** — two objects in memory turn out to be one row, because an upsert
  on a unique key returned an existing id.
- **State** — memory says live, the store says retired.
- **Constraints** — a foreign key or unique index the code never accounted for.

Give the failing assertion the power to say **do not publish this version**.

## Two habits that keep runs alive

- **Late optional stages degrade, never kill.** Anything after the main write —
  cleanup, extra enrichment, tidying — goes in a `try/catch` that logs and
  continues. A cosmetic step must not destroy a completed run's output.
- **Count downstream of the failure.** A counter placed before the step that can
  fail reports work that never landed. Log the shape of the result — attempted,
  succeeded, declined, failed — so an all-zero outcome announces itself.

## Fix the code, not the rows

A one-off repair script fixes today. The code runs every time.

Repair scripts are legitimate — sometimes the only way to avoid re-running an
expensive job — but never alone and never first. **Fix the source, then repair
the existing rows in the same round.** If there is appetite for only one, do the
source: bad rows you know about are a smaller problem than a generator you know
is broken.

---

# The outer loop — iterating the method

## Version every run; never overwrite

Every run writes under a new version, and old versions stay. This single decision
is what makes iteration possible: without it you cannot compare, cannot roll
back, and cannot tell whether a change helped.

Three parts:

- A **version column** on every derived table, and a **run table** holding each
  run's parameters, statistics, and status.
- Exactly one version marked **active** — what the product reads. Publishing is a
  separate, deliberate act from producing.
- Parameters recorded **with** the output, not in someone's shell history. A
  version whose settings are unknown cannot be reasoned about.

## Separate the expensive-and-stable from the cheap-and-volatile

The highest-leverage architectural decision in this kind of work: find the part
that is expensive but rarely needs to change, and give it **its own table and its
own lifecycle**, so the part you are actually iterating can be re-run cheaply.

Typical split: extraction and embedding are expensive and stable; grouping,
scoring and labelling are cheap and volatile. Done right, iterating the volatile
half costs a fraction of the whole job, and you can afford ten versions instead
of two.

Get this wrong and every idea costs a full re-run, so you stop having ideas.

## Trial run, then full run — they answer different questions

**A trial run answers: does the machinery work?** A small slice, run for real,
through every write path including the last one. Cheap enough to do many times.

**A full run answers: is the output any good?** Quality is a property of scale.
Structures that need density do not appear in a slice — a grouping step gated on
"at least N members" simply never fires on small input, so the trial run tells
you nothing about the thing you most want to see.

Never confuse a shrunken *parameter* for a small run. Reducing cluster count,
sampling rate, or concurrency changes how the same full workload is divided; the
model calls, the writes and the wall clock all stay. **What makes a run small is
fewer items.** If the job cannot process fewer items, add that switch before you
need it.

Expect to temporarily loosen scale-gated thresholds so a trial exercises a stage
that would otherwise never trigger — as a flag, not an edit.

## Read the output, not the log

The log tells you the job ran. It cannot tell you the output is good. Every
version, look at actual rows:

- **The extremes.** The biggest groups, the smallest, the emptiest, the outliers.
  Defects concentrate at the ends.
- **A random sample**, not a curated one.
- **The new thing.** Whatever this version changed — look at exactly that,
  directly.

This step is not automatable and is where nearly every real improvement starts.

## Show samples to the human early

The best moment in the loop is putting a concrete sample in front of the person
whose judgement defines "good" — before spending on a full run.

They will tell you things no metric would: that a structure you thought marginal
is commercially valuable and should be kept even when it looks trivial; that a
defect you ranked first is not a defect at all. Both of those reversals are worth
more than a week of tuning, and both arrive within minutes of showing real
output.

So: trial run → show samples → decide → full run. Not: full run → hope.

## Change one thing per version

Two changes in one version means you cannot attribute the difference. When two
changes are entangled, decide which one you are testing and hold the other fixed,
even if it means one more run.

Log what changed, in words, in the run's parameters or the ticket. Six versions
later nobody remembers why v5 existed.

## Compare versions on measures that survive the change

Pick a few numbers that stand for quality — coverage, size distribution,
self-reported purity, human-rated samples — and record them for every version.

Then guard against the trap: **a proxy is only valid relative to a structure.**
Change the structure and the proxy may quietly start measuring something else. A
metric that meant "duplicate categories" can become meaningless once categories
are grouped by similarity, because then the thing it detects is expected rather
than wrong. When the method changes, re-derive whether the measure still measures
what its name says. Otherwise you will report "no improvement" about a number
that stopped being about improvement.

## Do not optimize a threshold you invented

Batch jobs accumulate numbers someone picked: a size cap, a similarity cutoff, a
minimum count. When a report says "N items exceeded the threshold", the honest
first question is not how to fix them — it is **whether the threshold was ever
right**.

Measure the flagged population against an independent signal. The finding is
often that the rule was wrong and enforcing it was doing damage: splitting things
that belonged together, discarding things that were fine. Worse, an invented rule
tends to be load-bearing — other defects turn out to be its downstream
consequences, and removing it fixes them for free.

A threshold you set is not evidence about the world — it is a number someone
picked, and it has probably never been checked.

So when someone challenges one, **go and measure it instead of explaining why it
is right**. You can almost always construct a defence; that is the problem. One
measurement of a rule you believe in is worth more than several more runs, because
more runs only refine the work under a rule that may be wrong, while measuring can
show the rule itself is the defect. Challenges from whoever knows the domain
deserve this treatment first.

## Separate "the structure is wrong" from "the structure is coarse"

A common confusion that produces bad method changes: conflating *this grouping is
internally mixed* (a quality defect — split it) with *this level is too wide to
browse* (a navigation problem — group it). They feel similar and have opposite
remedies. Fixing the second with the first's tool damages real data by inventing
boundaries that do not exist.

When a fix requires reassigning items, ask whether the problem was ever about the
items. Adding a layer of organisation over unchanged data is almost always safer
than re-cutting the data.

## Know when to stop

Optimization has no natural end; the loop will keep offering improvements
forever. Stop when the marginal gain stops mattering to the purpose the data
serves — not when the numbers stop moving.

Signs it is time to stop: the remaining defects are aesthetic; the next
improvement costs more than the value it adds; the person paying says "good
enough". Write the remaining ideas down as future work and stop. An unshipped
perfect version is worth less than a shipped good one.

## Report honestly

- The summary reports what the **assertions** found, not what the code intended.
- Any bound the job imposed on itself — a cap, a sample, a skipped retry — is
  logged explicitly. Silent truncation reads as full coverage.
- When a version is worse, say so and say which measure says it. A loop that only
  ever reports progress is not measuring.

---

## A worked example

`references/trovestep-108.md` traces four method versions and seven defects
through one classification job over 29,000 records: what each version changed and
why, the measurement that overturned the author's own design, the moment a sample
shown to a human redirected the whole approach, and which defects a first-round
invariant would have caught. Read it for the concrete shape; skip it if you only
need the method.
