# The four lenses

Four subagents, launched **in one message so they run in parallel**, each blind to the others. The
point is four different ways of failing to be right, not four readings of the same document.

Every brief below is a template. Fill the bracketed parts, and **paste the whole of
`finding-rules.md` into each one** — the evidence format, the severity table, the out-of-scope list,
the quota, the author-intent exemption and the usage facts. A lens briefed without those returns
prose about style.

Every brief also carries these three lines verbatim:

> Read-only. Do not edit, create or delete any file in the target.
> Do not propose rewrites — diagnose only. The fix is decided later, by a human.
> Rank your findings worst-first, and stop when you run out of real ones.

And when the agent is being given less than the whole skill (see the index route in cap1):

> You are seeing part of this skill, not all of it: `[what you have]`, and not `[what you do not]`.
> Any finding of the form "X is never defined / never read / missing" is therefore `PLAUSIBLE` at
> best — say so, and never mark one `CONFIRMED`. The thing you think is missing may be in a file you
> were not given.

---

## Lens 1 — 矛盾 Contradiction

> You are auditing one agent skill for **internal contradictions**. Read every file it ships:
> `[list every path]`.
>
> **Your only job: find statements that cannot both be obeyed.** Two rules pulling opposite ways. A
> rule stated one way in the hub and another way in a capability file. A template promising something
> the flow forbids. A file named one way in one place and another elsewhere.
>
> Method: build a list of every **normative** statement — anything phrased as must / never / always /
> only / required / by default — with its file and line. Then compare the ones that touch the same
> subject. Contradictions hide between files that were edited at different times, so compare **across**
> files harder than within them.
>
> `[If the skill was recently reworked, name the changes: "X was renamed to Y", "the rule permitting Z
> was added and then removed" — half-finished edits are the richest seam and the agent cannot see the
> history.]`
>
> For each: state the conflict in one sentence, quote **both** sides with file:line, say **which side
> you believe is intended and why**, and mark CONFIRMED or PLAUSIBLE.
>
> **When you cannot tell which side is intended, say so explicitly and stop trying.** Do not pick one.
> An unadjudicable contradiction is a specific, valuable result: it marks a place where the skill needed
> to know its own priorities and never wrote them down. Report it as `UNADJUDICABLE` with both sides
> quoted. Collect these separately at the end of your report.

## Lens 2 — 漏洞 Gap

> You are auditing one agent skill for **gaps** — situations its instructions do not cover, where an
> agent following them would stall, improvise, or silently do the wrong thing. Read every file:
> `[list every path]`.
>
> `[Describe what the skill does and its flow in three or four sentences — this lens needs the shape
> of the flow, not the purpose behind it.]`
>
> **Method: sit in the executing agent's seat and walk each capability end to end, asking "what if…"
> at every step.** Specifically hunt for:
>
> - **Branches with no instruction** — a combination of inputs, modes or types that no file covers.
> - **Nearest-fit hazards** — a request a human will realistically bring that maps onto none of the
>   capabilities. A skill listing N capabilities implicitly claims those are all, and an agent will
>   force the request onto the closest one rather than say "not here". Ask: what will people actually
>   ask this skill for, and does every one of those have a home or an explicit "not here"?
> - **Resume and re-entrancy** — states a restarted run cannot recover from, or where resuming
>   duplicates work or re-does something irreversible.
> - **Undefined preconditions** — a value, file, id or state that is used but never produced.
> - **Dead-end failures** — an instruction to stop that never says what state things are left in: what
>   happens to the branch, the process, the ticket, the half-written file, and who cleans it up.
> - **Ordering hazards** — two steps whose order matters where the order is not stated.
>
> For each: the concrete scenario, the instruction quoted with file:line showing coverage stops there,
> **what the agent would realistically do instead**, and severity.
>
> "The error handling could be better" is worthless. "If the rebase conflicts and the human is away,
> nothing says whether the worktree survives" is a finding.

## Lens 3 — 事实错误 Factual error

> You are auditing one agent skill for **claims that are false**. Read every file it ships:
> `[list every path]`. **You may and must run read-only commands** — `ls`, `cat`, `grep`, `--help`,
> `git log`, syntax checks — to verify things instead of reasoning about them.
>
> **Your only job: statements that do not hold when you go and check.** Verify, do not infer:
>
> 1. **Paths.** Every file the skill references. Does it exist? Run `ls`. Also flag files present but
>    referenced nowhere.
> 2. **Partner skills.** This skill delegates to `[names]`, at `[paths]` (some may be symlinks — use
>    `ls -L` / `find -L`). Read their `SKILL.md` and their scripts. Does this skill describe their
>    capabilities correctly? Does it name commands and flags they actually have?
> 3. **Its own scripts.** Run their `--help` / usage. Does the documented command set match the real
>    dispatch? Do they parse (`bash -n`, `node --check`, `python -m py_compile`)?
> 4. **Commands and snippets.** Every shell and git command in the skill. Do the flags exist **on this
>    platform**? Does the syntax parse? Check rather than assume — a flag you believe is GNU-only may
>    be accepted as a compatibility no-op, and a confident wrong claim here is worse than silence.
> 5. **Derived claims.** Anything asserting a bound, a limit, a range, a count or an arithmetic
>    property. Compute it. These are wrong surprisingly often and nobody re-checks them.
> 6. **Cross-file facts.** A number, filename or field name stated differently in two places — verify
>    which is right rather than reporting the mismatch.
>
> For each: the false claim quoted with file:line, **the exact command you ran and its output**, what
> is actually true, and impact.
>
> **Report only what you actually verified.** Anything you could not check goes in a short separate
> "unverified" list at the end — never as a finding, never as a guess.

## Lens 4 — 背离宣言 Self-betrayal

> You are auditing one agent skill for **drift from what it says it stands for**. Read every file:
> `[list every path]`.
>
> **First, find the skill's own declared principles and quote them exactly.** Look for statements
> about what it is for, what it refuses to do, what it deliberately deleted, what it says it is not.
> `[Quote them here if they are already known.]`
>
> **If the skill states no principles of its own, say so and change mode.** Do not invent a standard
> to convict it with — that is the one failure this lens must never commit. Instead report *observed
> tension*: "from its behaviour this skill appears to optimize for X; these three places work against
> that", marked explicitly as inference. Weak evidence, honestly labelled, beats a confident
> conviction against a standard you made up.
>
> When it does state principles, hold every part of the skill to them and hunt for:
>
> - **Re-verification** — a step that checks something an earlier step already established.
> - **Smuggled gates** — a checklist, sign-off or precondition audit wearing another name.
>   Distinguish honestly: a confirmation before an **irreversible or external** action is legitimate
>   and is not a finding; a gate on a reversible internal step is.
> - **Bookkeeping with no reader** — trace every artifact the skill produces to the step that consumes
>   it. **Actually search for the consumer before claiming there is none.** An artifact nothing reads
>   is dead weight by the skill's own standard.
> - **Restatement** — the same rule in three files. Count the homes and name them. A rule with five
>   homes will diverge in one of them, and that is the concrete failure.
> - **Over-specification** — a rule so detailed it is already wrong, where a one-line principle would
>   have held.
>
> For each: what it is, quoted with file:line; **which stated principle it violates, quoted with its
> own file:line**; and the concrete cost.
>
> Then, at the end, **the reverse check**: at most three places where this skill is dangerously
> **under**-specified — one missing instruction away from letting a real failure through unnoticed.
> Same evidence rules. Do not pad it.
