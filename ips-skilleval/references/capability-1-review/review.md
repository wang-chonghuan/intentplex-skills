# Capability 1: Audit a skill

Four lenses, in parallel, then adjudicate. The output is a **decision list for the human**, never a
patch — nothing in the target is edited by this capability.

Read `references/common/finding-rules.md` before briefing anything. It is what stops a lens from
returning a style review, and every lens gets a copy of it.

## 0. Say what this costs

Before anything else, tell the human what they are buying: four subagents over every file the skill
ships, an ips-telos pass, plus a refuter per serious finding.

The one measured run — a 21-file, ~1700-line skill — cost about 390k subagent tokens for the four
lenses alone. **That is a single observation, not a formula**; quote it as one and scale your estimate
by the file count in front of you rather than repeating the number.

Then check it is worth spending. **Say so and offer to stop** when the target is freshly written, or
when the only change since the last audit was small. This audit finds what accretion breaks; on a
skill that has not accreted anything it will find grammar.

## 1. Scope — everything it ships

Enumerate the real file set. Do not trust a directory listing that has not followed symlinks; skill
directories are frequently symlinked into place:

```bash
find -L <skill-dir> -type f | sort
```

Every one of those files is in scope. Four of them deserve specific attention:

- **The hub** (`SKILL.md`) — the only file always in context. Everything else is loaded on demand,
  which means a rule that lives only in a spoke is a rule an agent may never read.
- **`scripts/`** — executable, therefore checkable. Lens 3 runs them.
- **`templates/`** — **weight these heaviest.** A defect here gets copied into other repositories and
  becomes that project's own file; fixing the skill afterwards does not reach it. A template error is
  the only kind that escapes.
- **The frontmatter `description`** — read it, but see the usage facts before spending any attention
  on it. When the skill is invoked by name, its precision is not load-bearing.

If the skill delegates to other skills, resolve their real paths now — lens 3 will need them to check
whether the claims made about them are true.

### When the skill is too big to hand a lens whole

Measure before deciding: `find -L <skill-dir> -type f -name '*.md' | xargs wc -l | tail -1`. Under
roughly 3000 lines, give every lens everything and skip the rest of this section.

Above that, **do not simply split the files between agents.** Contradictions and orphaned rules live
*between* files; an agent holding half the skill cannot see them, and worse, it will confidently
report "X is never defined" about something defined in a file it was not given. Sharding a lens
without care turns it into a false-finding generator.

Instead, build a **normative index** first — one cheap pass that reads every file and extracts only
what the lenses compare:

```markdown
<file>:<line> | MUST|NEVER|ALWAYS|ONLY|DEFAULT | <the statement, verbatim>
<file>:<line> | PRODUCES | <artifact it writes>
<file>:<line> | REQUIRES | <artifact, value or state it consumes>
<file>:<line> | POINTS-TO | <file it tells the agent to read>
```

That index is usually a tenth of the skill and carries almost everything lenses 1 and 4 need. Then:

- **Lens 1** works from the index, opening only the files behind a suspected conflict. Cross-file
  comparison is preserved, which is the whole point.
- **Lens 2** gets the files that describe **execution** — the hub and the capability files — in full,
  plus the index for everything else. It walks flows; it does not need every template verbatim.
- **Lens 3 shards cleanly.** Checking a path or a command in one file needs no other file. Split it by
  file group across several agents and merge; nothing is lost.
- **Lens 4** gets the hub in full (that is where principles live) plus the index, whose `PRODUCES` /
  `REQUIRES` rows are exactly what the artifact-has-no-reader trace needs.

**Any agent given less than the whole skill must be told what it is not seeing**, and its "never
defined / never read / missing" findings come back as `PLAUSIBLE`, never `CONFIRMED`. Adjudication
verifies each of them against the full file set before it can be reported. State in the final report
that the index route was used.

## 2. The usage facts

Ask the three questions in `finding-rules.md` — who runs it, how it is invoked, what a wrong run
costs. One message, three questions, and they are answerable in a sentence.

**Do not ask what the skill is for.** That question is answered later, only if the audit proves it
needs answering, and by then it can be asked concretely. Asking it now gets an improvisation that
then contaminates every lens.

