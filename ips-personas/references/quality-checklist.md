# Quality checklist

Used by the trial run (cap 2) and the sample spot-check (cap 3) to judge whether a persona result is a real user's grounded judgment or a hollow performance. This is a *reading* checklist, not a per-result rerun loop — quality is primarily enforced by the run contract in cap 3. A failure here means the spec was insufficient (see cap 2's diagnosis table), not that a gate is missing.

A result should pass all of these:

1. **Grounded, not vague.** Every reaction is pinned to a specific screen/step/element with a verbatim quote. No generic lines ("the UX could be smoother"). This is the single most important check. For a live web target, the quotes must come from the Playwright-rendered product (the `shots/` bundle), not a WebFetch shell — a JavaScript app judged only from its un-rendered shell is *not experienced*, and any "it's broken/empty" verdict built on that is invalid.
2. **A real step-by-step friction log.** The log is ordered by what the persona hit, in the moment — not a tidy after-the-fact summary. If it reads like a feature description, the persona never actually traversed it.
3. **Experience over completion.** The result reports what it was like, including hesitation and where it would bounce — not just whether the task got done. A pre-completion bounce is a valid result, not a failure to grade.
4. **In character.** The reactions match the temperament — an anxious-novice doesn't read like a power user; a distracted-skimmer didn't carefully read everything.
5. **Not sycophantic, not manufactured-negative.** It didn't like everything on thin justification; it also didn't invent complaints or edge cases it never hit. Both are hollow.
6. **Bracket intact.** It credits only what appears, never the maker's intent, effort, or roadmap.
7. **Expectation-anchored, competitor-correct.** Below/Meets/Exceeds is judged against the persona's stated expectation. If §5 configured a competitor, it was actually visited and compared; if not, no specific external product is named or claimed as visited.
8. **Actionable.** A single highest-leverage change is named.

If a sampled result fails, the spec — not the skill — is the thing to change. Improve the spec (cap 1) and re-run.
