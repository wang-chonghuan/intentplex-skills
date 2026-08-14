# Capability 3 — Run + synthesize

Run the personas from a filled `spec.md` against the target and produce their verdicts plus a synthesis. Each persona runs as an **independent subagent** so its reasoning cannot contaminate another's. This capability holds the fixed **run contract** — the constant that makes a good spec produce a good run.

## Inputs

- A filled `cwd/.ips-personas/sessions/<slug>/spec.md`.
- The run scope from §6 (all, or specific persona numbers). If §6 asked to trial first and that hasn't happened, do cap 2 first.

## Preflight: verify the spec is safe to run

Before assembling any brief — this runs for both the trial (cap 2) and the full run — verify the two bracket channels, because personas will see §2 but never §3:

- **§2 shared context is neutral.** Scan it for benefit claims, value propositions, or outcome framing. Selling language here biases *every* persona toward approval, and the trial cannot catch it — a bias-inflated positive result reads exactly like a clean pass. If §2 carries any selling, that is a **spec defect**: stop and fix §2 before running (first principle — diagnose the spec, never feed a polluted §2 to personas). This is an input check, not a per-result gate.
- **§3 product intent is present and will be withheld** from every persona; it is opened only at synthesis.

## Rendering a live web target (use Playwright — do not trust WebFetch)

A modern web target is usually a JavaScript app: `WebFetch`/`curl` return only the un-rendered shell (logo, nav, tagline) and its client-side routes 404 on a direct hit. **Judging from that shell is the classic way to produce a confident, wrong verdict** about a "broken" or "empty" product — a persona must experience the REAL rendered product, so render it in a browser that executes JS.

Default method: **Playwright (real Chromium)** — the same engine n-autoqa uses. `scripts/render-capture.mjs` drives it:

```
node scripts/render-capture.mjs <url> <session>/shots "Section A" "Section B" ...
```

It opens the target, waits for the SPA to render, screenshots the landing state and the state after clicking each label, and writes `<session>/shots/NN-*.png` plus `shots/steps.json` (verbatim on-screen text per state). Prerequisite: Playwright + Chromium (n-autoqa cap 1 provisions it, or `npx playwright install chromium`).

Two modes:

- **Shared render pass (default).** Before launching personas, drive the flows each §4 goal would require — landing + each main section/drawer + a representative interaction (set a budget, submit a form). Every persona then experiences this one bundle: it reads the shots + `steps.json`, quotes what it saw, and marks anything it would have tried but isn't captured as *not experienced*. One browser run serves all personas — cheaper and reliable.
- **Per-persona live driving.** When a persona's path materially diverges, hand that subagent the same helper and let it drive its own path in character.

Keep the script's gotcha: for SPAs with continuous network (maps, polling) do **not** wait on `networkidle` — it times out; use `domcontentloaded` + a stability wait. The in-app MCP browser may be used instead when healthy, but Playwright is the default because it renders like a real user and does not depend on that service. If a target genuinely cannot be rendered, mark results *not experienced* — never judge a JS app from its fetch shell.

## The run contract — bake this into every persona subagent's brief

Launch one subagent per selected persona (Claude Code: Agent/Task tool; other hosts: their subagent mechanism). If the host has no subagents, role-play each in as close to a reset context as the host allows, one at a time, carrying no prior persona's notes forward.

Give each subagent: its persona row from §5 (goal, temperament — from `references/persona-cast/<slug>.md` or the inline description — expectation, optional competitor), the §2 shared context, and the §1 target. **Never** include §3 product intent. Then bind the contract below.

### ★ Headline clause: success is an honest report of experience, not task completion

This is the lever that turns a task-completing robot into a person who hesitates and quits. It leads the brief; it is not a footnote.

- **Mechanism (the output contract shapes behavior).** An agent told "your job is to complete X" tunnels toward X, ignores friction on the way, and reports only done/not-done. An agent told "your job is to behave like <persona> and react to everything you meet on the way to X, naming every place you'd hesitate, doubt, or want to quit" attends to every step. Demanding a step-by-step friction log *forces* it to watch each step.
- **State it plainly in the brief:** "Success is honestly reporting your experience, not finishing the task. Bouncing before the end is a valid, informative result — a real user leaving *is* the finding."
- **Pursue the goal at outcome altitude.** The §5 goal is the *end* the user wants; friction is whatever stands in the way. Never treat a friction step as the goal — you don't complain about the task you were assigned, only about the obstacles to what you actually wanted.
- **Explore like a human, and you are authorized to.** Move step by step; you may wander, backtrack, get pulled toward a shinier button, or give up. Report where you deviated and where you quit.
- **Temperament is your exploration policy.** An impatient-skeptic bails fast; an anxious-novice freezes at jargon; a curious enthusiast pokes everything. Let the temperament drive the path and the reactions.

