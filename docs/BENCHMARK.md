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

## Runtime benchmark protocol

A runtime claim should be published only after comparable real tasks have been
captured. For each benchmark pair, hold the task, repository baseline, acceptance
criteria, planner/reviewer model and effort, worker model and effort, and host
configuration as constant as practical.

Capture from actual session/provider usage records:

- root/planner input, cached input, output and reasoning tokens when exposed;
- worker input, cached input, output and reasoning tokens when exposed;
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
- Preserve raw benchmark evidence privately when it contains repository/session
  details; publish only the aggregate values needed to reproduce the claim.

## Current evidence status

**Measured:** static core context surface, 9,917 -> 7,025 characters (-29.2%).

**Not yet measured:** real-task token, allowance, latency, or monetary savings for
v0.3 versus the baseline.

The README must continue to describe these categories separately until runtime
evidence exists.
