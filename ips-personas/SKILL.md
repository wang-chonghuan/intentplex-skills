---
name: ips-personas
description: Load when the user wants to judge a user-facing artifact — a page, flow, feature, output, or questionnaire — through simulated product users, to learn whether it meets or exceeds user expectations and will attract, retain, or grow users. The user fills one spec template, then trial-runs one persona and runs a panel as independent subagents. Trigger phrases include "ips-personas", "persona review", "用户视角评审", "模拟用户看这个", "这个页面能留住用户吗". Do not load to judge an artifact by its author's intent — use ips-telos for final-cause review.
---

# ips-personas

Judge a user-facing artifact the way real users judge it: through a panel of situated personas, each run as an independent subagent that actually experiences the artifact and reports back. Use it to answer one product question about a page, flow, feature, output, or questionnaire — will this **attract**, **retain**, and **grow** users, or lose them?

The whole interface is one filled spec → a trial run → a full run. This skill produces persona verdicts and a synthesis. It never modifies the artifact under review.

## First principle: the skill is fixed, the spec is the only variable

This skill is written so that **a good spec produces a good run.** The run contract — bracketing, outcome-level goals, exploration, grounding, anti-vagueness, default-churn — is baked into the capabilities as a constant that the user never touches. Therefore the only optimization variable during use is the **spec** (`assets/spec-template.md`, filled into the session).

When a trial run produces weak output, the diagnosis is *the spec was not good enough* — improve the spec, not the skill. The trial run tests whether the **input** is sufficient; it never carries the blame for skill quality. (A dead link or gated target is an environment problem: report it as *not experienced*, don't treat it as a spec defect.) If the run contract itself ever proves wrong, that is an authoring-time bug in this skill, outside the user's optimization loop.

## Core Logic — the Doxa engine

ips-telos judges an artifact by its maker's *final cause*: why it was built. This skill judges the same artifact by its **user's** cause, from the outside. Three moves, in order:

1. **Bracket the maker (ἐποχή).** The user encounters only the *phenomenon* — what appears on screen or in the output. They never see your intent, effort, roadmap, or the constraint that made it hard. Judge only what appears. This stops the maker from grading their own homework; a persona may credit nothing it cannot perceive.
2. **Measure against the user's telos, not yours.** Each persona arrives carrying its own end — the job it came to get done — judged first by whether it serves that end and meets the expectation the user arrived with. Comparison against **specific named competitors** is an optional lens set in the spec; a comparative personality still weighs against its own generic baseline (habit, free option, doing nothing) through its expectation either way.
3. **Default to churn — but earn every verdict.** A persona's baseline is to leave. Staying, clicking, returning, recommending must be *earned* by something perceived. Agreeable, conforming feedback is the known failure of simulated users. But the mirror is equally worthless: churn is the *default*, not the *goal*, and **manufactured friction is as invalid as manufactured praise**. Both staying and leaving must trace to something perceived and cited.

## The persona model: two axes

A single persona sees only its own encounter, so it catches defects *in* an encounter but never in the *distribution* of the whole output. Composition spans two independent axes:

- **Goal / need (the spine, always required).** What the persona came for. Spread goals across the space the artifact should serve to catch **coverage defects**: narrow, one-note, one-dimensional, serving only one segment. This is the primary axis.
- **Temperament (the exploration policy).** *How* the persona judges and wanders — patience, trust, tech-literacy, what earns a step, what triggers churn. The built-in cast is a menu in `references/persona-cast/` (see its `index.md`); a spec row may also define a custom temperament inline. Temperament catches **experience defects**: confusing, slow, untrustworthy, unscannable — and it is what makes each persona explore *differently*, like different real humans, rather than march one optimal route.

Compose on the diagonal: pair each goal with the temperament most likely to expose its failure. **If every persona wants the same thing, an artifact that serves only that thing looks perfect to all of them** — coverage defects surface only when goals span, and only in synthesis, as a pattern across personas.

## The interface: one spec → trial → run

Everything the user provides lives in one filled template, `assets/spec-template.md`, copied to `cwd/.ips-personas/sessions/<slug>/spec.md`. Then:

**Capability 1 — Draft the spec.** Copy the template into the session; for a bare request ("review my app"), pre-draft the goals-to-span and the persona diagonal so the user edits rather than starts blank. Read `references/capability-1-draft-spec.md`.

**Capability 2 — Trial run.** Run one persona (the riskiest, or two of the most different) from the spec, show the output, and check it against `references/quality-checklist.md`. Good → full run; weak → improve the spec and re-trial. This replaces a per-result gate. Read `references/capability-2-trial-run.md`.

**Capability 3 — Full run + synthesize.** Run the selected or all personas as independent subagents under the fixed run contract, collect results, spot-check a sample, and synthesize. Read `references/capability-3-run.md`.

## Session layout

```
cwd/.ips-personas/sessions/<slug>/
├── spec.md              # the only input: target, context, intent, goals, personas, run scope
├── shots/               # Playwright-rendered screenshots + steps.json (live web targets)
├── results/<persona>.md # one per persona, written by its subagent
└── report.md            # synthesis
```

Full contract in `references/common/session-layout.md`. All state lives in the user's repo, never in the skill.

## Rules

- The skill is fixed; the spec is the only variable. When a run is weak, improve the spec.
- Judge only what a persona can perceive. Never credit maker intent, effort, roadmap, or unshipped plans.
- Success for a persona is an honest report of its experience, not task completion. A persona that bounced before finishing is a valid, informative result.
- Span two axes: goals across what the artifact should serve (coverage), temperament across how users explore (experience). Goals whose span is narrow can only yield a narrow claim — say so.
- Default verdict is churn, symmetric: manufactured friction is as invalid as manufactured praise.
- Run subagents independently so one persona's reasoning does not contaminate another's. If the host has no subagents, role-play each in as close to a reset context as the host allows, one at a time.
- For a live web target, render it with Playwright (real Chromium, executes JS) via `scripts/render-capture.mjs` so personas experience the real product — never judge a JavaScript app from a WebFetch shell. See cap 3.
- Never modify the artifact under review. Write all state to `cwd/.ips-personas/`.
