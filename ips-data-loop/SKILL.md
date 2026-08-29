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
**make each version better than the last, keep each version cheap enough that
you can afford to run many, and measure honestly enough that you can tell whether
the latest one is actually better or just different.**

The mistake that costs the most is treating an optimization problem as a
deterministic one: writing the job, running it once, checking it does not crash,
and shipping. The output will be plausible and mediocre, and nothing will tell
you so.

## Two loops, nested

The inner loop is about **correctness**: does the run produce structurally sound
data? It is cheap and mechanical, and it has to be working before the outer loop is
worth anything: if you cannot trust that the rows are sound, you have no way to
tell whether the output is good.

The outer loop is about **method**: is this the right way to do the job? It is
expensive, slow, and driven by judgement. It is where the value is.

Do not spend the outer loop's money on inner-loop failures. A full run that dies
on a null pointer taught you nothing about your method.

---

# The inner loop — making the data trustworthy enough to judge

## Declare invariants before writing code

List what must be true of the output when the job finishes. Three to five
statements, true or false about rows, not "it should look reasonable".

Write them **first**. If you write the check after the code, you will
unconsciously write a check the code already passes — you look at what the program
does and describe that, so it goes green and tells you nothing. Write it before
the code exists and it cannot copy the code's assumptions, because there are no
assumptions to copy yet. That is the whole reason the order matters.

To tell whether a check is real, ask: **could this ever fail?** If you cannot
describe the specific bad rows that would make it fail, it is not testing
anything — it is a comment that happens to be written in SQL.

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

- **A nice-to-have step at the end must not be able to kill the run.** Anything
  that happens after the main write — cleanup, extra enrichment, tidying up — goes
  in a `try/catch` that logs the error and carries on. Otherwise a tidying step
  that throws will destroy two hours of finished work that was already computed.
- **Put your counters after the step that can fail, not before it.** If you count
  work as you hand it off, you are counting attempts, not results — the log will
  say "39 assigned" while the database has zero. Log every outcome separately:
  attempted, succeeded, declined, failed. Then a run that produced nothing says so
  out loud instead of looking healthy.

## Fix the code, not the rows

A one-off repair script fixes today. The code runs every time.

Repair scripts are legitimate — sometimes the only way to avoid re-running an
expensive job — but never alone and never first. **Fix the source, then repair
the existing rows in the same round.** If you only have time for one of the two, fix the
source: rows you know are wrong are a smaller problem than a program you know
will produce wrong rows again.

---

# The outer loop — iterating the method

## Version every run; never overwrite

Every run writes under a new version, and old versions stay. This single decision
is what makes iteration possible: without it you cannot compare, cannot roll
back, and cannot tell whether a change helped.

Three parts:

- A **version column** on every derived table, and a **run table** holding each
  run's parameters, statistics, and status.
- Exactly one version marked **active** — the one the product actually reads.
  Producing a version and putting it live are two separate decisions, and the
  second one should take a deliberate action.
- The settings recorded **next to** the output, not left in someone's shell
  history. If you cannot see what settings produced a version, you cannot say why
  it differs from the last one, and comparing them is guesswork.

## Separate the expensive-and-stable from the cheap-and-volatile

This is the design decision that pays off most in this kind of work. Find the
step that costs a lot but rarely needs changing, and give it **its own table and
its own version**, separate from everything downstream. Then the part you are
actually still changing can be re-run on its own, without paying for the expensive
step again.

Typical split: extraction and embedding are expensive and stable; grouping,
scoring and labelling are cheap and volatile. Done right, iterating the volatile
half costs a fraction of the whole job, and you can afford ten versions instead
of two.

Get this wrong and every idea costs a full re-run, so you stop having ideas.

## Trial run, then full run — they answer different questions

**A trial run answers: does the machinery work?** A small slice, run for real,
through every write path including the last one. Cheap enough to do many times.

**A full run answers: is the output any good?** You can only see that at full
size. Some parts of the output only exist when there is enough data to form them —
a step that only groups things when it has at least N of them will simply never
run on a small slice. So the trial run can pass while telling you nothing at all
about the part you most wanted to look at.

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

- **The extremes.** The biggest groups, the smallest, the empty ones, the odd
  ones. Whatever is broken usually shows up at the top or the bottom of a sorted
  list, not in the middle.
- **A random sample**, not a curated one.
- **The new thing.** Whatever this version changed — look at exactly that,
  directly.

No script can do this part for you, and it is where nearly every real improvement
starts.

