# Capability 1 — Draft the spec

Produce the one input the whole review runs on: a filled `spec.md` in the session folder. The spec is the only variable the user tunes, so this step is about getting it *good*, not about interrogating the user.

## Steps

1. Choose a short kebab-case session slug (e.g. `onboarding-v2`, `pricing-page`) and create `cwd/.ips-personas/sessions/<slug>/`.
2. Copy `assets/spec-template.md` to `cwd/.ips-personas/sessions/<slug>/spec.md`.
3. **Pre-draft, don't interrogate.** For anything more than a fully specified request, fill in a first draft the user can edit:
   - Infer §1 target and §2 neutral context from the request and repo.
   - Propose §4 **goals to span** — the real outcome-level ends users come to this target for. Spread them across the space the target should serve (an onboarding covers "get set up and reach first value"; a pricing page covers "decide if it's worth it," "compare plans," "trust the vendor"). Goals are outcomes, never features or friction-steps.
   - Propose §5 **the diagonal** — pair each goal with the temperament most likely to expose its failure (a signup goal → `anxious-novice` or `impatient-skeptic`; a value goal → `value-comparator`; a dense output → `distracted-skimmer` + `detail-critic`). Pick temperaments from `references/persona-cast/index.md`, or write a custom one inline in the table when no cast temperament fits.
   - Leave §3 product intent for the user (it's theirs), and §6 run scope with a sensible default (trial the riskiest persona first).
4. Show the draft and ask the user to correct goals, personas, expectations, and — if they want a comparative verdict — fill §5's optional competitor column. Confirm before handing to cap 2.

## What "good" looks like (so the draft aims right)

- **§2 is neutral.** Strip every benefit claim, value prop, and outcome framing — selling language shown to a persona smuggles maker intent past the bracket. Describe what the thing *is*, not how good it is.
- **§3 is bracketed.** Product intent stays in the spec but is never copied into any persona's context; it is opened only at synthesis.
- **§4 goals are outcomes, and they span.** Outcome-level goals are what let friction be *discovered on the way* rather than scripted. A goal list that all points at one facet cannot detect a one-note artifact — if the space genuinely can't be spanned, say so in the report later.
- **§5 is a diagonal, not a product.** N goals, N personas, each goal paired with one revealing temperament — not every goal × every temperament.

## Rules

- Do not create a separate persona file or storage directory. Custom temperaments live inline in §5 of the spec; the built-in cast is referenced by slug.
- Every persona row needs a goal and an expectation before the spec is runnable. Competitors are optional.
- Keep product intent out of §1, §2, and §4. Only §3 holds it, and only synthesis reads it.
- **§1 must be experienceable now.** The target has to be something a persona can actually open and use today — a running app/page, a reachable file, a concrete output, or a questionnaire — not a not-yet-built described flow. If nothing is experienceable yet, say so before running; the review needs a real artifact, or every result comes back *not experienced*.
- **Verify §2 neutrality before handoff.** §2 is the one channel personas see, so a selling or outcome-framing leak here silently biases them. Re-read §2 and strip any benefit/value/outcome language before handing to cap 2. (cap 3's preflight re-checks this, but catch it here first.)
