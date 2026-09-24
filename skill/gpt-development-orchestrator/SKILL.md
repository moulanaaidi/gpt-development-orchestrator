---
name: gpt-development-orchestrator
description: Plan and coordinate substantial software work in Codex using a Sol-led plan, bounded GPT worker implementation, and independent review. Do not use for small, self-contained changes.
metadata:
  short-description: Plan, delegate, and review substantial Codex work
---

# GPT Development Orchestrator

Use this skill for work whose risk, scope, or parallelism benefits from explicit planning and independent implementation review. Handle small, clear, low-risk tasks directly without ceremony.

Sol is the controller: it orients in the target repository, owns design and architecture, defines acceptance, selects available models, integrates changes, and performs final review. Workers implement only bounded assignments and return evidence; they do not approve or expand their own work.

## Workflow

1. Read applicable repository instructions and inspect the relevant code and worktree.
2. Sol creates an actionable plan with dependencies, write sets, acceptance criteria, validation, and risks. Read [references/planning.md](references/planning.md).
3. Route only ready tasks using the models and delegation capabilities actually exposed by the host. Read [references/routing.md](references/routing.md) and [references/delegation.md](references/delegation.md) when delegating.
4. Review every worker's actual diff and evidence in two passes: specification compliance, then engineering quality. Read [references/review.md](references/review.md).
5. Integrate, run relevant combined validation, and report verified results. For work spanning sessions, maintain a checkpoint using [references/continuity.md](references/continuity.md).

Use [templates/plan.md](templates/plan.md), [templates/task-brief.md](templates/task-brief.md), and [templates/checkpoint.md](templates/checkpoint.md) when their structure helps; adapt them to the repository's own contracts.

## Non-negotiables

- One active writer per path. Parallelize only independent tasks with disjoint write sets.
- Keep secrets and unnecessary sensitive data out of worker prompts and outputs.
- No automatic commit, push, merge, publish, deploy, credential changes, or production effects. Follow target-repository policy and obtain any required authorization before external or consequential actions.
- If scope, a write boundary, or a plan assumption proves wrong, stop that task and return the conflict to Sol.
