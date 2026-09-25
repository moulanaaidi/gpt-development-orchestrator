# Architecture

## Purpose

GPT Development Orchestrator v0.2 is a thin-root workflow for substantial software work. It separates high-leverage planning and acceptance from high-volume implementation.

The design target is simple:

```text
Planner plans once -> GPT-6 Luna builds/tests/debugs -> Reviewer accepts once
```

When a trusted specification was already produced outside Codex, the root can be thinner still:

```text
external approved spec -> GPT-6 Luna implements directly
```

## Authority

The planner/reviewer owns product and architecture decisions, interfaces, security boundaries, acceptance criteria, and final acceptance.

The implementation worker owns routine repository discovery inside its bounded scope, code changes, focused tests, debugging, and verification. It does not redefine the contract or approve its own work.

## Two execution paths

### External approved specification

Use this when ChatGPT or another trusted planning step already produced the implementation contract.

A GPT-6 Luna Codex session:

1. reads the approved specification and repository instructions;
2. inspects only relevant code;
3. implements the coherent bundle;
4. runs targeted tests and debugging;
5. returns one completion report.

No in-Codex planner/reviewer planning/review loop is required unless explicitly requested.

### In-Codex thin-root orchestration

Use this when the feature still needs planning inside Codex.

1. **Orient:** the planner reads only enough repository context to settle architecture and contracts.
2. **Specify:** the planner creates a concise implementation contract.
3. **Dispatch:** one coherent bundle goes to GPT-6 Luna.
4. **Wait:** Luna owns implementation, tests, debugging, and routine verification without polling.
5. **Review:** the reviewer inspects the completed diff once using specification and engineering-quality lenses.
6. **Correct if needed:** send one consolidated correction request to the same worker.
7. **Integrate:** perform broader checks only at real integration boundaries.

A second correction cycle is reserved for concrete high-assurance risk.

## Efficiency model

The workflow reduces root activity by avoiding:

- per-task model ranking and cost analysis;
- repeated repository discovery by both root and worker;
- tiny worker tasks for each file or function;
- progress polling;
- separate root calls for specification and engineering review;
- ritual reruns of the worker's full validation;
- checkpoints after every turn.

The normal delegated shape is one planning batch, one dispatch, one wait, one batched review, and one final response.

## Worker model

GPT-6 Luna is the default implementation worker. Installation creates a dedicated native `gpt_luna_builder` role pinned to `gpt-6-luna` with medium reasoning effort. The package does not change the global default subagent model and no longer tries to determine a globally optimal model for each task.

If Luna is unavailable, report the blocker rather than silently falling back.

The external-spec path can run directly in a Luna root session. The in-Codex path requires native delegation from the planner/reviewer to Luna.

## Bundling and ownership

One worker owns one coherent vertical bundle. A bundle may span entity, DTO, service, controller, UI, migrations, and tests when those changes belong to the same stable contract.

Use multiple workers only when work is genuinely independent, write sets are disjoint, and separate workspaces are verified.

## Planning artifacts

Markdown is the normal lightweight format. The existing JSON plan schema and validator remain available for projects that need a machine-readable contract; they are optional and should not become mandatory paperwork.

## Installation

The existing installer remains preview-first and reversible:

- skill installation is atomic;
- global `AGENTS.md` policy integration is opt-in;
- existing content is preserved outside owned markers;
- backups and receipts support guarded undo;
- doctor is read-only.

## Safety boundaries

The workflow does not authorize:

- commit, push, merge, or publication;
- deployment or production mutation;
- credential creation or rotation;
- destructive migrations;
- broadening the worker's approved scope.

Repository policy and explicit user authorization remain authoritative.

## Non-goals

- A hosted orchestration service.
- An external model router.
- Automatic model benchmarking.
- Continuous worker polling.
- A mandatory workflow for trivial changes.
- Autonomous source-control or production operations.
