# Version 0.1 Release Checklist

## Architecture

- [x] The skill remains generic and contains no product-specific governance.
- [x] Sol owns planning, design, integration, and final acceptance.
- [x] Worker routing is risk-based and limited to models available in the host.
- [x] Small tasks can be completed without unnecessary delegation.

## Safety

- [x] Installer preview causes no filesystem mutation.
- [x] Apply is explicit, idempotent, atomic, and backed up.
- [x] Policy edits are optional and confined to owned markers.
- [x] Undo refuses stale or unsafe restoration.
- [x] All destination and receipt paths are contained under the selected Codex
  home.
- [x] No code reads authentication files or emits secret values.
- [x] Doctor is read-only.

## Planning And Delegation

- [x] Valid example plan passes validation.
- [x] Invalid structure, task IDs, models, dependencies, cycles, write sets, and
  validation fields fail with actionable paths.
- [x] Parallel tasks cannot claim overlapping write sets.
- [x] Worker brief requires changed paths, commands/results, deviations, and
  unresolved risks.
- [x] Sol performs specification and engineering review passes.

## Verification

- [x] `python -m unittest discover -s tests -v` passes.
- [x] The current Codex skill validator accepts the packaged skill.
- [x] Preview, apply, doctor, idempotent reapply, and undo pass in a temporary
  Codex home.
- [x] A clean install leaves no machine-specific paths in installed content.
- [x] `git diff --check` passes.
- [x] Sol has reviewed every delegated diff and no critical or high finding is
  open.

## Release Hygiene

- [x] README contains tested install and usage commands.
- [x] Version and change notes are updated.
- [x] No generated receipts, temporary homes, caches, or secrets are tracked.
- [x] Commit, tag, publish, or deployment occurs only after explicit user
  authorization.

Verified on Windows with Python 3.12. Seven POSIX/link tests were skipped on
this host because Windows link privileges or POSIX mode semantics were not
available; the guarded code paths remain covered by platform-conditional tests.
