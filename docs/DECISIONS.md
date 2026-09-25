# Architecture Decisions

## ADR-001: Product-neutral workflow

The orchestrator contains no product-specific governance. Each target repository owns its business rules, approvals, and deployment policy.

## ADR-002: Thin-root orchestration

**Decision:** For substantial in-Codex work, a Sol-class root establishes the contract once, GPT-6 Luna owns the coherent implementation loop, and Sol performs one batched acceptance review.

**Reason:** Root-model tokens have the highest value on architecture, contracts, risk, and acceptance. Repository exploration, implementation, testing, and debugging are high-volume activities that should remain with the cheaper worker.

## ADR-003: External specifications may bypass in-Codex planning

**Decision:** When the user provides an approved external specification and the active Codex session is GPT-6 Luna, the worker implements directly. It does not recreate the plan or require a Sol subagent.

**Reason:** This is the lowest-overhead path when ChatGPT already performed the expensive reasoning. Replanning inside Codex duplicates work and consumes the allowance the workflow is meant to preserve.

## ADR-004: GPT-6 Luna is the default implementation worker

**Decision:** Version 0.2 defaults to GPT-6 Luna rather than dynamically ranking workers for every task.

**Reason:** Per-task model discovery, quality-floor scoring, cost comparisons, and routing paperwork add root activity. The user's workflow already separates planning/review from implementation, so a stable cheap-worker default is more efficient.

If Luna is unavailable, the workflow reports the blocker instead of silently switching models.

## ADR-005: Coherent bundles instead of tiny tasks

**Decision:** A worker normally receives one vertical implementation bundle that may span multiple files and internal test/code/fix cycles.

**Reason:** Every dispatch creates context and coordination overhead. Splitting DTO, entity, service, controller, UI, and tests into separate agents is usually less efficient than one bounded end-to-end assignment.

## ADR-006: Worker owns routine discovery and debugging

**Decision:** Within the approved scope, Luna may inspect neighboring code, follow existing conventions, implement, run focused tests, diagnose failures, and iterate until ready for review.

**Reason:** Sending routine implementation questions back to Sol makes the root thick again.

## ADR-007: One batched Sol review

**Decision:** Specification compliance and engineering quality/security are two lenses in one acceptance pass.

**Reason:** They are both required, but they do not need separate orchestration cycles.

## ADR-008: One correction by default

**Decision:** Normal work gets at most one consolidated correction request after the initial implementation. A second cycle is reserved for a concrete unresolved high-assurance issue.

**Reason:** Correction loops are expensive because they reactivate both worker and root contexts.

## ADR-009: Trivial work bypasses orchestration

**Decision:** Typos, tiny local edits, read-only questions, and explicitly single-agent tasks do not require the full workflow.

**Reason:** Process overhead can exceed implementation cost for small changes.

## ADR-010: No polling

**Decision:** After dispatch, the root waits for completion instead of requesting routine progress updates or duplicating worker exploration.

**Reason:** Polling adds token churn without improving the finished patch.

## ADR-011: Optional global policy

**Decision:** Global `AGENTS.md` integration remains opt-in.

**Reason:** The skill is useful without globally affecting every project. When installed, the policy is scoped to substantial work and preserves repository/user restrictions.

## ADR-012: Safe installation remains

**Decision:** Keep preview-first installation, atomic changes, backups, receipts, guarded undo, and doctor diagnostics.

**Reason:** These mechanisms are useful independently of the orchestration strategy and make global configuration changes reversible.

## ADR-013: No autonomous external effects

The orchestrator does not authorize commits, pushes, merges, deployment, credential changes, destructive migrations, or production operations.
