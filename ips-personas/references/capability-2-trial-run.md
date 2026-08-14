# Capability 2 — Trial run

Run one persona before committing to the whole panel, to check that **the spec is good enough** to produce good output. This is the gate's replacement: cheap sampling instead of a per-result rerun loop, which is what makes many-persona reviews slow.

## What the trial tests

It tests the **input**, not the skill. The run contract in cap 3 is fixed and correct; the trial asks whether *this spec* feeds it well enough. A weak trial means the spec needs work — never that the skill needs a gate.

## Steps

1. Choose the trial persona: **if §6 named one, use it.** Otherwise pick the persona **most likely to expose a problem** (the harshest temperament on the riskiest goal), or two of the most *different* personas — one persona under-samples, since different personas walk different paths.
2. Run it exactly as cap 3 would (`references/capability-3-run.md` — same run contract, same output shape). Trialing under a different contract than the real run would prove nothing.
3. Read the result against `references/quality-checklist.md`.

## Reading the result → it points at the spec

If the trial is weak, route the symptom to what to fix **in the spec** (the skill is the constant):

| Symptom | Spec fix |
|---|---|
| Vague, generic, not pinned to steps | §4 goal too abstract → make it a concrete outcome; check the temperament is a sharp one |
| Tunnel-visioned — only did the assigned task, missed friction | §4 goal is a feature/step, not an outcome → raise it to the end the user actually wants |
| Off-character | §5 temperament weak or mismatched → pick a sharper one, or sharpen the inline description |
| Thin / no evidence, "not experienced" | §1 target unreachable or underspecified → fix access or say where to go (this is environment, not the spec's content) |
| Only one facet covered across personas | §4 goals don't span → add the missing outcome-level needs |

Fix the spec, re-trial. Only when the trial is clean, proceed to the full run (cap 3).

## Rules

- The trial uses the identical run contract as cap 3 — no shortcuts, or it doesn't predict the real run.
- Diagnosis lands on the spec (or the environment), never on "add a gate." If the contract itself looks wrong, that's an authoring bug in this skill, outside this loop.
- Don't trial the easiest persona. Trial the one most likely to fail, so a clean trial actually means something.
