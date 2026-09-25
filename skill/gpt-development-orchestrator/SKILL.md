---
name: gpt-development-orchestrator
description: Thin-root development workflow for substantial multi-file work. Reuse an approved external specification when one exists; otherwise let a planner/reviewer root define the contract once, then give one coherent implementation bundle to GPT-6 Luna and review the completed patch once. Skip trivial edits and explicitly single-agent tasks.
metadata:
  short-description: Planner plans once, Luna builds, Reviewer accepts once
---

# Planner decides. Luna builds. Reviewer accepts.

Use this skill for substantial multi-file features, migrations, refactors, or builds. Do not force it onto trivial edits, read-only questions, or explicitly single-agent tasks.

The goal is to minimize expensive root-model activity while preserving strong planning and independent acceptance.

## Choose the path

### A. Approved external specification

If the user provides an approved implementation specification from ChatGPT or another trusted planning step:

1. Treat that specification as authoritative.
2. If the active Codex session is already GPT-6 Luna, implement directly without recreating the plan.
3. Inspect only the repository areas needed to satisfy the specification.
4. Own implementation, focused testing, debugging, and routine verification in one coherent run.
5. Return one concise completion report.

Do not add an in-Codex planning or review loop unless the user asks for it.

### B. In-Codex thin-root orchestration

If the task still needs planning inside Codex:

1. A planner/reviewer root establishes the objective, boundaries, contracts, acceptance criteria, material risks, and a dependency-ordered implementation bundle. Reuse any existing approved design instead of writing a competing one. Read references/planning.md only when planning detail is needed.
2. Route the implementation bundle through the installed native `gpt_luna_builder` role, pinned to GPT-6 Luna. Do not perform dynamic per-task model ranking or cost analysis. Read references/routing.md only when routing must be verified.
3. Give Luna one coherent end-to-end bundle. Let it own in-scope repository discovery, implementation, tests, debugging, and routine verification. Do not poll a healthy worker or duplicate its repository work. Read references/delegation.md when preparing the brief.
4. After Luna completes, the reviewer checks the actual diff and evidence once using two lenses in one batch: specification compliance and engineering quality/security. Read references/review.md when performing acceptance.
5. If corrections are needed, send all concrete findings to the same worker in one request. Default to one correction cycle. Expand only for a concrete high-assurance risk.
6. Run cross-task validation only at genuine integration boundaries and update continuity state only when work will span sessions.

## Efficiency rules

- One planning batch, one dispatch, one wait, one batched review, one final response is the normal shape.
- Do not split a coherent feature into tiny worker calls for progress visibility.
- Do not poll workers or ask for routine intermediate summaries.
- Do not repeat repository discovery already owned by the worker.
- Do not rerun the worker's full validation without a concrete reason.
- Keep worker briefs task-specific and link to authoritative repository material instead of copying large documents.
- Use one writer by default. Parallelize only independent work with disjoint write sets and verified separate workspaces.
- Check worker availability once per session or after an actual invocation failure; do not repeatedly probe unchanged configuration.

## Safety boundaries

The workflow does not authorize commits, pushes, merges, publishing, deployments, credential changes, production operations, or destructive external actions. Follow repository policy and explicit user authorization.
