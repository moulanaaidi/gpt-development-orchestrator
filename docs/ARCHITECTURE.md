# Architecture

## Purpose

GPT Development Orchestrator is a thin-root workflow for substantial software work. It separates high-leverage planning and acceptance from high-volume implementation.

The design target is:

```text
planner/reviewer plans once -> configured worker builds/tests/debugs -> planner/reviewer accepts once
```

When a trusted specification was already produced outside the implementation session, the root can be thinner still:

```text
external approved spec -> suitable implementation model implements directly
```

## Authority

The planner/reviewer owns product and architecture decisions, interfaces, security boundaries, acceptance criteria, and final acceptance.

The implementation worker owns routine repository discovery inside its bounded scope, code changes, focused tests, debugging, and verification. It does not redefine the contract or approve its own work.

## Two execution paths

### External approved specification

Use this when another trusted planning step already produced the implementation contract.

A suitable implementation session:

1. reads the approved specification and repository instructions;
2. inspects only relevant code;
3. implements the coherent bundle;
4. runs targeted tests and debugging;
5. returns one concise completion report.

No in-session planning/review loop is required unless explicitly requested.

### Orchestrated thin-root path

Use this when the feature still needs planning in the active development session.

1. **Orient:** the planner/reviewer reads only enough repository context to settle architecture and contracts.
2. **Specify:** it creates a concise implementation contract.
3. **Dispatch:** one coherent bundle goes to the configured worker.
4. **Wait:** the worker owns implementation, tests, debugging, and routine verification without polling.
5. **Review:** the planner/reviewer inspects the completed diff once using specification and engineering-quality lenses.
6. **Correct if needed:** send one consolidated correction request to the same worker.
7. **Integrate:** perform broader checks only at real integration boundaries.

A second correction cycle is reserved for concrete high-assurance risk.

## Efficiency model

The workflow reduces planner/reviewer activity by avoiding:

- per-task full model benchmarking and cost studies;
- repeated repository discovery by both planner/reviewer and worker;
- tiny worker tasks for each file or function;
- progress polling;
- separate calls for specification and engineering review;
- ritual reruns of the worker's full validation;
- checkpoints after every turn.

The normal delegated shape is one planning batch, one dispatch, one wait, one batched review, and one final response.

## Model policy

The planner/final reviewer is intentionally not pinned to a model name. Use the best suitable available model for the task, risk, and budget, with explicit user/project choices taking precedence. The skill cannot switch the active root model.

Avoid a fresh model-ranking exercise on every task. Re-evaluate only when the task requirements, available models, configured preferences, or host materially change.

The package currently installs `gpt_luna_builder` as its default implementation role. That role is pinned to its configured model and reasoning effort, but the architecture permits a project-approved alternative worker role.

The external-spec path can run directly in any suitable implementation session. The orchestrated path requires a capable planner/reviewer plus a usable implementation path.

## Bundling and ownership

One worker owns one coherent vertical bundle. A bundle may span entity, DTO, service, controller, UI, migrations, and tests when those changes belong to the same stable contract.

Use multiple workers only when work is genuinely independent, write sets are disjoint, and separate workspaces are verified.

## Planning artifacts

Markdown is the normal lightweight format. The existing JSON plan schema and validator remain available for projects that need a machine-readable contract; they are optional and should not become mandatory paperwork.

## Installation

The installer remains preview-first and reversible:

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
- A mandatory external model router.
- Automatic benchmarking on every task.
- Continuous worker polling.
- A mandatory workflow for trivial changes.
- Autonomous source-control or production operations.