## Show samples to the human early

The best moment in the loop is putting a concrete sample in front of the person
whose judgement defines "good" — before spending on a full run.

They will tell you things no number could: that something you were about to drop
as unimportant is actually worth a lot to the business and should be kept even
when it looks trivial; that the problem you ranked as most serious is not a
problem at all. Either of those reversals saves more than a week of tuning, and
both usually arrive within minutes of showing them real output.

So the order is: trial run, show samples, decide, then full run. Not: full run,
and hope it turned out well.

## Change one thing per version

If a version contains two changes and the result is better, you do not know which
change did it — or whether one helped and the other hurt. When two changes seem to
depend on each other, pick the one you are actually testing and leave the other
alone, even if that costs an extra run.

Write down what changed, in plain words, in the run's settings or the ticket. Six
versions later nobody will remember why v5 existed, including you.

## Check that your quality measures still mean what they used to

Pick a few numbers that stand for quality — coverage, size distribution,
self-reported purity, human-rated samples — and record them for every version.

Here is the trap. **A stand-in number only means what you think it means as long
as the structure stays the same.** Change the method and the same number can
quietly start measuring something entirely different, while keeping its old name.

A real case: a count of "items that also belong to a neighbouring category" was a
good way to spot categories that had been wrongly split in two. Then the method
changed so that similar categories were deliberately grouped together — and from
that point on, an item belonging to a neighbour was *expected*, not a sign of
anything wrong. The number barely moved, and reporting it as "no improvement"
would have been meaningless, because it had stopped being about improvement.

So whenever the method changes, work out again whether each measure still measures
what its name claims, before you read anything into its value.

## Do not optimize a threshold you invented

Batch jobs accumulate numbers someone picked: a size cap, a similarity cutoff, a
minimum count. When a report says "N items exceeded the threshold", the honest
first question is not how to fix them — it is **whether the threshold was ever
right**.

Take the items the rule flagged and measure them against something the rule had
no part in deciding. Often what you find is that the rule itself was wrong, and
enforcing it was doing damage — breaking apart things that belonged together, or
throwing away things that were fine.

And it is usually worse than that: a made-up rule tends to have other things
resting on it. Bugs you were treating as separate turn out to be consequences of
that rule, so deleting it fixes them too, at no cost.

A threshold you set is not evidence about the world — it is a number someone
picked, and it has probably never been checked.

So when someone challenges one, **go and measure it instead of explaining why it
is right**. You can almost always construct a defence; that is the problem. One
measurement of a rule you believe in is worth more than several more runs, because
more runs only refine the work under a rule that may be wrong, while measuring can
show the rule itself is the defect. Challenges from whoever knows the domain
deserve this treatment first.

## "This group is a mess" and "this level is too crowded" are different problems

These two feel alike and get confused constantly, and the fixes are opposite:

- **This group has unrelated things in it.** That is a quality problem. The fix is
  to split the group.
- **This level has too many groups to browse.** That is a navigation problem. The
  fix is to add a layer above them, leaving every group intact.

Using the first fix on the second problem is how you end up carving real
categories in half along boundaries you invented, because they were never
genuinely two things.

So when a fix involves moving items around, stop and ask whether the problem was
ever about the items at all. Putting a layer of organisation on top of unchanged
data is almost always safer than re-cutting the data itself.

## Know when to stop

This kind of work has no finish line — there will always be one more thing that
could be better. Stop when the next improvement no longer makes any difference to
what the data is actually for. Not when the numbers stop moving; they never
entirely stop.

You are done when the problems that remain are cosmetic, when the next fix costs
more than it is worth, or when the person paying for it says it is good enough.
Write the leftover ideas down as future work and stop. A good version that people
are using beats a perfect one that is still being polished.

## Report honestly

- The end-of-run summary reports what the **checks actually found**, not what the
  code was trying to do.
- If the job limited itself in any way — took only the top N, sampled, gave up
  after one retry — say so in the log. If you leave it out, the run looks like it
  covered everything.
- When a version comes out worse, say so, and say which measure shows it. If every
  round you report is an improvement, you are not really measuring.

---

## A worked example

`references/trovestep-108.md` traces four method versions and seven defects
through one classification job over 29,000 records: what each version changed and
why, the measurement that overturned the author's own design, the moment a sample
shown to a human redirected the whole approach, and which defects a first-round
invariant would have caught. Read it for the concrete shape; skip it if you only
need the method.
