# Changelog

## 0.2.0 - 2026-09-26

- Redesign the workflow around thin-root orchestration: Planner plans once, GPT-6 Luna owns implementation/test/debug/verification, and Reviewer reviews once.
- Add an external-approved-spec path that lets a GPT-6 Luna Codex session implement directly without recreating planning inside Codex.
- Stop forcing orchestration onto trivial edits and read-only work.
- Remove per-task model ranking, cost analysis, and quality-floor routing from the runtime workflow; GPT-6 Luna is the default implementation worker.
- Prefer one coherent vertical implementation bundle over many tiny worker tasks.
- Treat specification compliance and engineering quality/security as two lenses in one batched review.
- Default to one consolidated correction cycle; reserve a second for concrete high-assurance risk.
- Explicitly discourage worker polling, duplicate repository exploration, and routine full-validation reruns.

## 0.1.3 - 2026-09-24

- Check host delegation and identity compatibility once per session, verify
  each invocation, and fail fast on missing evidence; retry compatibility
  checks only after a host change or invocation failure.
- Limit each implementation to an initial attempt and two correction cycles;
  replanning the same outcome does not reset the limit.
- Add a representative-screen direction gate for visual product work, separate
  visual acceptance from structural validation, and keep worker briefs concise.
- Record first-pass outcomes, corrections, and host-reported usage only;
  unreported usage remains unknown.

## 0.1.2 - 2026-09-24

- Require a planner-authored plan, bounded implementation by a lower GPT worker,
  and independent two-pass independent review for every implementation task, including
  small changes.
- Clarify that the global AGENTS.md policy is opt-in.

## 0.1.1 - 2026-09-24

- Route against models exposed in the current Codex session using a task quality
  floor, expected total effort, and explicit uncertainty about unknown costs.
- Record optional routing evidence in plans and use version-neutral examples.

## 0.1.0 - 2026-09-24

- Added the generic planner-led Codex orchestration skill.
- Added planning, delegation, review, and continuity templates.
- Added the JSON plan schema and deterministic plan validator.
- Added the preview-first, reversible skill and optional policy installer.
- Added managed backups, strict receipts, guarded undo, and read-only doctor.
