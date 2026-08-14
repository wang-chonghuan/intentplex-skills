# Capability 2: Work the decision list

cap1 produced a report. This turns it into edits — the objectively fixable ones directly, everything
else only after the human has decided it.

The report usually arrives from an **earlier session**. Do not assume the conversation that produced
it is still in context; work from the report and from the files, and re-check anything you are about
to act on. A finding that was true last week may have been fixed since.

## Order

**机器可修 first, in one pass.** Wrong paths, dead references, stale names, false arithmetic,
contradictions with an obvious intended side, commands that do not run. They need no decisions, they
are cheap, and clearing them shortens the list the human has to read.

Then the **需人裁决** items, one at a time.

## The 需人裁决 items

Each is a trade-off the author owns. Put it to them as a choice, not as a problem:

> **N. `<the finding, one line>`**
> Now: `<what the skill does today>` — `<file>:<line>`
> Option A: `<change>` — costs `<what it costs>`
> Option B: `<change>` — costs `<what it costs>`
> My recommendation: `<one of them>`, because `<one sentence>`.

Three rules for this:

- **Always recommend.** "This needs your decision" with no position is the work handed back.
- **State the cost of your own recommendation.** A recommendation with no downside listed is a
  recommendation that has not been thought through, and the human cannot weigh it.
- **A repeat of the ask is a decision.** If the human hears the concern and says do it anyway, that
  settles it — implement it, do not re-argue it later in the run.

Batch related decisions. Several findings usually turn on one underlying choice; asking that choice
once, with all its consequences listed, beats five questions that are secretly the same question.

## The unadjudicable group

If cap1 surfaced conflicts nobody could settle, the human's answer to that single question is not
just a fix — **it is a principle the skill never had.** Write it into the skill as one, in the hub
where it will actually be read, then resolve each conflict against it.

This is the highest-value edit the whole audit produces: it stops the same class of conflict
recurring, which no individual fix does.

## While editing

- **Change what was decided and nothing else.** An audit hands you a licence to touch many files at
  once, and adjacent cleanup done under that licence is unreviewed change. Note what you noticed;
  do not fix it.
- **A rule gets one home.** When a fix restates something already stated elsewhere, replace the other
  copy with a pointer instead of leaving two. Duplication was probably on the list to begin with.
- **Verify the way lens 3 did.** A fixed path gets an `ls`; a fixed command gets run; a fixed
  arithmetic claim gets computed. Fixing a factual error by writing a different unverified claim is
  the one mistake this capability must not make.
- **Never edit a skill's target repositories.** If the skill ships `templates/` that were copied into
  projects, those copies now belong to those projects. Report the drift; do not chase it.

## Finish

Report per finding: **fixed**, **skipped** (with the human's reason), or **no change needed** (with
what showed it). Then say what is left open.

Do not re-run cap1 to confirm the fixes. Re-auditing what you just edited is the second verification
that this whole design refuses; the next audit happens when the skill has accreted again, not when it
has just been cleaned.
