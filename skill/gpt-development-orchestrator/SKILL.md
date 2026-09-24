---
name: gpt-development-orchestrator
description: Require a Sol-authored plan, bounded lower-GPT worker implementation, and independent Sol review for every code or file change, including small tasks. Read-only questions and reviews do not require a worker.
metadata:
  short-description: Require Sol-led planning, implementation, and review for code and file changes
---

# GPT Development Orchestrator

Use this skill for every code or file implementation task, regardless of size or apparent simplicity. Read-only questions and read-only reviews do not need an implementation worker.

Sol is the controller: it orients in the target repository, creates the actual plan, owns design and architecture, defines acceptance, selects available models, integrates changes, and independently reviews every implementation. A lower GPT worker implements only a bounded assignment and returns evidence; workers do not approve or expand their own work. There is no size-based local implementation bypass. If the root agent is not Sol, it must delegate planning and review to Sol without claiming Sol identity.

## Workflow

1. Read applicable repository instructions and inspect the relevant code and worktree.
2. Sol creates an actual, task-specific plan with dependencies, write sets, acceptance criteria, validation, and risks. Read [references/planning.md](references/planning.md).
3. Route every implementation task to a suitable lower GPT worker selected only from the current host's advertised model choices, using native delegation. Never infer or guess a model ID or use an external router. Read [references/routing.md](references/routing.md) and [references/delegation.md](references/delegation.md).
4. Sol independently reviews every worker's actual diff and evidence in two passes: specification compliance, then engineering quality. Read [references/review.md](references/review.md).
5. Integrate, run relevant combined validation, and report verified results. For work spanning sessions, maintain a checkpoint using [references/continuity.md](references/continuity.md).

Use [templates/plan.md](templates/plan.md), [templates/task-brief.md](templates/task-brief.md), and [templates/checkpoint.md](templates/checkpoint.md) when their structure helps; adapt them to the repository's own contracts.

## Non-negotiables

- One active writer per path. Parallelize only independent tasks with disjoint write sets.
- Keep secrets and unnecessary sensitive data out of worker prompts and outputs.
- No automatic commit, push, merge, publish, deploy, credential changes, or production effects. Follow target-repository policy and obtain any required authorization before external or consequential actions.
- If suitable Sol or worker capability, native delegation, or adequate host identity evidence is unavailable, fail closed: do not implement and explain the blocker. Distinguish host-provided invocation evidence from self-reported receipts; receipts alone do not prove model or agent identity.
- Global policy and this skill are strong process guidance, not technical enforcement across all hosts or sessions. A host-level invocation gate is needed for a technical guarantee.
- If scope, a write boundary, or a plan assumption proves wrong, stop that task and return the conflict to Sol.
