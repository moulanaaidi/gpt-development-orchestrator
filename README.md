# GPT Development Orchestrator

A thin-root development workflow for Codex.

**Planner decides. Luna builds. Reviewer accepts.**

The workflow keeps expensive root-model activity focused on high-leverage decisions while GPT-6 Luna owns the high-volume implementation loop: repository discovery inside a bounded scope, coding, focused tests, debugging, and routine verification.

It supports two practical ways of working:

- **External-plan path:** create and approve the specification in ChatGPT, then give it to a GPT-6 Luna Codex session. Codex implements directly without recreating the plan.
- **In-Codex path:** a planner/reviewer root plans once, dispatches one coherent bundle to GPT-6 Luna, waits, then reviews the completed diff once.

Trivial edits and read-only questions do not need orchestration.

## Why this exists

The original 0.1 workflow routed every implementation change through planning, worker delegation, and independent review. That maximized process consistency but also created unnecessary root-model activity and context churn.

Version 0.2 changes the optimization target: preserve strong architecture and review while reducing Codex usage.

Normal delegated work should look like:

```text
Planner  -> one planning/contract batch
Luna     -> discover + implement + test + debug + verify
Reviewer -> one batched acceptance review
         -> optional one consolidated correction
```

Do not split a coherent feature into tiny workers, poll a healthy worker, or repeat repository exploration simply for visibility.

## Recommended workflow for limited Codex allowance

Use ChatGPT for planning and independent review, and Codex for implementation:

```text
ChatGPT planner/reviewer model
        |
        v
approved implementation specification
        |
        v
VS Code + Codex GPT-6 Luna
        |
        +-- inspect relevant code
        +-- implement
        +-- targeted tests
        +-- debug/fix
        +-- concise completion report
        |
        v
Git diff / GitHub
        |
        v
ChatGPT planner/reviewer model
        |
        v
review against specification
```

In this path, the expensive planning/review work is outside the Codex implementation loop.

## What the package provides

- A Codex skill for thin-root planning, delegation, and review.
- A native `gpt_luna_builder` role pinned to `gpt-6-luna` at medium reasoning effort.
- Worker instructions optimized for coherent GPT-6 Luna implementation bundles.
- Optional plan/task/checkpoint templates.
- A deterministic JSON plan validator for projects that want a machine-readable contract.
- A preview-first installer with optional scoped global policy integration.
- Backups, receipts, guarded undo, and a read-only doctor.

It never grants permission to commit, push, merge, deploy, change credentials, or perform production operations.

## Requirements

- Python 3.11 or newer for installer/validator utilities.
- A Codex host that supports skills.
- For the in-Codex delegated path: a capable planner/reviewer model, GPT-6 Luna exposed by the host, and native delegation.
- For the external-plan path: a GPT-6 Luna Codex session is enough because planning happened outside Codex.

## Install

Installation targets `CODEX_HOME` when set, otherwise `~/.codex`.

Preview:

```powershell
python install.py
```

Apply the skill and native Luna worker role:

```powershell
python install.py --apply
```

This installs the skill under `$CODEX_HOME/skills/gpt-development-orchestrator/` and the dedicated worker at `$CODEX_HOME/agents/gpt_luna_builder.toml`. It does not change your global default subagent model.

Optionally add the scoped orchestration policy to global `AGENTS.md`:

```powershell
python install.py --with-policy --apply
```

The policy is optional. It now applies thin-root orchestration only to substantial work and explicitly leaves trivial work alone.

## Usage

### External approved spec

Recommended when you want to minimize Codex allowance:

```text
$gpt-development-orchestrator

Implement the approved specification below.
Do not redesign or re-plan it. Own repository discovery within scope,
implementation, targeted tests, debugging, and verification.

SPECIFICATION:
...
```

Run this in a GPT-6 Luna Codex session.

### In-Codex orchestration

When the feature still needs design inside Codex:

```text
$gpt-development-orchestrator plan and execute this substantial feature.
Keep the planner/reviewer root thin: establish the contract once, give one coherent bundle
to GPT-6 Luna, wait for completion, and review the final diff once.
```

## Validation

Validate a machine-readable plan without executing commands inside it:

```powershell
python tools/validate_plan.py examples/valid-plan.json
```

Run the offline test suite:

```powershell
python -m unittest discover -s tests -v
```

## Design principles

1. **Reuse approved decisions.** Do not recreate architecture when a trusted specification already exists.
2. **Coherent worker bundles.** One worker can change many related files and iterate internally.
3. **Worker-owned implementation loop.** Luna handles normal discovery, code, tests, debugging, and verification.
4. **Thin root.** Planning and review happen once per meaningful phase, not continuously.
5. **Batched review.** Specification compliance and engineering quality are two lenses in one review.
6. **One correction by default.** A second cycle is reserved for concrete high-assurance risk.
7. **No silent model fallback.** If the required worker is unavailable, report it.
8. **No unnecessary external effects.** Source-control and production operations still require explicit authorization.

See `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` for the detailed rationale.
