# Version 0.1 Release Checklist

Historical planner-model references have been normalized to generic planner/reviewer roles so this checklist does not impose a current model choice.

## Architecture

- [x] The skill remains generic and contains no product-specific governance.
- [x] The planner/reviewer owns planning, design, integration, and final acceptance.
- [x] Worker routing is risk-based and limited to models available in the host.
- [x] Small tasks can be completed without unnecessary delegation.

## Safety

- [x] Installer preview causes no filesystem mutation.
- [x] Apply is explicit, idempotent, atomic, and backed up.
- [x] Policy edits are optional and confined to owned markers.
- [x] Undo refuses stale or unsafe restoration.
- [x] All destination and receipt paths are contained under the selected Codex home.
- [x] No code reads authentication files or emits secret values.
- [x] Doctor is read-only.

## Planning And Delegation

- [x] Valid example plan passes validation.
- [x] Invalid structure, task IDs, models, dependencies, cycles, write sets, and validation fields fail with actionable paths.
- [x] Parallel tasks cannot claim overlapping write sets.
- [x] Worker brief requires changed paths, commands/results, deviations, and unresolved risks.
- [x] The planner/reviewer performs specification and engineering review passes.

## Verification

- [x] `python -m unittest discover -s tests -v` passes.
- [x] The current Codex skill validator accepts the packaged skill.
- [x] Preview, apply, doctor, idempotent reapply, and undo pass in a temporary Codex home.
- [x] A clean install leaves no machine-specific paths in installed content.
- [x] `git diff --check` passes.
- [x] The planner/reviewer reviewed every delegated diff and no critical or high finding is open.

## Release Hygiene

- [x] README contains tested install and usage commands.
- [x] Version and change notes are updated.
- [x] No generated receipts, temporary homes, caches, or secrets are tracked.
- [x] Commit, tag, publish, or deployment occurs only after explicit user authorization.

Verified on Windows with Python 3.12. Seven POSIX/link tests were skipped on this host because Windows link privileges or POSIX mode semantics were not available; the guarded code paths remain covered by platform-conditional tests.

## Version 0.1.2 Checklist

This addendum applies to the 0.1.2 release. The v0.1 checklist above records the historical 0.1 release checks. Its earlier small-task delegation policy was superseded for 0.1.2 by the mandatory workflow below.

### Policy And Review

- [x] Every implementation task, including small changes, requires an actual planner-authored task plan before implementation.
- [x] Implementation is assigned to a suitable lower-cost worker using a model advertised by the current host and its native delegation mechanism.
- [x] The planner/reviewer independently reviews each worker diff for specification compliance and engineering quality/risk; workers do not approve their own work.
- [x] Policy requires failing closed when a capable planner/reviewer, suitable worker, native delegation, or adequate host invocation identity evidence is missing; this is workflow guidance, not technical enforcement without a host-level invocation gate.
- [x] The global AGENTS.md policy is documented as opt-in.
- [x] Doctor reports missing or stale installed policy, and `--policy-file` checks the selected policy file consistently.
- [x] Documentation states honestly that process guidance is not technical enforcement and a host-level invocation gate is required for a guarantee.

### Verification And Release Hygiene

- [x] Run the applicable test suite and skill validator; record results and platform-specific skips.
- [x] Verify doctor behavior for missing and stale policy, including parity when a policy file is selected with `--policy-file`.
- [x] The planner/reviewer completes both independent review lenses for the release diff, with no unresolved critical or high findings.
- [x] Add a dated CHANGELOG.md entry describing the changes for every version before that version is published.
- [x] Confirm the release version, notes, and checklist agree.
- [x] Commit, tag, publish, or deploy only after explicit user authorization; the user explicitly authorized publication of these changes via the release commit.

## Version 0.1.3 Checklist Addendum

This addendum records the 0.1.3 workflow guidance without rewriting the historical release outcome.

### Workflow Guidance

- [x] Check host delegation and identity compatibility once per session; verify identity on every invocation and recheck compatibility only after a host change or invocation failure. Missing evidence stops work promptly.
- [x] Limit implementation to one initial attempt plus at most two correction cycles; replanning the same intended outcome does not reset the limit.
- [x] For visual product work, get planner/reviewer direction approval on one representative production-quality screen before scaling; seek user approval only when repository policy requires it.
- [x] Record visual acceptance separately from structural validation, and keep worker briefs compact with links to authoritative context.
- [x] Record first-pass success, corrections, and host-provided usage only; mark unreported usage unknown.
- [x] Keep these policies described as guidance; they are not host enforcement.

### 0.1.3 Release Gate

- [x] `python -m unittest discover -s tests -v` passes (60 tests; 7 skips for Windows-unavailable link and POSIX capabilities).
- [x] `python tools/validate_plan.py examples/valid-plan.json` passes.
- [x] `git diff --check` passes.
- [ ] Planner/reviewer completes independent specification and engineering-quality review; pending until that review is recorded.
- [ ] Release acceptance is recorded only after all preceding gates pass.