Carry the answers into all four briefs. They are the fastest filter available: each one deletes a
whole category of finding before it is written.

## 3. The blind spot the lenses share — and the ips-telos pass that covers it

**The four lenses share a blind spot: every one of them is an internal-consistency machine.** They
can prove a skill disagrees with itself, does not cover a case, states something false, or has
drifted from its own words. **None of them can say the skill is the wrong shape.** A skill can be
perfectly consistent, fully covered, factually exact, faithful to its principles — and still be built
wrong. Nothing in the four will ever tell you that.

So run **ips-telos** on the target at the same time, as a fifth parallel job. It is single-agent,
judgment-led and cheap next to the lenses, and it answers the one question they cannot: does this
artifact's form serve the reason it exists?

**Two rules keep it from re-introducing the circularity this design was built to avoid:**

1. **Its output goes to the adjudicator only, never to a lens.** ips-telos infers a final cause; if the
   lenses saw it, they would all convict against one agent's inference and the independence that makes
   four lenses worth running would be gone.
2. **Its findings do not enter the report as findings** unless they pass the same failure-scenario
   test as everything else. What it uniquely contributes is a **verdict on the shape**, and that is
   reported as a verdict, in its own section, marked as judgment rather than evidence.

## 4. Launch the four lenses

**One message, four agents, so they run in parallel.** They must be blind to each other — the value
is four independent failure modes, and an agent that has seen another's findings anchors on them.

Build each brief from `references/common/lenses.md`, filling in:

- the full file list from step 1;
- the whole of `finding-rules.md`, verbatim;
- the usage facts from step 2;
- for lens 2, three or four sentences describing the skill's flow — this lens needs the **shape**, not
  the purpose;
- for lens 1, any recent rework you know of: renames, a rule added then removed, a file split. **Half-
  finished edits are the richest seam and the agent cannot see the history.**

While they run, do not duplicate their work. Reading a file yourself to prepare for adjudication is
fine; running lens 3's checks in parallel with lens 3 is waste.

**If a lens fails or returns nothing usable**, re-launch that one lens once. If it fails again,
continue with the rest and **say in the report which lens did not run** — a three-lens audit reported
as four is a false clean bill of health on whatever that lens covered. Never substitute your own
reading for a failed lens and present it as that lens's result.

## 5. Adjudicate

`references/common/adjudication.md`, in full: merge, resolve inter-lens conflicts, adversarially
verify everything at 会犯错 or above, classify 机器可修 / 需人裁决, group the unadjudicable
contradictions, write the report.

Two failure modes to name, because both feel like diligence:

- **Relaying.** Pasting four reports and calling it an audit. The adjudication *is* the deliverable.
- **Deferring to the subagents.** They are confident and they are sometimes wrong. When two disagree,
  whoever ran the command wins; when neither ran it, run it yourself.

## 6. The second ips-telos pass — patch or restructure?

Once the report exists, run **ips-telos once more**, giving it the target *and the adjudicated
findings*, and asking one question:

> Given these confirmed defects, is this artifact still fit for its purpose with these fixed — or do
> they indicate the design itself is wrong, and patching them one by one is the wrong response?

This is the only step that can return **"do not fix these twelve things"**. A long defect list is
sometimes a symptom rather than the disease, and an audit that only ever produces patches will keep a
badly-shaped skill alive by mending it forever. Today's list is exactly the evidence needed to tell
the two apart, and it did not exist before adjudication — which is why this pass runs here and not
at the start.

If it says restructure, that goes at the top of the report as its own recommendation, with the
defect list kept beneath it as supporting evidence. **The human decides**; this skill does not
restructure anything.

Do not run it a third time. Two passes — one on the artifact, one on the artifact plus what was
found — is the whole of it.

## 7. Hand over

Give the human the report from `adjudication.md`. Then stop.

**Do not start fixing.** Even the 机器可修 items wait — they are cheap to apply and the human may
want a different fix, or may be about to restructure the whole area. Applying is cap2, and it exists
as a separate capability because the decision list usually outlives the session that produced it.

If the report contains an unadjudicable group, ask that one question now, while the evidence is in
front of both of you. The answer belongs in the skill afterwards — as a stated principle, which is
the thing whose absence created the group in the first place.
