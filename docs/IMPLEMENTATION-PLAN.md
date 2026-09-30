# Implementation Plan

This is the historical version 0.1 implementation record. Historical model-specific task labels have been normalized so this repository does not imply a permanent planner/reviewer model. Current routing is defined in `skill/gpt-development-orchestrator/references/routing.md`.

## Release Objective

Deliver version 0.1 as an installable, testable, and reversible Codex skill that implements planner-led planning, risk-based worker routing, evidence-based review, and cross-session continuity.

## Quality Gates

- Python 3.11+ standard library only at runtime.
- Preview-only installation unless `--apply` is explicit.
- Atomic writes, backups, ownership markers, and receipt-driven undo.
- No reads from authentication files and no secret values in output.
- Plan validation rejects unsafe parallel ownership and incomplete task briefs.
- Skill validation passes the current Codex skill validator.
- Unit and integration tests pass on the local Windows environment.
- The planner/reviewer reviews every delegated diff and runs the combined suite.

## Work Packages

### ROOT-01: Architecture And Contracts

- **Owner:** planner/reviewer controller
- **Write set:** `README.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION-PLAN.md`, `docs/DECISIONS.md`
- **Output:** frozen version 0.1 boundaries, role authority, routing policy, component design, delegation contracts, and quality gates.
- **Acceptance:** implementation workers can proceed without choosing product policy or inventing architecture.

### TERRA-01: Safe Installation And Diagnostics

- **Owner:** historical implementation worker
- **Depends on:** ROOT-01
- **Write set:** `install.py`, `orchestrator_core/**`, `tests/test_installer.py`, `tests/test_doctor.py`
- **Output:** preview/apply/uninstall-or-undo mechanics, atomic backups and receipts, marked policy merge, path discovery, package integrity checks, and read-only doctor command.
- **Acceptance:** repeated apply is idempotent; undo restores prior content; interrupted writes cannot leave partial target files; dry run changes nothing; tests use isolated temporary homes.

### WORKER-01: Skill Workflow Package

- **Owner:** historical implementation worker
- **Depends on:** ROOT-01
- **Write set:** `skill/gpt-development-orchestrator/**`, `POLICY.md`, `WORKER-INSTRUCTIONS.md`
- **Output:** concise skill entrypoint, progressive references for planning, routing, delegation, review, and continuity, plus task/checkpoint templates and UI metadata.
- **Acceptance:** no product coupling; small tasks are not needlessly orchestrated; authority and safety boundaries match the architecture; all references are discoverable from `SKILL.md`.

### WORKER-02: Plan Schema And Validator

- **Owner:** historical implementation worker
- **Depends on:** ROOT-01
- **Write set:** `schemas/plan.schema.json`, `tools/validate_plan.py`, `tests/test_validate_plan.py`, `examples/valid-plan.json`
- **Output:** documented JSON contract and deterministic validator with useful path-based error messages.
- **Acceptance:** validates the example; rejects missing fields, unknown model names, dependency cycles, undeclared dependencies, duplicate task IDs, overlapping parallel write sets, empty acceptance criteria, and mutating tasks without validation commands.

### ROOT-02: Integration And Review

- **Owner:** planner/reviewer controller
- **Depends on:** TERRA-01, WORKER-01, WORKER-02
- **Write set:** any repository path, only to integrate or correct reviewed work
- **Output:** reviewed combined implementation, aligned path references, completed public documentation, license/security files if useful, and release checkpoint.
- **Acceptance:** all tests and validators pass; install preview/apply/doctor/undo are exercised in temporary directories; no unresolved critical or high finding remains.

## Review Procedure

The planner/reviewer reviews each work package in two passes:

1. **Specification:** boundaries, requested behavior, interfaces, and evidence.
2. **Engineering:** correctness, failure handling, security, maintainability, portability, tests, and interaction with other packages.

Findings are consolidated before assigning corrections. Workers do not approve their own output.