### The rest of the contract

- **Actually experience the target.** For a live web target, experience the Playwright-rendered states (see "Rendering a live web target") — read the shots + `steps.json`, pursue your goal through them, and quote what you actually saw; mark anything you'd have tried but isn't captured as *not experienced*. For a static output or file, read it directly. For a questionnaire, answer each question in character, grounded in the experience.
- **Ground everything, no vagueness.** Every reaction — praise or complaint — is pinned to a specific screen, step, or element, with a verbatim quote of what you saw. Banned: generic lines like "the UX could be smoother." If you can't reach the target, say so and mark the result *not experienced* rather than narrate a fiction.
- **Judge by your telos and the expectation you arrived with.** Rate Below/Meets/Exceeds against *your stated expectation*, not in the abstract.
- **Competitors.** If §5 named a competitor for you, actually visit it and judge against it. If none, do not name or claim to have used a specific external product you never saw (a comparative temperament may still weigh against its own generic baseline — habit, free option, doing nothing).
- **Default to churn, symmetric.** Baseline is to leave; earn any step forward by something perceived. Do not manufacture friction you didn't hit — invented complaints fail as hard as invented praise.

### Per-persona output shape

Each subagent writes `results/<persona>.md`:

```markdown
# <Persona> (goal: <G>) — verdict

- Verdict: Churn | Stay-and-shrug | Convert | Advocate
- Meets expectation: Below | Meets | Exceeds   (vs MY stated expectation)
- vs competitor: <only if §5 configured one — name it and whether this beat it; omit otherwise>

## Step-by-step friction log   (in the order I hit it, NOT a summary)
- Step <n> · saw: "<verbatim on-screen text / element>" · reaction: <my in-character feeling> · hesitate or want to quit?: <pinned here if so>
- ...
- <where I deviated / bounced / gave up, and why>

## What earned a step forward
<only things perceived and cited; empty is a valid, important answer>

## What pushed me toward churn
<friction I actually hit — never invented>

## The one thing that would change my verdict
<the single highest-leverage change, in this persona's own priorities>
```

## Spot-check, then synthesize

Do not gate every result with a rerun loop. Instead, spot-check a **sample** (1–2 results) against `references/quality-checklist.md`. If the sample is clean, trust the run — the contract, verified once in the trial and again here, is the guarantee. If the sample is weak, the spec was insufficient: fix the spec (cap 1) and re-run, per the first principle.

Then write `report.md`. Only here may you open §3 product intent — the synthesis's core value is the gap between what the maker hoped and what the personas perceived.

```markdown
# Persona Review — <slug>

## Verdict at a glance
| Persona | Goal | Verdict | Meets expectation | vs competitor (if any) |
|---------|------|---------|-------------------|------------------------|

## Attract / Retain / Grow
- Attract: <will it win the first encounter? who bounced and where>
- Retain: <will it hold them past first use? what erodes staying>
- Grow: <will anyone advocate? what would make them, or what caps it at shrug>

## Intent vs perception gap
<where the maker's hoped-for outcome and the personas' lived experience diverge — most actionable>

## Distributional read
<defects no single persona can see — monotony, narrowness, a missing dimension, serving one segment. Read the pattern: convergent churn for the SAME reason ("nothing here addressed my need") means the output is one-note relative to the needs it should serve — name the facet it collapsed onto and the ones it missed. Mandatory caveat: state whether the roster's goals spanned what the target should serve; if not, this can only report the needs tested, not that the output is well-rounded.>

## Convergent / Divergent findings
<what differently-motivated personas independently hit; where they split and which segment each represents>

## Excluded / not-experienced
<any persona that couldn't reach the target, and why>

## Highest-leverage changes
<ranked; each tied to the personas and the attract/retain/grow lever it moves>
```

## Rules

- Keep subagents independent; never leak §3 intent into a persona; never carry notes between personas.
- The friction log is required and ordered — it is the structural device that forces step-by-step attention.
- Report; never modify the artifact under review.
- Quality is enforced by the contract + trial + sample spot-check, not by a per-result gate. A weak result means a weak spec, not a missing gate.
