# What counts as a finding

**Read this before briefing any lens, and give it to every lens verbatim.** Without it a lens returns
a style review — technically accurate, uniformly worthless, and long.

## The usage facts — collect these first

Three questions, asked of the human before anything runs. They are **facts about how the skill is
used**, not descriptions of what it is for. People answer facts reliably and improvise purposes.

1. **Who runs it?** The author themselves · someone else on the team · an unattended agent.
2. **How is it invoked?** Named explicitly ("use n-foo cap2") · loaded automatically from its
   description · called by another skill.
3. **What does a wrong run cost?** Wasted work only · a dirty repository · a write to an external
   system, money, or production data.

Each answer deletes whole categories of finding before they are written:

- Named explicitly → **anything about description triggering is out of scope.** The description is
  not doing routing work, so its precision is not load-bearing.
- Author-only → "a newcomer would not understand this" is not a finding.
- Wrong run costs only wasted work → "there is no confirmation before X" is not a finding.
- Unattended → every place needing a human present **is** a finding.

If the human will not answer, assume the most demanding case (someone else, auto-loaded, external
consequences) and **say in the report that you assumed it** — findings that rest on the assumption
are marked so they can be dismissed in one line.

## The test every finding must pass

> **An agent following this skill, in a situation that will really occur, does something wrong.
> Write that situation and that wrong thing.**

If you cannot write it, you do not have a finding — you have a preference. Delete it. This single
rule filters more noise than every other rule here combined.

Two corollaries:

- **The behaviour gate.** If fixing it changes only how the document reads, and not what an agent
  does, it is not reportable. The one exception is a **factual error**: a wrong path or a command
  that does not exist is reportable even when today's agent happens to route around it, because it
  is false and falsehoods spread.
- **The reality gate.** "In a situation that will really occur" is doing work. A failure that needs
  three unlikely things to line up is not a finding; say so and move on.

## Severity — by consequence, never by feeling

| Level | Meaning |
|---|---|
| **阻断 Blocking** | An agent following the skill produces a wrong result, or cannot proceed at all. |
| **会犯错 Will-err** | In a foreseeable situation the agent will probably do the wrong thing. |
| **磨损 Decay** | It works today, but the structure guarantees it stops being true — a rule with two homes that will diverge, a derived bound that is already wrong. |
| *below that* | **Not reported.** Not in an appendix, not in a "minor" section, not as a footnote. |

There is no "minor" tier on purpose. A minor tier is where an unbounded audit hides its padding, and
its existence invites every lens to fill it.

## Out of scope — do not spend a slot here

- Wording, tone, phrasing, "this could be clearer", "this reads awkwardly".
- Formatting, heading style, table-vs-list, ordering of sections for aesthetics.
- Missing examples, missing diagrams, missing README, missing changelog.
- Generic best practice the skill did not sign up for ("it should have tests", "it should log more").
- Features the skill does not have and never claimed to have.
- Hypothetical futures: "if this skill later supports X, then…".
- Anything the usage facts have already ruled irrelevant.

## Author intent is exempt

**A skill that deliberately refuses to do something is not failing to do it.** Before reporting an
absence, look for the refusal — skills state them as "no X", "we do not", "deliberately omitted",
"deleted because…". Quote it and drop the finding.

The finding is only alive if the refusal **contradicts something else the skill requires**, and then
it is a contradiction (lens 1), not a gap.

This rule exists because the most confident-sounding audit failure is flagging a deliberate design
choice as an oversight, at length, with reasoning.

## Quota

**At most 8 findings per lens**, and this is a ceiling, not a target.

> **Returning 3 findings is a better answer than padding to 8.** A lens that finds nothing says
> "nothing found" and stops. Nobody is graded on volume.

When a lens genuinely has more than 8, it reports the 8 worst and states how many it dropped and of
what kind — a silent truncation reads as "that was everything".

## Evidence format — every finding, no exceptions

```markdown
N. **<one sentence: the defect>**
   - Where: `<file>:<line>` — and the **verbatim quote**, not a paraphrase.
   - Also: `<file>:<line>` + quote, for the other side of a contradiction.
   - Failure: <the situation, and what the agent does wrong in it>.
   - Severity: 阻断 | 会犯错 | 磨损
   - Confidence: **CONFIRMED** (I quoted both sides / ran the command / read the file) or
     **PLAUSIBLE** (it follows from reading, but I did not verify it)
```

A finding with no verbatim quote is not admissible — reviewers reliably misremember what a document
said, and a paraphrase is where that error hides. Mark `PLAUSIBLE` honestly; the adjudicator treats
CONFIDENCE as a routing signal, and a false CONFIRMED poisons the whole report.

## The reverse check

An audit that only subtracts will strip a skill of the safety it needs. So **lens 4 ends with at most
three** findings of the opposite kind: **where is this skill dangerously under-specified** — a place
where one missing instruction lets a real failure through silently.

Three is a ceiling and this section is not required to be filled. It is a counterweight, not a wish
list; the same evidence rules and the same failure-scenario test apply.
