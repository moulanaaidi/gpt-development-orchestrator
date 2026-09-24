# Implementation Plan

## Release Objective

Deliver version 0.1 as an installable, testable, and reversible Codex skill that
implements Sol-led planning, risk-based GPT worker routing, evidence-based
review, and cross-session continuity.

## Quality Gates

- Python 3.11+ standard library only at runtime.
- Preview-only installation unless `--apply` is explicit.
- Atomic writes, backups, ownership markers, and receipt-driven undo.
- No reads from authentication files and no secret values in output.
- Plan validation rejects unsafe parallel ownership and incomplete task briefs.
- Skill validation passes the current Codex skill validator.
- Unit and integration tests pass on the local Windows environment.
- Sol reviews every delegated diff and runs the combined suite.

## Work Packages

### SOL-01: Architecture And Contracts

- **Owner:** Sol-class controller
- **Write set:** `README.md`, `docs/ARCHITECTURE.md`,
  `docs/IMPLEMENTATION-PLAN.md`, `docs/DECISIONS.md`
- **Output:** frozen version 0.1 boundaries, role authority, routing policy,
  component design, delegation contracts, and quality gates.
- **Acceptance:** implementation workers can proceed without choosing product
  policy or inventing architecture.

### TERRA-01: Safe Installation And Diagnostics

- **Owner:** Terra-class worker (`gpt-5.6-terra` in the current host)
- **Depends on:** SOL-01
- **Write set:** `install.py`, `orchestrator_core/**`,
  `tests/test_installer.py`, `tests/test_doctor.py`
- **Output:** preview/apply/uninstall-or-undo mechanics, atomic backups and
  receipts, marked policy merge, path discovery, package integrity checks, and
  read-only doctor command.
- **Acceptance:** repeated apply is idempotent; undo restores prior content;
  interrupted writes cannot leave partial target files; dry run changes
  nothing; tests use isolated temporary homes.

### LUNA-01: Skill Workflow Package

- **Owner:** Luna-class worker (`gpt-6-luna` in the current host)
- **Depends on:** SOL-01
- **Write set:** `skill/gpt-development-orchestrator/**`, `POLICY.md`,
  `WORKER-INSTRUCTIONS.md`
- **Output:** concise skill entrypoint, progressive references for planning,
  routing, delegation, review, and continuity, plus task/checkpoint templates
  and UI metadata.
- **Acceptance:** no Reach or CEO coupling; small tasks are not needlessly
  orchestrated; authority and safety boundaries match the architecture; all
  references are discoverable from `SKILL.md`.

### LUNA-02: Plan Schema And Validator

- **Owner:** Luna-class worker (`gpt-6-luna` in the current host; GPT-5.5 and
  GPT-5.4 are not currently exposed as native worker overrides)
- **Depends on:** SOL-01
- **Write set:** `schemas/plan.schema.json`, `tools/validate_plan.py`,
  `tests/test_validate_plan.py`, `examples/valid-plan.json`
- **Output:** documented JSON contract and deterministic validator with useful
  path-based error messages.
- **Acceptance:** validates the example; rejects missing fields, unknown model
  names, dependency cycles, undeclared dependencies, duplicate task IDs,
  overlapping parallel write sets, empty acceptance criteria, and mutating
  tasks without validation commands.

### SOL-02: Integration And Review

- **Owner:** Sol-class controller
- **Depends on:** TERRA-01, LUNA-01, LUNA-02
- **Write set:** any repository path, only to integrate or correct reviewed work
- **Output:** reviewed combined implementation, aligned path references,
  completed public documentation, license/security files if useful, and release
  checkpoint.
- **Acceptance:** all tests and validators pass; install preview/apply/doctor/
  undo are exercised in temporary directories; no unresolved critical or high
  finding remains.

## Review Procedure

Sol reviews each work package in two passes:

1. **Specification:** boundaries, requested behavior, interfaces, and evidence.
2. **Engineering:** correctness, failure handling, security, maintainability,
   portability, tests, and interaction with other packages.

Sol consolidates findings before assigning corrections. Workers do not approve
their own output.
