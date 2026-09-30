# Changelog

## Unreleased - 2026-09-30

### Token-budget v0.3

- Reduce always-loaded orchestration text while preserving thin-root planning/review and a separate implementation worker.
- Make direct implementation the preferred path when an approved specification already exists.
- Add spec-by-reference guidance to avoid repeatedly pasting large workpacks into worker/reviewer prompts.
- Add transcript, repository-discovery, test-log, checkpoint, and completion-report token discipline.
- Add prompt-size regression tests so the core skill, global policy, worker instructions, and task brief do not silently grow without review.
- Remove the fixed planner/reviewer model assignment. The planner/reviewer is now selected from the best suitable available model for the task, risk, and budget, respecting explicit user/project choices.

### Worker routing

- Retain the bundled `gpt_luna_builder` role as the current default implementation worker.
- Treat the bundled worker as a package default rather than an architectural requirement.
- Preserve approved external specifications and fail clearly when a required configured worker is unavailable.

## 0.2.0 - 2026-09-26

- Redesign the workflow around thin-root orchestration: Planner plans once, the implementation worker owns implementation/test/debug/verification, and Reviewer reviews once.
- Add an external-approved-spec path that lets a suitable implementation session execute directly without recreating planning.
- Stop forcing orchestration onto trivial edits and read-only work.
- Remove per-task full model ranking, cost analysis, and quality-floor routing from the runtime workflow.
- Prefer one coherent vertical implementation bundle over many tiny worker tasks.
- Treat specification compliance and engineering quality/security as two lenses in one batched review.
- Default to one consolidated correction cycle; reserve a second for concrete high-assurance risk.
- Explicitly discourage worker polling, duplicate repository exploration, and routine full-validation reruns.

## 0.1.3 - 2026-09-24

- Check host delegation and identity compatibility once per session, verify each invocation, and fail fast on missing evidence; retry compatibility checks only after a host change or invocation failure.
- Limit each implementation to an initial attempt and two correction cycles; replanning the same outcome does not reset the limit.
- Add a representative-screen direction gate for visual product work, separate visual acceptance from structural validation, and keep worker briefs concise.
- Record first-pass outcomes, corrections, and host-reported usage only; unreported usage remains unknown.

## 0.1.2 - 2026-09-24

- Require a planner-authored plan, bounded implementation by a lower-cost worker, and independent review for implementation tasks.
- Clarify that the global AGENTS.md policy is opt-in.

## 0.1.1 - 2026-09-24

- Route against models exposed in the current development session using a task quality floor, expected total effort, and explicit uncertainty about unknown costs.
- Record optional routing evidence in plans and use version-neutral examples.

## 0.1.0 - 2026-09-24

- Added the generic planner-led development orchestration skill.
- Added planning, delegation, review, and continuity templates.
- Added the JSON plan schema and deterministic plan validator.
- Added the preview-first, reversible skill and optional policy installer.
- Added managed backups, strict receipts, guarded undo, and read-only doctor.
