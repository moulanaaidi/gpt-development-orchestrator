# Benchmark methodology

This document separates two different questions:

1. **Static context efficiency:** how much orchestration instruction text the
   package carries on its core hot path.
2. **Runtime efficiency:** how many real model tokens/turns/correction cycles are
   consumed to deliver accepted implementation work.

The first is measured now and is fully reproducible from Git. The second requires
comparable Codex session usage records and must not be inferred from prompt size.

## Static context-surface result

Baseline commit:

`909500bc8cf67b8b78fb6a90645ccea288772c30`

Candidate:

current token-budget v0.3 branch / `HEAD`.

| Surface | Path | Baseline chars | v0.3 chars | Reduction |
| --- | --- | ---: | ---: | ---: |
| Root skill | `skill/gpt-development-orchestrator/SKILL.md` | 4,428 | 3,620 | 18.2% |
| Optional global policy | `POLICY.md` | 2,877 | 1,570 | 45.4% |
| Bundled worker role | `skill/gpt-development-orchestrator/agents/gpt_luna_builder.toml` | 1,512 | 1,165 | 22.9% |
| Task brief template | `skill/gpt-development-orchestrator/templates/task-brief.md` | 1,100 | 670 | 39.1% |
| **Core hot-path total** | — | **9,917** | **7,025** | **29.2%** |

The total is the sum of the four exact UTF-8 text files above. The global policy
is optional at install time; the table intentionally shows the full-policy
surface so the comparison is conservative and easy to reproduce.

The broader reference library is not included in the headline number because
references are read selectively rather than injected into every task. Including
selective references would mix hot-path and cold-path context.

## Reproduce

From a Git checkout containing the baseline commit:

```powershell
python tools/measure_context.py --base-ref 909500bc8cf67b8b78fb6a90645ccea288772c30 --head-ref HEAD
```

The script reads the exact files from each Git ref using `git show`, reports
character counts, and calculates the reduction. It makes no model/API calls.

To measure only the current working tree:

```powershell
python tools/measure_context.py
```

## What this proves

The static benchmark proves that v0.3 carries materially less core orchestration
text than the selected pre-v0.3 baseline while preserving the workflow contract
tests.

It does **not** prove an equal reduction in:

- billed input tokens;
- cached/uncached token usage;
- output/reasoning tokens;
- wall-clock time;
- subscription allowance consumption;
- total task cost.

Those depend on tokenizer behavior, host/system context, repository state,
model/effort, task mix, cache behavior, worker output, and correction cycles.

## Preliminary runtime evidence — Benchmark #1

A controlled BawaGo benchmark was run on 2026-09-30 from baseline commit
`cf82df95a9369e5f627b4de275e91b56f991505c` using the same root model and
reasoning effort in both treatments: GPT-6 Sol, medium reasoning.

The task was a multi-file booking custody/state-transition guard with real
PostgreSQL 16.4 validation.

| Metric | Direct | Orchestrated root | Change |
| --- | ---: | ---: | ---: |
| Root input tokens | 2,458,445 | 776,348 | **-68.4%** |
| Cached root input | 2,356,352 | 727,040 | **-69.1%** |
| Root output tokens | 15,522 | 5,985 | **-61.4%** |
| Root reasoning output | 3,767 | 2,555 | **-32.2%** |
| Root command executions | 37 | 21 | **-43.2%** |
| Elapsed seconds | 907.594 | 1,031.953 | **+13.7%** |
| Final PostgreSQL tests | 18 pass | 17 pass | — |

What this supports: the orchestrated treatment materially reduced the amount of
root/planner context and root-side tool work for this task.

What it does **not** support:

- delegated worker token usage was not captured, so total orchestrated input,
  total reported tokens, and API-equivalent cost remain unknown;
- the orchestrated candidate failed the independent correctness acceptance gate
  on a stale same-state concurrency case even though its implementation session
  reported success;
- therefore this run cannot be used as evidence of equal-quality overall token
  or cost efficiency.

The direct candidate's independent code review passed the substantive custody
criteria; its initial review lacked inspectable full-suite execution evidence,
which was later supplied by a clean PostgreSQL 16.4 run with 18 passing tests.
The orchestrated candidate's final suite passed 17 tests, but passing tests did
not establish the missing same-state concurrency invariant.

Benchmark #1 is retained as useful evidence of **root-workload reduction** and as
a regression case for the acceptance-review contract. It is excluded from any
equal-quality aggregate efficiency claim.

