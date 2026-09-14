# Gate 3: Safe Upgrade

What was this output created to accomplish, and could the application be "upgraded" while losing functionality, changing data meaning, or depending on an unsupported stack?

Use an inline independent-stance review; prefer an independent reviewer for major or shared SSR/provider changes when delegation is permitted. Supply old/new versions, relevant release refs, baseline, final diff and real test/browser results.

## Blocking Invariants

- The selected stable set is compatible, pinned and reflected in the lockfile/installed packages; exceptions require explicit approval.
- Changed APIs are verified against their own packages, including X/Charts and CLI report schema.
- Product meaning, SSR, interaction, access and token/component discipline remain intact with adequate current regression evidence.

Record `PASS` or `INCOMPLETE` with evidence and concrete defects. Allow one targeted repair/recheck; return to missing prerequisites or report an unresolved blocker rather than weakening tests. A successful install or goal status cannot pass this gate.
