# Architecture Decisions

## ADR-001: Generic Rather Than Reach-Specific

**Decision:** The orchestrator contains no Reach terminology, delivery-domain
rules, CEO role, or product-specific approval gate.

**Reason:** It must serve future projects. Each target repository owns its own
business governance and approval requirements.

## ADR-002: Native Codex Delegation

**Decision:** Version 0.1 uses Codex native subagents with explicit, host-
available GPT model selection and role-based routing.

**Reason:** Native delegation exposes Sol-, Terra-, and Luna-class workers in
the current environment. An external API router would add credentials, cost
controls, failure modes, and maintenance without improving the initial goal.
Lower-cost GPT versions may be configured when the host actually exposes them.

## ADR-003: Sol Retains Final Authority

**Decision:** Sol plans and reviews; implementation workers cannot approve,
integrate, or expand their own work.

**Reason:** Separating implementation from acceptance reduces self-review bias
and prevents task drift.

## ADR-004: Skill And Deterministic Tools

**Decision:** Package orchestration guidance as a Codex skill and use small
standard-library tools for validation, installation, undo, and diagnostics.

**Reason:** This is portable, inspectable, and easy to remove. A daemon or web
service is unnecessary for local development orchestration.

## ADR-005: Dry Run And Reversibility

**Decision:** Installation previews by default; mutation requires `--apply` and
produces backups plus an undo receipt.

**Reason:** Global Codex policy affects every project and must be explicit,
auditable, and reversible.

## ADR-006: No Unverified Custom Agent Schema

**Decision:** Version 0.1 does not install custom agent TOML profiles.

**Reason:** Model overrides are available directly through native delegation,
while a stable local custom-agent schema has not been verified. Avoiding guessed
configuration prevents a brittle foundation.

## ADR-007: No Autonomous External Effects

**Decision:** The orchestrator never auto-commits, pushes, deploys, creates
credentials, or mutates production systems.

**Reason:** Delegation changes who performs bounded code work, not what the user
has authorized.
