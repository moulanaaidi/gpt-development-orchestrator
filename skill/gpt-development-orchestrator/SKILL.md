---
name: gpt-development-orchestrator
description: Token-efficient development workflow. Reuse an approved external specification when one exists; otherwise let GPT-6.1 Sol plan once, GPT-6 Luna build one coherent bundle, and Sol review the final diff once.
metadata:
  short-description: Plan once, build once, review once
---

# Thin-root orchestration

Use this skill only for substantial multi-file work. Skip trivial edits, read-only questions, and explicitly single-agent tasks.

## Models

- Planner/final reviewer: GPT-6.1 Sol (`gpt-6.1-sol`).
- Worker: GPT-6 Luna (`gpt-6-luna`) through `gpt_luna_builder`.

A skill cannot switch the active root model. If the required model or delegation path is unavailable, report the blocker instead of silently substituting another model.

## Fast path: approved external specification

When the user already provides an approved external specification:

1. Treat it as authoritative.
2. If the current session is already GPT-6 Luna, implement directly without recreating the plan.
3. Prefer a repository path or accessible file reference to the specification instead of pasting it into another prompt.
4. Luna owns scoped discovery, implementation, focused tests, debugging, and routine verification.
5. Return one concise completion report.

Do not add an in-Codex planning or review loop unless the user explicitly asks for one.

## In-Codex path

When planning is still required:

1. Sol defines only the objective, non-goals, contracts, bounded write scope, material risks, acceptance criteria, and focused validation.
2. Dispatch one coherent implementation bundle to `gpt_luna_builder`.
3. Do not poll the worker, request play-by-play updates, or split a vertical feature into tiny worker calls.
4. Luna discovers only the relevant repository area, implements, tests, debugs, and verifies.
5. Sol reviews the actual diff once for specification compliance plus engineering/security quality.
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
