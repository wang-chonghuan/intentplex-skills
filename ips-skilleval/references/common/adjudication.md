# Adjudication

**This is the product.** Four lens reports concatenated is not an audit — it is the raw material, and
handing it over moves the hard part back onto the human. Everything below happens in the orchestrating
agent, after the lenses return and before anything is shown.

Expect the raw pile to shrink by half or more. That is the step working, not work being lost.

## 1. Merge what is the same finding

The lenses overlap on purpose, so the same defect arrives up to three times wearing different
clothes: a contradiction lens calls it "two rules disagree", a gap lens calls it "no instruction for
this case", a self-betrayal lens calls it "a record nobody can write".

Merge on **the defect**, not the wording — same file and same underlying cause is the same finding.
Keep the **strongest evidence** from each report and note that N lenses found it independently.
Independent arrival is real signal about severity; do not throw it away by deduplicating silently.

## 2. Resolve the conflicts between lenses

**The lenses will contradict each other, and this is where an unadjudicated report does its damage.**
One says a command is broken; another ran it and it worked. One calls a rule redundant; another calls
its absence a gap.

Rules for settling it:

- **Whoever actually checked wins.** A lens that ran the command and pasted the output beats a lens
  that reasoned about the command, every time, regardless of which sounds more confident.
- **When neither checked, check it yourself.** These are cheap; do not arbitrate between two guesses.
- **When it is a judgment rather than a fact, it is not a conflict** — it is a trade-off, and it goes
  to the human in the decision list with both readings stated.

Report what you overturned. A rejected finding, named, is a useful part of the output: it stops the
next reader from rediscovering it, and it is evidence the adjudication happened.

## 3. Adversarially verify what survives

Every 阻断 and 会犯错 finding gets a **refuter**: a subagent whose only job is to kill it.

> Try to refute this claim about the skill at `[path]`: `[the finding, verbatim, with its quotes]`.
> Read the files. Run whatever read-only commands settle it. Look specifically for: a rule elsewhere
> that already handles this case; a deliberate refusal that makes it a choice rather than a defect; a
> misread quote; a scenario that cannot actually arise.
> **Default to `refuted: true` when you are not sure.** A finding that survives an honest attempt to
> kill it is worth reporting; one that merely was not disproved is not.

Refuted findings are dropped. Contested ones — where the refuter raises something real but not fatal —
are reported with the objection attached, so the human decides with both sides in front of them.

This step exists because **plausible-but-wrong findings are the most expensive kind**: they read as
authoritative and they cause real edits to correct code. An unverified audit trades a small amount of
recall for a large amount of that.

## 4. Classify — the thing the human actually needs

Every surviving finding is exactly one of:

**机器可修 Objectively fixable** — fixing it requires no knowledge of what the author values. A wrong
path, a dead reference, a stale name, a false arithmetic claim, a contradiction with an obvious
intended side, a command that does not run.

**需人裁决 Needs the author** — fixing it requires knowing what the author values. How much structure
is right, how much verification is enough, whether an artifact earns its keep, whether a rule should
have one home or three.

> **The rule: if the fix requires knowing what the author values, it is theirs to decide.**

This is the same boundary that decides whether a lens needed a purpose, and it is not a coincidence —
both are the line between what can be checked and what must be chosen.

For every 需人裁决 item, state **the options and your recommendation**. "This needs a decision" with
no recommendation is work handed back. Recommend, and make it easy to overrule.

## 5. The unadjudicable contradictions

Lens 1 returns these separately: places where two rules conflict and **nobody can say which is
intended**. They are not ordinary contradictions and must not be reported as such.

Together they answer a question the audit never asked directly: **where did the missing purpose
actually cost something?** Report them as one short group:

> These N conflicts cannot be settled from the skill alone. Each is a place where the skill had to
> know its own priorities and never wrote them down. Settling them is one decision, not N: `[state
> the axis they share — speed versus certainty, agent freedom versus human control, and so on]`.

Then ask the human that **one** question, with the conflicts as evidence. This is the only point in
the whole audit where the human is asked what the skill is for — and by now the question is concrete,
grounded in text they wrote, with two real options attached.

If there are none, say nothing. A skill with no unadjudicable conflicts did not need a stated purpose.

## 5b. Where the ips-telos verdict goes

The first ips-telos pass arrives here, and only here. Use it three ways:

- **As a tie-breaker on the trade-offs**, not on the facts. When a 需人裁决 item turns on "is this
  structure earning its keep", ips-telos has already judged that question against the artifact's
  purpose — cite it in the recommendation. Never let it overrule a lens on a matter of fact; it did
  not run the command.
- **As a cross-check on the unadjudicable group.** If it inferred a final cause and the conflicts all
  sit on one axis, its inference is a candidate answer to put to the human — offered as a candidate,
  clearly labelled as inferred, never presented as the skill's actual purpose.
- **As its own verdict section.** Whatever it says about the artifact's shape stays a verdict. Do not
  dissolve it into the defect list; a judgment about form is not a defect and reporting it as one
  gives it evidence it does not have.

If its findings duplicate a lens finding, keep the lens's — it has the quote and the failure scenario.

## 6. The report

```markdown
# ips-skilleval — <skill name>

## 结论
<Two or three sentences. Is it safe to depend on? What is the worst thing in it?>
<If the second ips-telos pass said restructure rather than patch, that goes here, first, and the
 defect list below becomes its supporting evidence.>

Usage facts assumed or supplied: <the three answers>.
Ran: <N> lenses, <N> raw findings, <N> after merge, <N> after refutation.

## 阻断 / 会犯错 / 磨损
<Ranked. Each in the evidence format, with 机器可修 | 需人裁决 marked, and a proposed fix.>

## 需要你定的
<The 需人裁决 items as a numbered decision list: options + recommendation, one line each.>

## 没有共识的规则冲突
<The unadjudicable group and the single question it implies. Omit if empty.>

## 形状判定（ips-telos）
<Its verdict on whether the artifact's form serves its purpose. Judgment, not evidence — labelled
 as such. Omit if the pass did not run.>

## 反向：检查不足的地方
<At most three. Omit if empty.>

## 被否决的发现
<What a lens claimed and why it did not survive. Short. Omit if empty.>
```

**Do not include a "minor" or "nitpick" section.** There is no tier below 磨损, and adding one is how
an audit smuggles back the padding this whole design exists to prevent.

If the audit found nothing above 磨损, say that plainly. **"Nothing worth reporting" is a valid and
valuable result** — and an audit incapable of returning it is an audit whose findings mean nothing.
