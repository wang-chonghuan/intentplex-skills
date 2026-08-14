# Session layout

All working state lives in the user's product repo at `cwd/.ips-personas/`, never inside the skill. `cwd` is the repository the user is reviewing, not the skill directory. One review = one self-contained session folder.

```
cwd/.ips-personas/sessions/<slug>/
├── spec.md              # the only input (cap 1): target, context, intent, goals, personas, run scope
├── shots/               # Playwright render pass (cap 3): NN-*.png + steps.json for a live web target
├── results/             # one file per persona, written by its subagent (cap 3)
│   └── <persona>.md
└── report.md            # synthesis across personas (cap 3)
```

There is no separate persona storage directory. Custom temperaments live inline in §5 of `spec.md`; built-in temperaments are referenced by slug from `references/persona-cast/`. The run capability may optionally write each subagent's assembled brief under a `briefs/` subfolder for audit, but that is not required.

## spec.md

`spec.md` is a filled copy of `assets/spec-template.md`. Its six sections are the entire input surface:

1. **Target** — what the personas experience (artifact or questionnaire).
2. **Shared context** — neutral situation only; shown to personas, so no selling language.
3. **Product intent** — bracketed; never enters any persona's context, opened only at synthesis.
4. **User goals to span** — outcome-level goals, spread across what the target should serve.
5. **Personas** — the diagonal: each goal paired with a temperament (cast slug or inline), an expectation, and an optional competitor.
6. **Run scope** — trial-first choice and which personas to run.

Keep §3 product intent out of §1, §2, and §4 — the gap between §3 and what personas perceived is the synthesis's most valuable output, and it only works if personas never saw §3.

## Naming

Use short kebab-case slugs for sessions (`onboarding-v2`, `pricing-page`) and personas (`impatient-skeptic`). Do not rename a session's files mid-review.