## Forced-delegation diagnostic — Benchmark #2

Benchmark #2 was run on 2026-09-30 against this repository from baseline
`bc45196a906aebc00fbe816a58dea95fbd4f8919`. The installed orchestrator source
was `5dd287475feed7befa6c75f58ef155fc99ac3e7a`.

The task added a stable JSON output mode to `tools/validate_plan.py` while
preserving the existing text CLI. Both treatments used GPT-6 Sol, medium
reasoning. The delegated treatment used the configured GPT-6 Luna, medium worker.

| Metric | Direct | Forced delegated | Change |
| --- | ---: | ---: | ---: |
| Root input tokens | 335,785 | 242,653 | **-27.7%** |
| Root cached input | 305,024 | 192,768 | — |
| Root output tokens | 4,152 | 2,504 | — |
| Root reasoning output | 838 | 571 | — |
| Worker input tokens | N/A | 463,233 | — |
| Worker cached input | N/A | 425,216 | — |
| Worker output tokens | N/A | 3,847 | — |
| Worker reasoning output | N/A | 452 | — |
| Aggregate input tokens | 335,785 | 705,886 | **+110.2%** |
| Aggregate reported tokens | 339,937 | 712,237 | **+109.5%** |
| Independent acceptance | PASS | **FAIL** | not comparable |

The delegated candidate normalized the plan argument through `Path`, so on
Windows the JSON `plan` value changed separators instead of preserving the exact
argument string required by criterion 1. The direct candidate preserved the
literal argument and passed independent acceptance.

This benchmark is classified as a **forced-delegation diagnostic**, not a policy
benchmark. The task already had an approved, bounded specification and a suitable
active implementation model. The orchestrator's documented external-spec fast
path would normally choose direct implementation for that shape. The benchmark
prompt intentionally forced Sol -> worker -> Sol to measure delegation overhead,
so its +110.2% aggregate input result must not be presented as the overhead of the
normal routing policy.

The result is still useful: it demonstrates that delegation can be a net loss on
bounded work and that reducing root tokens alone is not an efficiency objective.
It also adds an acceptance-review regression case for exact literal/round-trip
requirements.

## Policy benchmark — Benchmark #3

Benchmark #3 was run on 2026-09-30 against BawaGo from baseline
`c6050875110f5a597ab0c6a216a57254ba267b9a`. Both root sessions used GPT-6 Sol,
medium reasoning. The task hardened the shared environment-file parser and
`configctl validate-env` behavior under a bounded approved workpack.

The orchestrator was allowed to apply its real routing policy. It selected the
**direct** path because the task had an approved bounded specification and a
suitable active implementation model. No worker was dispatched.

| Metric | Plain direct | Policy-selected direct | Change |
| --- | ---: | ---: | ---: |
| Root input tokens | 692,851 | 927,432 | **+33.9%** |
| Root cached input | 647,424 | 892,416 | — |
| Root output tokens | 10,072 | 12,088 | — |
| Root reasoning output | 1,390 | 1,938 | — |
| Aggregate reported tokens | 702,923 | 939,520 | **+33.7%** |
| Root tool calls | 21 | 25 | — |
| Elapsed seconds | 548.614 | 675.758 | **+23.2%** |
| Tests reported | 23 pass | 24 pass | — |
| Independent acceptance | **FAIL** | **PASS** | not equal quality |

The plain-direct candidate failed criterion 2 because its unquoted inline-comment
parser recognized only ASCII space/tab before `#`; a vertical-tab whitespace
boundary was missed. Its tests remained green. The policy-selected direct
candidate handled the broader whitespace contract and passed all six independent
acceptance criteria.

This benchmark does not show raw token savings: policy execution used more
root context and more elapsed time. It does show why runtime evaluation must use
**accepted-work efficiency** rather than raw token count alone. The cheaper
candidate produced rejected work; the higher-usage candidate produced accepted
work.

Because both candidates did not pass the same acceptance gate, Benchmark #3 is
not eligible for an equal-quality token-efficiency percentage. It is evidence
that the policy selected the correct direct route and that additional
specification/verification discipline can improve first-pass correctness.

## Policy benchmark — Benchmark #4

