# Changelog

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

- Require a Sol-authored plan, bounded implementation by a lower GPT worker,
  and independent two-pass Sol review for every implementation task, including
  small changes. Fail-closed handling of missing capability or identity
  evidence is a workflow requirement, not technical enforcement without a
  host-level invocation gate.
- Clarify that the global AGENTS.md policy is opt-in and that the workflow is
  strong process guidance, not technical enforcement; a host-level invocation
  gate is needed for that guarantee.
- Check for missing or stale installed policy in doctor and keep
  `--policy-file` behavior consistent with the selected policy file.

## 0.1.1 - 2026-09-24

- Route against models exposed in the current Codex session using a task quality
  floor, expected total effort, and explicit uncertainty about unknown costs.
- Record optional routing evidence in plans and use version-neutral examples.
- Remove fixed worker intelligence rankings from the skill and architecture.

## 0.1.0 - 2026-09-24

- Added the generic Sol-led Codex orchestration skill.
- Added host-capability-aware Terra, Luna, and lower-cost GPT routing guidance.
- Added planning, delegation, review, and continuity templates.
- Added the JSON plan schema and deterministic plan validator.
- Added the preview-first, reversible skill and optional policy installer.
- Added managed backups, strict receipts, guarded undo, and read-only doctor.
- Added unit and CLI lifecycle coverage.
