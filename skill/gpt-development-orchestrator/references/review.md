# Sol Review

Sol reviews every delegated change directly. Inspect the actual diff and relevant surrounding code; do not accept a worker's summary as proof. Run suitable checks when the environment permits and distinguish tests actually run from proposed tests.

## Pass 1: Specification

- Does the change meet the task outcome and acceptance criteria?
- Did it stay inside the assigned write set and preserve agreed interfaces and repository policies?
- Is there evidence for each important behavior, including failure paths where relevant?

## Pass 2: Engineering quality

- Check correctness, security/privacy, error handling, maintainability, portability, performance where material, and regression risk.
- Inspect tests for meaningful behavior coverage, not merely matching implementation details.
- Check interactions with other task bundles and the existing system.

## Outcome

Accept only when both passes are satisfactory and required validation is complete. Otherwise, Sol may make a narrow correction or issue one consolidated correction brief with findings, paths, and acceptance checks. Re-review the resulting diff. If more correction cycles are needed, state why. Do not let workers approve their own work or silently waive unresolved risks.

Report material gaps plainly. No automatic commit, push, merge, publish, deployment, credential mutation, or production operation is implied by review or acceptance.