Benchmark #4 used BawaGo from baseline
`c6050875110f5a597ab0c6a216a57254ba267b9a` with GPT-6 Sol, medium reasoning,
for both roots. It selected a substantially larger workpack where delegation had
a realistic opportunity to amortize implementation discovery.

The installed policy still selected **direct** because the approved-spec fast
path was written as an unconditional direct rule. Both candidates failed blinded
independent acceptance, so neither produced accepted work.

| Metric | Plain direct | Policy-selected direct | Change |
| --- | ---: | ---: | ---: |
| Root input tokens | 2,839,888 | 4,689,792 | **+65.1%** |
| Root cached input | 2,770,560 | 4,583,808 | — |
| Root output tokens | 20,670 | 23,481 | — |
| Root reasoning output | 3,666 | 5,101 | — |
| Aggregate reported tokens | 2,860,558 | 4,713,273 | **+64.8%** |
| Root tool calls | 50 | 67 | — |
| Elapsed seconds | 635.448 | 707.005 | **+11.3%** |
| Tests reported | 9 pass | 10 pass | — |
| Independent acceptance | **FAIL** | **FAIL** | not comparable |

Benchmark #4 exposed a routing-precedence defect: accepted-work guidance already
said sufficiently large implementation could delegate, while the external-spec
fast path still said an approved spec should always implement directly. An
approved specification should remove replanning, not decide the implementer.

This run does not establish that delegation would have passed or been cheaper;
no worker was dispatched. It establishes only that the prior policy prevented a
meaningful delegation decision on this task shape. Both failed candidates retain
their raw usage and zero accepted work.

## Routing-fix regression — Benchmark #5

Benchmark #5 reused the Benchmark #4 task byte-for-byte (SHA-256
`af1c2bd18123c685f35ea0f9fd7b435b4eec009b3a04d820c2f0a5c64f4002c7`) on the
same BawaGo baseline. The corrected policy selected **delegated**, proving the
approved-spec routing-precedence fix was exercised.

| Metric | Plain direct | Policy delegated | Change |
| --- | ---: | ---: | ---: |
| Root input tokens | 3,580,330 | 1,072,136 | **-70.1%** |
| Worker input tokens | N/A | 8,644,295 | — |
| Aggregate input tokens | 3,580,330 | 9,716,431 | **+171.4%** |
| Aggregate reported tokens | 3,602,544 | 9,757,097 | **+170.8%** |
| Elapsed seconds | 623.857 | 1,139.856 | **+82.7%** |
| Root tool calls | 55 | 32 | — |
| Worker tool calls | N/A | 102 | — |
| Correction cycles | 0 | 2 | protocol deviation |
| Independent acceptance | **FAIL** | **FAIL** | zero accepted work |

The routing fix worked mechanically and reduced root input substantially, but
delegation did not improve accepted-work efficiency. The worker consumed 8.64M
input tokens across 105 model responses / 102 exec calls, and the policy exceeded
the one-correction target.

Blinded review showed a shared correctness pattern rather than a Luna-only
failure: both candidates missed existing risk-clarification writes that could
bypass the new case lifecycle rules. The delegated candidate preserved exact
resolution/reopen values better; the direct candidate provided better typed
transition errors. This motivates mutation-surface auditing across all writers of
a protected state, plus tighter worker context/debug-loop discipline.

## Runtime benchmark protocol

A runtime claim should be published only after comparable real tasks have been
captured.

Separate two experiment types:

1. **Policy benchmark:** compare direct development with the orchestrator allowed
   to apply its real routing policy. If an approved bounded spec should take the
   direct fast path, that is a valid orchestrator outcome; do not force a worker
   merely to create a delegated treatment.
2. **Forced-delegation diagnostic:** deliberately require planner -> worker ->
   reviewer to measure delegation overhead or worker behavior. Report this as a
   diagnostic and do not generalize it to the normal policy.

For each benchmark pair, hold the task, repository baseline, acceptance criteria,
root model and effort, host configuration, and validation requirements constant
as practical. When delegation occurs, also record the worker model and effort.

Capture from actual session/provider usage records:

- root/planner input, cached input, output and reasoning tokens when exposed;
- worker input, cached input, output and reasoning tokens when exposed. Capture
  these from the host-level delegation record or a separate worker-session
  usage artifact; do not infer them from prose, elapsed time, or prompt length;
- number of root turns;
- number of worker dispatches;
- number of correction cycles;
- accepted implementation/test lines or another declared work unit;
- validation outcome and final acceptance status.

