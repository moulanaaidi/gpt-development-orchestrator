# Planning

Sol owns the plan. First understand the repository's instructions, architecture, current worktree, and relevant implementation. Do not plan from the request alone when local context can change the answer.

## Plan only what the task needs

- For a contained task, use a short checklist and clear acceptance criteria; do not manufacture phases or paperwork.
- For substantial work, define the intended outcome, in-scope and out-of-scope behavior, interfaces or invariants, dependencies, task owners/models, disjoint write sets, acceptance criteria, validation commands, and material risks. Record why the chosen model is likely to meet the quality floor at reasonable total effort.
- Mark blocked tasks explicitly and do not delegate them until their dependency is resolved.
- State assumptions where evidence is missing. Ask the user only when a material decision cannot be safely inferred.
- Preserve target-repository conventions and policies. This skill does not replace them.
- For visual product work, identify one representative production-quality screen,
  its visual acceptance criteria, and the Sol direction-approval gate before
  scaling. Require user approval only when target-repository policy says so.
- Separate visual acceptance from structural validation. Record observable
  visual qualities and interaction checks alongside, not instead of, behavior,
  accessibility, and automated validation.
- Keep plans concise: link to authoritative repository instructions and design
  sources rather than copying their contents.

Use [../templates/plan.md](../templates/plan.md) as an optional starting point. If the repository has a machine-readable plan contract, use and validate that contract instead of treating the markdown template as authoritative.

## Ready-to-delegate test

A task is ready only when its worker can identify the expected result, permitted paths, relevant interfaces, acceptance checks, and return format without making a product or architecture decision on Sol's behalf. Resolve shared interfaces before dispatching parallel work.
