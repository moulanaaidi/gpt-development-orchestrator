# GPT Development Orchestrator

A token-efficient development workflow for Codex.

**Sol 6.1 plans/reviews. Luna 6 builds.**

| Role | Model | Reasoning |
| --- | --- | --- |
| Planner / reviewer | `gpt-6.1-sol` | Host/session setting |
| Implementation worker | `gpt-6-luna` | Medium |

The design keeps high-cost reasoning at the architecture and acceptance boundaries while GPT-6 Luna owns repository discovery, implementation, tests, debugging, and routine verification.

## v0.3 optimization target

v0.2 reduced model turns. v0.3 also reduces **prompt/context duplication**.

The default rules are:

- reuse approved decisions instead of regenerating them;
- reference specs and repository instructions by path instead of pasting them repeatedly;
- pass task deltas, not conversation history;
- use one coherent worker bundle;
- return concise completion evidence rather than code/log dumps;
- review the actual diff once instead of rediscovering the repository;
- keep checkpoints only for real cross-session continuity.

### Lowest-token path

For limited Codex allowance, do planning/review outside Codex and use Luna only for implementation:

```text
ChatGPT planner/reviewer
        |
        v
approved spec saved in repository
        |
        v
VS Code + Codex GPT-6 Luna
        |
        +-- read spec by path
        +-- inspect only relevant code
        +-- implement + targeted tests + debug
        +-- concise completion report
        |
        v
ChatGPT reviews spec + diff
```

If the approved spec is already available to the Luna session, **you do not need to invoke the orchestration skill just to implement it**. Give Luna the spec path and implementation request directly. This avoids loading planning/review instructions into an implementation-only turn.

Example:

```text
Implement the approved specification at:
docs/workpacks/FEATURE-X.md

Treat it as authoritative. Inspect only relevant repository areas.
Own implementation, focused tests, debugging, and verification.
Return a concise completion report; do not repeat the spec or dump full logs.
```

## In-Codex orchestration

When the feature still needs planning inside Codex, select GPT-6.1 Sol and invoke:

```text
$gpt-development-orchestrator plan and execute this substantial feature.
```

The normal delegated shape is:

```text
Sol  -> one compact contract
Luna -> one coherent implementation bundle
Sol  -> one batched diff review
     -> optional one consolidated correction
```

Do not poll a healthy worker or split a vertical feature into tiny dispatches.

## What the package installs

- the `gpt-development-orchestrator` skill;
- a dedicated `gpt_luna_builder` role pinned to GPT-6 Luna medium;
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