## Accepted-work efficiency

The primary runtime question is not "which treatment used fewer tokens?" but
"what resources were required to produce independently accepted work?"

Raw token and elapsed-time comparisons remain important, but a lower-usage
candidate that fails acceptance must not be presented as more efficient delivery.

Track, where evidence permits:

- first-pass independent acceptance (PASS/FAIL);
- accepted tasks / attempted tasks;
- total reported tokens per accepted task;
- total reported tokens per 1,000 accepted implementation/test lines;
- planner/reviewer input per 1,000 accepted implementation/test lines;
- worker input per 1,000 accepted implementation/test lines;
- root turns per accepted workpack;
- correction cycles per accepted workpack;
- elapsed time per accepted task.

When a candidate fails acceptance, its accepted implementation/test lines are
zero for normalization purposes. Do not divide by zero or manufacture an
"efficiency" ratio; report the failed outcome and raw resource usage instead.

Recommended normalized metrics should be aggregated only across task pairs that
meet the declared quality-comparability rule.

If pricing is used, record the exact dated rate source and distinguish API-equivalent
estimates from ChatGPT/Codex subscription usage. Do not convert missing usage into
zero and do not estimate savings from task duration or number of files alone.

## Fair-comparison rules

- Use restorable Git baselines.
- Exclude generated/vendor artifacts from line-based work units.
- Do not compare one research-heavy phase with one code-heavy phase without
  clearly disclosing the task-mix difference.
- Count failed/corrective runs in the workflow that caused them.
- Report unmeasured fields as unknown.
- Treat worker usage as required for aggregate delegated token/cost claims.
- Label policy benchmarks and forced-delegation diagnostics separately.
- Do not force delegation for an approved bounded spec when the routing policy
  would normally implement it directly.
- Require both candidates to pass the same independent acceptance gate before
  including the pair in an equal-quality efficiency aggregate.
- Preserve implementation-session validation summaries so an independent
  reviewer can inspect required pass/fail/skip evidence without rerunning broad
  tests.
- Preserve raw benchmark evidence privately when it contains repository/session
  details; publish only the aggregate values needed to reproduce the claim.

## Current evidence status

**Measured:** static core context surface, 9,917 -> 7,025 characters (-29.2%).

**Preliminary runtime evidence:** Benchmark #1 measured a 68.4% reduction in root
input tokens, but worker usage was unavailable and the orchestrated candidate
failed independent correctness acceptance. This is root-workload evidence, not
an overall efficiency claim.

**Forced-delegation evidence:** Benchmark #2 reduced root input by 27.7% but
increased aggregate input by 110.2%, increased aggregate reported tokens by
109.5%, and failed independent acceptance. Because the task qualified for the
documented direct external-spec path, this diagnoses delegation overhead rather
than the normal routing policy.

**Policy evidence:** Benchmark #3 allowed the real routing policy to choose its
route. It selected direct implementation, used 33.9% more input than the plain
direct baseline, and passed independent acceptance while the lower-usage baseline
failed a whitespace-parsing criterion. This supports accepted-work evaluation,
not a token-savings claim.

**Routing regression evidence:** Benchmark #4 selected direct on a substantially
larger approved workpack because the external-spec rule overrode the size-aware
routing rule. Both candidates failed; policy input was 65.1% higher. Delegation
benefit remains untested for that workpack.

**Routing-fix evidence:** Benchmark #5 changed the same-task policy route from
direct to delegated and cut root input 70.1%, but aggregate input rose 171.4% and
both candidates failed. The routing precedence fix worked; worker/reviewer
accepted-work efficiency remains unproven.

**Not yet established:** equal-quality total-token, allowance, or monetary
savings for the orchestrator's real routing policy versus direct development.

Use `tools/summarize_runtime_benchmark.py` to aggregate root/worker usage without
turning missing telemetry into zero. Example:

```powershell
python tools/summarize_runtime_benchmark.py \
  --direct-root direct-run.json \
  --orchestrated-root orchestrated-run.json \
  --orchestrated-worker orchestrated-worker-run.json \
  --direct-acceptance pass \
  --orchestrated-acceptance pass
```

If the host does not expose worker usage, omit `--orchestrated-worker`; aggregate
orchestrated usage and equal-quality efficiency eligibility will remain unknown/
false rather than being silently undercounted.

The README must continue to describe these categories separately until runtime
evidence exists.
