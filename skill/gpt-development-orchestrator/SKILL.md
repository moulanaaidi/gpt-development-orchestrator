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
2. Sol creates an actual, task-specific plan with dependencies, write sets, acceptance criteria, validation, and risks. For visual product work, the plan identifies one representative production-quality screen and visual acceptance. Read [references/planning.md](references/planning.md).
3. Check host delegation and identity compatibility once per session before implementation. Route every implementation task to a suitable lower GPT worker selected only from the current host's advertised model choices, using native delegation. Verify invocation identity each time; repeat the compatibility check only after a host change or invocation failure. Missing evidence means stop, not repeated retry. Read [references/routing.md](references/routing.md) and [references/delegation.md](references/delegation.md).
4. Sol independently reviews every worker's actual diff and evidence in two passes: specification compliance, then engineering quality. Each task permits one initial implementation and at most two correction cycles. Read [references/review.md](references/review.md).
5. For visual work, Sol approves the representative screen's direction before it is scaled; seek user approval only when required by the target repository. Assess visual acceptance separately from structural validation.
6. Integrate, run relevant combined validation, and report verified results. Keep briefs concise by linking to authoritative context. Record first-pass success, corrections, and host-provided usage only (otherwise usage is unknown). For work spanning sessions, maintain a checkpoint using [references/continuity.md](references/continuity.md).

Use [templates/plan.md](templates/plan.md), [templates/task-brief.md](templates/task-brief.md), and [templates/checkpoint.md](templates/checkpoint.md) when their structure helps; adapt them to the repository's own contracts.

## Non-negotiables

- One active writer per path. Parallelize only independent tasks with disjoint write sets.
- Keep secrets and unnecessary sensitive data out of worker prompts and outputs.
- No automatic commit, push, merge, publish, deploy, credential changes, or production effects. Follow target-repository policy and obtain any required authorization before external or consequential actions.
- Check once per session that a suitable Sol, lower-GPT worker, native delegation, and invocation-identity evidence are available; verify identity on each invocation. Recheck compatibility only after host change or invocation failure. If Sol planning/review, worker, delegation, or identity evidence is unavailable, fail closed: stop and report without implementing or repeatedly retrying unchanged missing evidence. Distinguish host evidence from self-reported receipts.
- Stop after the initial attempt and two correction cycles if acceptance is still unmet. Replanning the same intended outcome does not reset the correction limit.
- For visual product work, get Sol's direction approval on one representative production-quality screen before scaling. Ask the user only if repository policy requires it; visual approval does not replace structural validation.
- Keep worker briefs to task-specific context and links to authoritative repository documents. Do not reproduce entire documents in the brief.
- Record first-pass result, corrections, and usage reported by the host; otherwise record usage as unknown.
- Global policy and this skill are strong process guidance, not technical enforcement across all hosts or sessions. A host-level invocation gate is needed for a technical guarantee.
- If scope, a write boundary, or a plan assumption proves wrong, stop that task and return the conflict to Sol.
