---
name: gpt-development-orchestrator
description: Token-efficient thin-root workflow for substantial multi-file work. Reuse approved specifications, send one compact implementation bundle to GPT-6 Luna, and review only the resulting delta. Skip trivial work and avoid repeated context.
metadata:
  short-description: Plan once, build once, review the delta once
---

# Thin-root development orchestration

Use this skill only for substantial multi-file features, migrations, refactors, or builds. Trivial edits, read-only questions, and explicitly single-agent tasks bypass it.

## Roles

- Planner/final reviewer: GPT-6.1 Sol (`gpt-6.1-sol`).
- Implementation worker: `gpt_luna_builder`, pinned to GPT-6 Luna (`gpt-6-luna`) at medium reasoning.

A skill cannot switch the active root model. Never silently substitute another model.

## Route

### Approved external specification

An approved external specification is already the plan. Never run another planning pass merely because this skill is active.

- If the active session is GPT-6 Luna, implement directly.
- If a non-Luna root has native access to `gpt_luna_builder`, dispatch exactly one implementation bundle without replanning. Do not add an in-Codex review unless the user requested it.
- If minimizing Codex allowance is the priority, prefer opening the approved specification directly in a GPT-6 Luna session instead of first loading it into a Sol root.
- When the specification is available in the shared workspace, pass its path and relevant section/anchor plus a compact task capsule; do not copy the whole document into the worker prompt.
- If only part of a large specification applies, send only that authoritative slice.

### In-Codex planning

When no approved contract exists:

1. GPT-6.1 Sol inspects only enough repository evidence to settle product/architecture decisions and acceptance.
2. Produce one concise contract and normally one vertical implementation bundle. Read `references/planning.md` only when needed.
3. Dispatch once to `gpt_luna_builder`. Luna owns scoped discovery, implementation, focused tests, debugging, and routine verification. Read `references/delegation.md` only when needed.
4. Wait without polling or overlapping repository exploration.
5. Review the changed delta once using specification-compliance and engineering-quality/security lenses. Read `references/review.md` only when needed.
6. Send all required corrections in one findings-only request to the same worker. A second cycle is only for a concrete unresolved high-assurance risk.

## Context discipline

- Prefer targeted search, file ranges, changed-file lists, and diff hunks over recursive repository inventories or full-file/full-document reads.
- Reuse paths, anchors, and approved artifacts instead of paraphrasing or repasting them.
- Target a worker handoff of at most 500 words, excluding paths and validation commands. Expand only when a contract cannot safely be referenced.
- Successful test evidence is command + result summary; do not paste routine logs.
- Worker completion reports should stay at or below 250 words unless blocked or a material risk needs explanation.
- Review starts from changed-file names/statistics and relevant hunks; open full files or neighboring code only for a concrete dependency or risk.
- Correction requests contain only new findings/deltas. Do not resend unchanged specification text.
- Do not repeat repository discovery, full validation, model checks, or unchanged instructions without a concrete reason.
- Update continuity state only for cross-session work.

## Normal shape

One contract -> one dispatch -> one wait -> one delta review -> optional one correction -> one final response.

The workflow does not authorize commits, pushes, merges, publishing, deployments, credential changes, production operations, or destructive external actions. Repository policy and explicit user authorization remain authoritative.
