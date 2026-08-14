---
name: ips-tooltrend
description: Load when the user wants, for a product category, the buying lens rather than a product recommendation — what actually decides the choice, the pitfall buyers regret, and where the category's capabilities are heading. Triggers include "ips-tooltrend", "before you pick", "选品指标和坑", "这个类目该看什么、避什么、在往哪走", "研究一下这个领域怎么选". Produces three sourced one-liners per category. Do not load to rank or recommend specific products.
---

# ips-tooltrend

Research a product category and return three lines that help someone choose
*within* it: what decides the choice, what buyers regret, and how the class of
product is changing. The output is a lens, not a recommendation — the lines must
work for a product that is not on anyone's list yet.

The whole method is `references/research-prompt.md`. Read it before running
anything; it holds the prompt verbatim, the placeholder table, and why each part
of it is load-bearing.

## Running it

One subagent per category, with web search and file read. Categories are
independent, so launch them in parallel and let them finish out of order.

Substitute the placeholders and send the prompt unchanged. Do not paraphrase the
two tests, the email-client illustration, or the empty-string rule — each of
them exists because an earlier version failed without it, and softening any one
of them reproduces that failure.

Expect roughly two to four minutes and fifteen to twenty tool calls per
category. A subagent that returns in under a minute did not search.

## Reviewing what comes back

The subagent applies the two tests to itself. Apply them again — it is the
author, and authors pass their own work. Then check what the prompt does not
cover:

**Strip numbers that no source states.** A run produced "every tool automates
roughly 90-95% of transactions" while its own evidence trail showed vendors
claiming 96.5% and 98%. The figure was inferred, not found. Numbers are also the
least stable part of the output: two runs against the same report returned 4.6×
and 5.3× for the same metric. Prefer lines with no number at all — the strongest
outputs had none.

**Distrust the `moving` line's sources hardest.** It is the slot that attracts
prices, launches and dates, and those are exactly what secondary blogs repeat
without checking. Three SEO sites agreeing is one source, not three. Require the
vendor's own changelog, pricing page or help centre, or drop the line.

**Watch the shape repeat across categories.** "They all demo well on X; the real
test is Y" is a good line once and a template by the fifth time. When running
many categories, read the `weigh` lines together and send back any that share a
skeleton.

**These are opinions, and some are strong** — "model choice barely matters now"
is an argument, not a fact. Route them through whatever review the destination
uses for authored content. This output is not safe to publish unattended, and a
nightly job that regenerates and publishes without a human is the one deployment
shape to refuse.

## Where the output goes

Persist it with the destination's *authored* content, not with anything a
scheduled job may overwrite. The lines are researched judgements and they decay:
store a date alongside them and treat it as a review clock, not a timestamp.

## Gotchas

Research runs on a category also surface staleness in the material they read —
prices that moved, a top-ranked entry whose licence forbids the use it is ranked
for. That is a finding about the corpus, not about the card. Report it
separately rather than folding it into the three lines.
