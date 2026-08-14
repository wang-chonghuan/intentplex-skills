---
name: ips-skilleval
description: Load when the user wants an agent skill audited for defects that would make an agent do the wrong thing — contradictions between its own rules, gaps its flow does not cover, factually wrong commands or paths, and drift from what the skill says it stands for — or says "ips-skilleval", "审查这个 skill", "查一下这个技能有没有漏洞和矛盾", "evaluate this skill". Runs four independent lenses as parallel subagents, then adjudicates and adversarially verifies before reporting. Expensive; for a skill that has accreted many edits or is about to be depended on. Do not load to create or restructure a skill.
---

# ips-skilleval

Audit an agent skill the way a skill actually fails: not by reading it and having opinions, but by
running four independent lenses over everything it ships, then **adjudicating** what they found.

## Start here — what is being asked?

| The human wants… | Go to |
|---|---|
| a skill audited | **cap1** — `references/capability-1-review/review.md` |
| the findings from a finished audit acted on | **cap2** — `references/capability-2-apply/apply.md` |
| a skill created or restructured | **Nothing here.** Say so |
| "is this skill any good?", with no appetite for a full run | **Say what a run costs** (below), then let them choose |

A request that fits none of these gets asked about — do not map it onto the nearest capability.

## The one thing this skill exists to prevent

**Any agent asked to find fault in a skill will find fault forever.** Everything can be improved,
producing a finding is free, and the cost is paid by whoever reads the report. An audit that returns
sixty findings has not been thorough; it has moved the work of separating signal from noise onto the
human, which is the work it was supposed to do.

So the whole design makes findings **expensive to produce and cheap to kill**:

- **A finding must name a concrete failure** — "an agent following this does X wrong". No failure
  scenario, no finding. This one rule does most of the filtering.
- **Findings are adversarially verified** — survivors get a refuter whose only job is to kill them.
- **Quotas per lens**, with returning fewer stated as the better answer.
- **A named out-of-scope list**, so slots are not spent on wording and taste.
- **Author intent is exempt** — a skill that says "I deliberately do not do X" is not failing to do X.

All of it is in `references/common/finding-rules.md`. **Read that file before any lens runs.** A lens
briefed without it produces a style review.

## The four lenses

Independent, parallel, blind to each other. Diversity of failure mode, not four passes of the same
reading. Briefs to hand the subagents verbatim are in `references/common/lenses.md`.

1. **矛盾 Contradiction** — two rules that cannot both be obeyed.
2. **漏洞 Gap** — a situation the instructions do not cover, walked from the executing agent's seat.
3. **事实错误 Factual error** — claims that fail when checked. **This lens runs commands.** Its
   authority comes from having actually looked.
4. **背离宣言 Self-betrayal** — the skill judged against its own stated principles, quoted back at it.

**All four share one blind spot: they are internal-consistency machines.** They cannot tell you the
skill is the wrong shape — only that it disagrees with itself, misses a case, states something false,
or drifted. So **ips-telos runs twice alongside them**: once in parallel with the lenses, with its
output going to the adjudicator alone so it cannot contaminate them; once after the findings exist,
to answer the one question a defect list cannot — **patch these, or restructure?**

Only lens 4 needs to know what the skill is *for*. The other three are answerable from the artifact
and the world alone — which is why the audit does not begin by asking the human to state a purpose
they may never have had. See "The missing purpose" below.

## The missing purpose

Most skills never state what they are for. Inferring a purpose and then judging the skill against
your own inference is circular: it launders the reviewer's taste into "the standard", after which
every finding looks principled and none of them are.

So this skill does **not** open by asking "what is this for?" — asked cold, a human improvises an
answer describing the skill they wish they had written, which is less reliable than the artifact.

Instead:

- **Three lenses need no purpose at all.** Run them first.
- **Lens 4 runs only if the skill states principles of its own.** If it does not, it reports observed
  tension rather than violation, and says so. It never invents a standard to convict with.
- **Where the absence actually costs something, lens 1 finds it**: a contradiction nobody can
  adjudicate is exactly a place where the skill needed a purpose and never wrote one. That is a
  finding with evidence, not a blank the reviewer quietly filled in.

What the human *is* asked for, up front, is three **facts about use** — answerable, not
self-descriptive. `references/common/finding-rules.md` has them.

## Capabilities

1. **cap1 审查** — scope the artifact set, collect the usage facts, run the four lenses in parallel,
   adjudicate, report. **Produces a decision list, not a patch.**
2. **cap2 落地** — work the decision list: apply what is objectively fixable, put every trade-off to
   the human one at a time.

## What this costs, and when not to run it

A real run is four subagents over every file a skill ships, an ips-telos pass, and a refuter per serious
finding. The one measured case — 21 files, ~1700 lines — was about 390k subagent tokens for the lenses
alone. Treat that as one data point, not a rate, and say what you expect before starting.

**Do not run it** on a freshly written skill (it has not accreted anything yet), or after a small
edit. It earns its cost on a skill that has been **edited across many sessions** — where rules have
been added faster than old ones were removed — or on one you are **about to start depending on**.

**It must be able to audit itself.** Running ips-skilleval on ips-skilleval is its only honest acceptance
test; a finding it cannot survive is a finding it should not be reporting about others.

## Scope

Audits **skills** — it does not create or restructure them, and it never edits the target during
cap1. Skills have a known anatomy and this audit uses it: the hub is always loaded, `references/` is
loaded on demand, `scripts/` can be executed and checked against what the docs claim, and
**`templates/` escapes** — anything shipped there gets copied into other repositories, where it
becomes that project's own file and stops being reachable by fixing this skill. Weight template
findings accordingly.
