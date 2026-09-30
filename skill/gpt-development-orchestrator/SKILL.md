---
name: gpt-development-orchestrator
description: Token-efficient development workflow. Reuse an approved external specification when one exists; otherwise let a capable planner/reviewer define the contract once, give one coherent implementation bundle to the configured worker, and review the final diff once.
metadata:
  short-description: Plan once, build once, review once
---

# Thin-root orchestration

Use this skill only for substantial multi-file work. Skip trivial edits, read-only questions, and explicitly single-agent tasks.

## Model policy

- Planner/final reviewer: the best suitable available model for the task, risk, and budget. Respect an explicit user or project model choice first; otherwise use the capable model selected by the host/session.
- Implementation worker: use the configured worker role. The bundled default is `gpt_luna_builder`, but the orchestration contract does not depend on a specific planner/reviewer model.

Do not hard-code a planner/reviewer model family or name. A skill cannot switch the active root model; if the current root is unsuitable, report that a capable planner/reviewer must be selected rather than inventing a fixed fallback.

## Fast path: approved external specification

When the user already provides an approved external specification:

1. Treat it as authoritative.
2. If the current session is a suitable implementation model, implement directly without recreating the plan.
3. Prefer a repository path or accessible file reference to the specification instead of pasting it into another prompt.
4. The implementation model owns scoped discovery, implementation, focused tests, debugging, and routine verification.
5. Return one concise completion report.

Do not add an in-session planning or review loop unless the user explicitly asks for one.

## Orchestrated path

When planning is still required:

1. The planner/reviewer defines only the objective, non-goals, contracts, bounded write scope, material risks, acceptance criteria, and focused validation.
2. Dispatch one coherent implementation bundle to the configured worker.
3. Do not poll the worker, request play-by-play updates, or split a vertical feature into tiny worker calls.
4. The worker discovers only the relevant repository area, implements, tests, debugs, and verifies.
5. The planner/reviewer reviews the actual diff once for specification compliance plus engineering/security quality.
6. If needed, send all findings back in one consolidated correction request. Default to one correction cycle.

Normal shape: one planning batch, one dispatch, one wait, one batched review, one final response.

## Token discipline

- Reference authoritative specs, plans, policies, and design files by path; do not duplicate their full text in worker or review prompts.
- Pass deltas, not history. Do not replay prior model transcripts or completed reasoning.
- Worker completion reports must be concise: changed paths/behavior, checks run, deviations, unresolved risks, and blockers only.
- Review the spec reference + actual diff + concise verification evidence. Do not repeat full repository discovery or full test logs unless a concrete failure requires it.
- Use targeted search/open operations; avoid dumping broad directory contents or unrelated files into context.
- Update checkpoints only when work will actually cross sessions.
- One writer owns a path. Parallelize only independent, disjoint work in separate workspaces.

This workflow does not authorize commits, pushes, merges, publishing, deployments, credential changes, production operations, or destructive external actions.
