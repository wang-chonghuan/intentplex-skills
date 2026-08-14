---
name: ips-telos
description: Load when the user asks to review, audit, judge, or stress-test an artifact by its final cause, asks whether an artifact achieves its purpose, or explicitly says "Final-Cause Adversarial Review" / "telos" / "ips-telos".
---

# ips-telos

Use this skill to review an artifact by its final cause: the purpose that gives its form meaning. The target may be a skill, capability, gate, spec, plan, design, document, ticket, prompt, workflow, implementation handoff, or other agent-created artifact.

This skill produces a review report. Do not modify the target artifact unless the user explicitly asks for fixes.

## Core Logic

## Final-Cause Adversarial Review

The secret of adversarial agent review is to ask first: what was this artifact created to achieve?

This is its final cause: the purpose that gives its form meaning.

Judge everything against that purpose. Does the artifact’s current form help the purpose become real, or does it introduce drift, ambiguity, misunderstanding, miscalibrated degrees of freedom, missing design, or overdesign?

Do not enter the semantic forest too early. A single question aimed at the final cause can be stronger than a long list of surface rules.

The final cause is the measure. Everything else must justify itself before it. Prefer the simplest design that fully serves the purpose: KISS is a bias, not an excuse to leave necessary design undone.

## Inputs

Required:

- Target artifact: a file path, pasted text, named skill/capability/gate, issue artifact, or other concrete object to review.

Optional:

- Stated final cause, if the user already knows the artifact's intended purpose.
- Source-of-truth context such as requirements, user request, spec, plan, design constraints, examples, or downstream consumer expectations.
- Specific concern to test, such as drift, ambiguity, excessive freedom, missing evidence, or weak gates.

If the target artifact is missing, ask for it. If the final cause is not supplied, infer it from the artifact, surrounding files, user request, and available source-of-truth context. Ask the user only when the final cause cannot be inferred without materially changing the review.

## Workflow

1. Identify the target artifact and the source-of-truth context needed to judge it.
2. State the inferred or supplied final cause in one concise sentence.
3. Review the artifact first against that final cause before applying any surface checklist.
4. Identify whether the artifact's current form helps the purpose become real or creates drift, ambiguity, misunderstanding, miscalibrated degrees of freedom, missing design, or overdesign.
5. Check only the mechanical details that matter to the final cause, such as required sections, file paths, data fields, commands, gates, or output shape.
6. Produce the report. Do not rewrite the artifact unless explicitly asked.

When the artifact is large, read only the parts needed to judge the final cause. When the artifact feeds a downstream workflow, review from the downstream user's or agent's point of view.
When judging design size, look both ways: an artifact can fail because it omits necessary structure, or because it adds artifacts, steps, abstractions, options, or gates that do not earn their keep.

## Output

Use this shape:

```markdown
# Final-Cause Adversarial Review

## Verdict

- Status: Pass | Needs Improvement | Fail
- Target:
- Final Cause:
- Needs Change: Yes | No

## Findings

1. Severity: Blocker | Major | Minor
   Finding:
   Why it matters:
   Suggested change:

## Fitness Summary

## Drift Risks

## Design Fit

## Recommended Changes
```

If there are no findings, write `No findings.` under `## Findings`.

## Severity

- Blocker: the artifact can be followed or used and still miss its final cause.
- Major: the artifact probably works but leaves avoidable ambiguity, weak boundaries, too much freedom, missing design, or unnecessary complexity.
- Minor: wording, structure, or mechanical improvements that do not threaten the final cause.

## Rules

- Preserve the supplied core logic exactly.
- Do not let a long checklist replace final-cause judgment.
- Do not judge style, wording, or format unless it affects the final cause.
- Do not invent requirements outside the artifact's purpose and source-of-truth context.
- Prefer simple designs, but do not reward simplicity that fails to support the artifact's actual purpose.
- Keep the report direct and actionable.
