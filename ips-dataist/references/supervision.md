# Supervision And Closure

## A Goal Is A Wrapper, Not Another Workflow

Create a persistent Goal or monitor only when the user requests it, using the
host's supported tools. A short Goal invocation inherits the same run contract,
authorization boundaries, and evidence requirements as direct execution.

Resolve ticket, database, run, code/worktree, owner, and durable checkpoint.
Translate the objective internally into:

```text
final state; approved population/datasets; spending/writing authority
current checkpoint; next unfinished stage; evidence that proves completion
genuine external blockers; explicitly accepted exceptions
```

Keep that in the existing execution record. Do not create parallel plans or a new
ticket per obstacle. Fix ordinary scoped bugs within the authorized ticket;
follow its actual merge/deploy authority. If the task is code-only, a Goal does
not grant production execution.

## Monitor Outcomes, Not Activity

Use compact host progress snapshots first. Inspect recent logs or a small
authoritative query only when they answer a new question. Avoid whole-transcript
reads, repeated full-table counts, huge raw payload scans, and observer load
during a heavy refresh.

Useful signals depend on the stage:

| Stage | Real evidence of progress |
|---|---|
| Dispatch | Accepted task IDs durably recorded, remaining undispatched count |
| Retrieval | New successful result bodies durably saved, not just polling rows |
| Modeling | New committed facts/checkpoints and shrinking replay backlog |
| Publication | Advancing dependency/SQL phase and eventual commit/readback |
| Deployment | Required services reaching the target revision and serving data |

Use measured throughput and supplier queue semantics to choose observation
cadence. Do not wake or direct the worker every minute merely because monitoring
is available. A long query may need activity/wait diagnostics rather than new
rows as its progress evidence.

## Intervene Only When It Changes The Outcome

Concrete reasons include:

- Duplicate collectors or uncertain paid dispatch.
- Raw not being committed while more money is spent.
- Large repeated validation, unnecessary whole-corpus work, or a new framework
  replacing a nearly complete working path.
- Excessive write concurrency, database recovery/OOM, or required page failures.
- Repeating the same failing request without new evidence.
- Stopping at code completion when the authorized objective includes data/live
  delivery, or claiming a result that the store does not contain.

Send one specific correction:

```text
Observed fact -> consequence -> smallest next action -> evidence to finish
```

Then watch the action. Do not issue competing instructions while the previous
one is being implemented. Do not restart a job or replace its worker merely
because another approach looks theoretically faster.

When the user changes the completion bar or says to stop overengineering, update
the worker and saved monitor instruction once. Respect the latest direction;
preserve completed work and data integrity. Minor exceptions can be recorded
under the user's revised scope, never disguised as original full completion.

If replacing/forking a worker is authorized, establish that the previous writer
has stopped or lost ownership before another can dispatch. Resume the same
ledger; do not notify the obsolete session. If asked only to report, do not
send instructions or mutate anything.

Normal progress stays quiet unless periodic reports were requested. Notify on
meaningful completion, a material failure, or an actual decision the user must
make. Do not wake the user for repairable scoped code defects.

## Distinguish Blocked From Inconvenient

Repair local parser, query, configuration, and compatible publication defects
within authority. Continue independent safe work while one provider task waits.
Budget exhaustion, missing credentials/authorization, or a supplier failure with
no remaining safe recovery path can be genuine external blockers.

Report the affected scope, durable checkpoint, attempts/evidence, and the exact
missing input. Do not call repeated internal errors "permanently unsupported"
without evidence. Do not retry indefinitely or mark an unfinished Goal complete
to escape a blocker. Use the host's actual blocked/completed semantics.

## Close Once, With Evidence Already Earned

Perform one proportional completion check, reusing passing evidence for unchanged
parts:

1. The frozen scope is accounted for by successful/reused results, documented
   supported terminal outcomes, or explicitly accepted exceptions. Failed or
   unknown items do not disappear from the denominator.
2. Paid results are durable and linked to requests; actual and uncertain charges
   reconcile with the original cumulative authorization.
3. Required modeling/publication is committed and its actual consumer shows the
   new data. HTTP 200 and a successful build alone do not prove this.
4. If deployment was requested, the intended active services run the compatible
   approved revision. Intentionally retired jobs stay retired.
5. Record the result and real limitations, close the authorized ticket/Goal,
   stop owned temporary processes, and remove the completed monitor.

Do not reread the whole repository, rerun the entire test suite, repeat every
data hash, or generate a new backup after these facts are established merely for
another handoff. Run mandatory project checks at their actual boundary and
target changed risk; do not invent additional gates.
