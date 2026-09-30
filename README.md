# GPT Development Orchestrator

A token-efficient development workflow for Codex.

**A capable planner/reviewer plans once. A configured worker builds. The planner/reviewer accepts once.**

| Role | Model policy |
| --- | --- |
| Planner / reviewer | Best suitable available model for task, risk, and budget; explicit user/project choice wins |
| Implementation worker | Configured worker role; bundled default is `gpt_luna_builder` |

The workflow keeps high-cost reasoning at architecture and acceptance boundaries while the implementation worker owns repository discovery, implementation, tests, debugging, and routine verification.

## Measured context efficiency

v0.3 has a reproducible **static context-surface** benchmark against the pre-v0.3
baseline commit `909500bc8cf67b8b78fb6a90645ccea288772c30`.

| Core orchestration surface | Pre-v0.3 | v0.3 | Reduction |
| --- | ---: | ---: | ---: |
| Root skill | 4,428 chars | 3,620 chars | 18.2% |
| Optional global policy | 2,877 chars | 1,570 chars | 45.4% |
| Bundled worker role | 1,512 chars | 1,165 chars | 22.9% |
| Task brief template | 1,100 chars | 670 chars | 39.1% |
| **Core hot-path total** | **9,917 chars** | **7,025 chars** | **29.2%** |

This measures the exact repository instruction text that forms the core
planner/policy/worker/task-brief surface. It is a deterministic proxy for prompt
bloat, **not** a claim that every task uses 29.2% fewer billed tokens or costs
29.2% less. Tokenization, caching, host-added context, repository size, task mix,
model choice, and correction cycles all affect real usage.

Reproduce the comparison from a Git checkout:

```powershell
python tools/measure_context.py --base-ref 909500bc8cf67b8b78fb6a90645ccea288772c30 --head-ref HEAD
```

See [benchmark methodology](docs/BENCHMARK.md) for the exact files, limitations,
and the runtime measurement protocol we will use for real Codex task comparisons.

## v0.3 optimization target

v0.2 reduced model turns. v0.3 also reduces **prompt/context duplication** and removes planner/reviewer model pinning.

The default rules are:

- reuse approved decisions instead of regenerating them;
- reference specs and repository instructions by path instead of pasting them repeatedly;
- pass task deltas, not conversation history;
- use one coherent worker bundle;
- return concise completion evidence rather than code/log dumps;
- review the actual diff once instead of rediscovering the repository;
- keep checkpoints only for real cross-session continuity;
- never bake one planner/reviewer model name into the workflow.

### Lowest-token path

For limited implementation allowance, do planning/review outside the implementation session and use a suitable worker only for implementation:

```text
capable external planner/reviewer
        |
        v
approved spec saved in repository
        |
        v
implementation session
        |
        +-- read spec by path
        +-- inspect only relevant code
        +-- implement + targeted tests + debug
        +-- concise completion report
        |
        v
planner/reviewer checks spec + diff
```

If the approved spec is already available to a suitable implementation session, **you do not need to invoke the orchestration skill just to implement it**. Give the implementation model the spec path and request directly.

Example:

```text
Implement the approved specification at:
docs/workpacks/FEATURE-X.md

Treat it as authoritative. Inspect only relevant repository areas.
Own implementation, focused tests, debugging, and verification.
Return a concise completion report; do not repeat the spec or dump full logs.
```

## Orchestrated path

When the feature still needs planning in the active development session, select a capable planner/reviewer model appropriate to the task and invoke:

```text
$gpt-development-orchestrator plan and execute this substantial feature.
```

The normal delegated shape is:

```text
planner/reviewer -> one compact contract
worker           -> one coherent implementation bundle
planner/reviewer -> one batched diff review
                  -> optional one consolidated correction
```

Do not poll a healthy worker or split a vertical feature into tiny dispatches.

## Model selection

The skill intentionally does not name a mandatory planner/reviewer model.

Selection precedence:

1. explicit user choice;
2. project-configured choice;
3. capable model already selected by the host/session;
4. if the active model is unsuitable, select another capable available model outside the skill.

Avoid a fresh benchmark, pricing study, or full model-registry scan on every task. Re-evaluate only when requirements, available models, or the host materially change.

The bundled implementation role is currently `gpt_luna_builder`, but that is a package default rather than an architectural requirement.

## What the package installs

- the `gpt-development-orchestrator` skill;
- a bundled `gpt_luna_builder` implementation role;
- compact planning/delegation/review references and templates;
- an optional global policy;
- installer, doctor, guarded undo, and JSON plan validation utilities.

Installation never changes the global default root or default subagent model.

## Install

Preview:

```powershell
python install.py
```

Apply:

```powershell
python install.py --apply
```

Optional global policy:

```powershell
python install.py --with-policy --apply
```

Use the global policy only when you want orchestration guidance automatically present in every Codex session. Leaving it out saves persistent context tokens.

## Validation

```powershell
python tools/validate_plan.py examples/valid-plan.json
python -m unittest discover -s tests -v
```

## Safety

The workflow does not grant permission to commit, push, merge, publish, deploy, change credentials, mutate production systems, or perform destructive external actions.
