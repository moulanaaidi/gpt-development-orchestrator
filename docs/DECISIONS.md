# Architecture Decisions

## ADR-001: Product-neutral workflow

The orchestrator contains no product-specific governance. Each target repository owns its business rules, approvals, and deployment policy.

## ADR-002: Thin-root orchestration

**Decision:** For substantial orchestrated work, a capable planner/reviewer establishes the contract once, the configured worker owns the coherent implementation loop, and the planner/reviewer performs one batched acceptance review.

**Reason:** Planner/reviewer tokens have the highest value on architecture, contracts, risk, and acceptance. Repository exploration, implementation, testing, and debugging are high-volume activities that should remain with the implementation worker.

## ADR-003: External specifications may bypass in-session planning

**Decision:** When the user provides an approved external specification and the active session is suitable for implementation, implement directly. Do not recreate the plan or require a planning subagent.

**Reason:** This is the lowest-overhead path when the expensive reasoning has already happened. Replanning duplicates work and consumes the allowance the workflow is meant to preserve.

## ADR-004: Bundled implementation worker is a default, not an architectural requirement

**Decision:** The package currently installs `gpt_luna_builder` as its default worker role. Projects may configure another approved worker.

**Reason:** A stable default avoids per-task worker-discovery overhead while keeping the architecture future-proof.

If the configured worker is unavailable, do not silently switch models unless a user/project-approved alternative exists.

## ADR-005: Coherent bundles instead of tiny tasks

**Decision:** A worker normally receives one vertical implementation bundle that may span multiple files and internal test/code/fix cycles.

**Reason:** Every dispatch creates context and coordination overhead. Splitting DTO, entity, service, controller, UI, and tests into separate agents is usually less efficient than one bounded end-to-end assignment.

## ADR-006: Worker owns routine discovery and debugging

**Decision:** Within the approved scope, the worker may inspect neighboring code, follow existing conventions, implement, run focused tests, diagnose failures, and iterate until ready for review.

**Reason:** Sending routine implementation questions back to the planner/reviewer makes the root thick again.

## ADR-007: One batched planner/reviewer pass

**Decision:** Specification compliance and engineering quality/security are two lenses in one acceptance pass.

**Reason:** They are both required, but they do not need separate orchestration cycles.

## ADR-008: One correction by default

**Decision:** Normal work gets at most one consolidated correction request after the initial implementation. A second cycle is reserved for a concrete unresolved high-assurance issue.

**Reason:** Correction loops are expensive because they reactivate both worker and planner/reviewer contexts.

## ADR-009: Trivial work bypasses orchestration

**Decision:** Typos, tiny local edits, read-only questions, and explicitly single-agent tasks do not require the full workflow.

**Reason:** Process overhead can exceed implementation cost for small changes.

## ADR-010: No polling

**Decision:** After dispatch, the planner/reviewer waits for completion instead of requesting routine progress updates or duplicating worker exploration.

**Reason:** Polling adds token churn without improving the finished patch.

## ADR-011: Optional global policy

**Decision:** Global `AGENTS.md` integration remains opt-in.

**Reason:** The skill is useful without globally affecting every project. When installed, the policy is scoped to substantial work and preserves repository/user restrictions.

## ADR-012: Safe installation remains

**Decision:** Keep preview-first installation, atomic changes, backups, receipts, guarded undo, and doctor diagnostics.

**Reason:** These mechanisms are useful independently of the orchestration strategy and make global configuration changes reversible.

## ADR-013: No autonomous external effects

The orchestrator does not authorize commits, pushes, merges, deployment, credential changes, destructive migrations, or production operations.

## ADR-014: Planner/reviewer selection is model-agnostic

**Decision:** Do not pin planning or final acceptance to a named model. Use the best suitable available model for task complexity, risk, and budget. Respect explicit user/project choices first, then the capable host/session selection.

**Reason:** Model availability and relative capability change over time. Hard-coding a planner/reviewer makes the workflow stale and can force unnecessary cost or block a better model.

The skill itself does not switch the active root model and should not run a full benchmark or model-registry exercise on every task.
