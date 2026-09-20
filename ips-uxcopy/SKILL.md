---
name: ips-uxcopy
description: Load when user-visible copy is being written, reviewed, or cleaned up — product pages, dashboards, empty states, tooltips, reports, emails — or when the user says "ips-uxcopy", "这文案像机器写的", "审一下文案", "clean up this copy", "why does this page read like filler". Use it to catch machine-written filler before it ships, and to write copy that does not need catching.
---

# ips-uxcopy

Use this skill on copy a real user will read. Two modes: **audit** an existing surface, or **author** new copy without producing the defects the audit looks for.

In audit mode this skill produces a report and suggested rewrites. Do not edit the target unless the user asks for fixes.

## Core Logic

Machine-written copy fails in a specific way: it is grammatical, well-organised, and says nothing the reader can use.

It happens because a model asked to fill a slot will always fill it. It describes the module instead of the object. It reports absence as if absence were content. It leaks the vocabulary of the system that produced it. It hedges every claim until nothing is claimed.

So the measure is not tone, grade level, or word count:

> **Every line must tell the reader something they did not know and can act on. A line that cannot is deleted, not improved.**

Three tests, in this order:

1. **Evidence.** Is there a fact behind this line? No fact, no line — and never a line announcing that the fact is missing.
2. **Conclusion.** Does it state something about *this* object, or does it describe the category the object belongs to?
3. **Deletion.** Remove the line. What does the reader lose? Nothing means it was never copy, only filler.

Absence is a layout decision, not a sentence. An empty section is removed, not narrated.

Do not let the smell catalog below replace these three tests. The catalog names what has already been seen; the tests catch what has not.

## Inputs

Required:

- The copy: a URL, file path, screenshot, pasted text, or the content brief for copy to be written.

Optional:

- Who reads it, and what they came to decide.
- The data actually available behind each line, including what is missing, sampled, or estimated.
- House voice, glossary, or an existing surface the user considers good.

When the copy depends on data, ask what is genuinely known before judging it. A line can only be called unsupported once it is clear no evidence stands behind it.

## Workflow

**Audit mode**

1. Read the surface as its reader, not as its author. Note what question the reader arrived with.
2. Apply the three tests to every line, block, and number.
3. Name the defect, quote the offending line, and give the replacement or mark it for deletion.
4. Judge the page as a whole: does it reach a conclusion anywhere, or only present material?
5. Report. Do not rewrite the surface unless asked.

**Author mode**

1. List what is actually known — with its source, sample size, and freshness.
2. Write the conclusion first: one plain sentence a reader could repeat to a colleague.
3. Add only the evidence that supports it.
4. Drop every block with no evidence behind it. Do not replace it with a note about the gap.
5. Run the three tests on your own draft before handing it over.

## The smells

Grouped by what they leak. Each is a defect on sight.

**System leaking into the page**

1. **Internal vocabulary.** Words from the schema, pipeline, or governance model printed for users: `saved`, `cohort`, `population`, `coverage`, `observed`, internal tier labels.
2. **Reporting absence.** "Not checked. No record found. No date available." Three sentences for one gap.
3. **Empty states with real estate.** A list of "not detected" rows. Missing data does not get a layout.
4. **Data-quality reporting.** Coverage ratios and QA counters that belong to the team's dashboard.

**Filler that survives review because it reads like prose**

5. **A teaching sentence above every block.** Explains what the module is for, says nothing about the object in it.
6. **Methodology in the body.** How the sample was built belongs in one footnote, once.
7. **Disclaimers that undercut the number beside them.** If it cannot be trusted, it should not be displayed.
8. **Unfalsifiable value claims.** "Reveals what supports growth and where the strategy is thin."
9. **Stacked abstract nouns.** "Monetisation coverage." "Competitive authority." No subject, no verb, no picture.
10. **Subjectless passives.** "No structured check has been recorded." By whom, of what?

**Shape that betrays the generator**

11. **Metrics with no conclusion.** A grid of numbers and not one sentence saying what they mean.
12. **Numbers with no baseline or sample.** A large figure drawn from 2% of the set, sitting in the same row as complete totals.
13. **Template parallelism.** The same "Shows how X, which Y, and how Z" frame repeated down the page.
14. **Stacked hedges.** Two qualifiers in one sentence until no claim survives.
15. **Headline with a twist.** "Not A, but B" constructions and withheld subjects. Name the subject and finish the sentence.

## Output

Audit mode uses this shape:

```markdown
# UX Copy Audit

## Verdict

- Status: Pass | Needs Improvement | Fail
- Target:
- Reader and their question:
- Worst pattern:

## Findings

1. Severity: Blocker | Major | Minor
   Smell:
   Quote:
   Why it fails:
   Replacement: <rewritten line, or DELETE>

## Page-level Judgment

<Does the page reach a conclusion? Where does the reader stall?>

## Recommended Changes
```

If there are no findings, write `No findings.` under `## Findings`.

Author mode returns the copy itself, plus one short list of what was dropped for lack of evidence, so the owner can decide whether to go get that evidence.

## Severity

- **Blocker**: the reader is misled, or leaves without the answer they came for. Includes numbers presented without the sample that would change their meaning.
- **Major**: the line survives but costs the reader time — filler, hedging, internal vocabulary, absence reported as content.
- **Minor**: wording and rhythm that would improve on a second pass.

## Rules

- Delete before rewriting. Most bad copy is not a wording problem.
- Never write a sentence whose subject is a gap in the data.
- One conclusion before any evidence; evidence before any methodology; methodology once, at the end.
- A number appears with its sample, its date, or its baseline — or it does not appear.
- Use the reader's words. If a term exists only inside the system, translate it or cut it.
- Say what is true plainly; do not soften a claim with hedges to make it survive review.
- Do not invent facts to fill a block. An empty block is the correct output when the evidence is missing.
- Keep the report direct: quote the line, name the defect, give the replacement.
