# Architecture Decisions

## ADR-001: Generic Rather Than Reach-Specific

**Decision:** The orchestrator contains no Reach terminology, delivery-domain
rules, CEO role, or product-specific approval gate.

**Reason:** It must serve future projects. Each target repository owns its own
business governance and approval requirements.

## ADR-002: Native Codex Delegation

**Decision:** Version 0.1 uses Codex native subagents with explicit, host-
available GPT model selection and role-based routing.

**Reason:** Native delegation exposes a set of GPT workers in the current
environment. An external API router would add credentials, cost controls,
failure modes, and maintenance without improving the initial goal. ADR-008
defines how available workers are chosen per session.

## ADR-003: Sol Retains Final Authority

**Decision:** Sol plans and reviews; implementation workers cannot approve,
integrate, or expand their own work.

**Reason:** Separating implementation from acceptance reduces self-review bias
and prevents task drift.

## ADR-009: Mandatory Sol-Worker-Sol For Implementation

**Decision:** Every code or file implementation task, including small changes,
requires an actual Sol-authored plan, bounded implementation by a lower GPT
worker selected from host-advertised choices and invoked through native
delegation, and independent two-pass review by Sol. Read-only questions and
reviews do not require a worker. A non-Sol root delegates plan authorship and
final review to Sol without claiming Sol identity. Missing Sol, worker,
delegation, or adequate host identity evidence fails closed. Self-reported
receipts are not host invocation evidence.

**Reason:** A size-based local bypass defeats consistent independent review and
planning. Host-advertised native capabilities avoid guessed model IDs and
external routing. The global policy and skill remain process guidance rather
than technical enforcement; host-level gating is required for a guarantee.

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

## ADR-008: Session-Specific Model Choice

**Decision:** Routing compares the models and reasoning levels exposed by the
current host against each task's quality floor and expected total effort. Model
IDs live in session plans, not permanent routing rules. Missing price or
quality data is recorded as unknown.

**Reason:** Versioned model rankings become stale. A lower per-message price
does not guarantee lower total usage when review and retries are counted. Host
descriptions and observed outcomes can inform a choice, but this workflow
cannot prove a globally optimal model without reliable measurements.

## ADR-010: Bounded Correction And Session Compatibility

**Decision:** Check delegation and identity compatibility once per session,
verify identity per invocation, and repeat compatibility checks only when the
host changes or an invocation fails. Stop on missing evidence. Limit an
implementation to one initial attempt and two correction cycles; replanning
the same intended outcome does not reset the limit.

**Reason:** Repeatedly probing an unchanged host or reopening the same plan
creates unbounded work without improving evidence or accountability.

## ADR-011: Visual Direction Before Scale

**Decision:** Visual product work starts with one representative,
production-quality screen. Sol confirms the direction before it is applied
more broadly. User approval is required only where the target repository says
it is. Visual acceptance is distinct from structural validation.

**Reason:** Early direction review bounds visual rework while preserving the
target repository's own approval rules and the separate need for behavioral,
accessibility, and test validation.

## ADR-012: Compact Briefs And Honest Outcome Evidence

**Decision:** Worker briefs summarize only task-specific context and link to
authoritative documents. Record first-pass success, correction count, and
host-provided usage; usage not reported by the host is unknown.

**Reason:** Linked context reduces prompt duplication, while explicit evidence
limits prevent self-reported or inferred usage from being mistaken for facts.
