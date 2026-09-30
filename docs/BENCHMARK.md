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

## Runtime benchmark protocol

A runtime claim should be published only after comparable real tasks have been
captured. For each benchmark pair, hold the task, repository baseline, acceptance
criteria, planner/reviewer model and effort, worker model and effort, and host
configuration as constant as practical.

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

Recommended normalized metrics:

- planner/reviewer input per 1,000 accepted implementation/test lines;
- worker input per 1,000 accepted implementation/test lines;
- total reported tokens per 1,000 accepted implementation/test lines;
- root turns per accepted workpack;
- correction cycles per accepted workpack.

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
- Treat worker usage as required for aggregate orchestrated token/cost claims.
- Require both candidates to pass the same independent acceptance gate before
  including the pair in an equal-quality efficiency aggregate.
- Preserve implementation-session validation summaries so an independent
  reviewer can inspect required pass/fail/skip evidence without rerunning broad
  tests.
- Preserve raw benchmark evidence privately when it contains repository/session
  details; publish only the aggregate values needed to reproduce the claim.

## Current evidence status

**Measured:** static core context surface, 9,917 -> 7,025 characters (-29.2%).

**Preliminary runtime evidence:** one controlled task measured a 68.4% reduction
in root input tokens, but worker usage was unavailable and the orchestrated
candidate failed independent correctness acceptance. This is root-workload
evidence, not an overall efficiency claim.

**Not yet established:** equal-quality total-token, allowance, or monetary
savings for v0.3 versus direct development.

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
