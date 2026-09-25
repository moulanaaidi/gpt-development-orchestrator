# Batched independent review

Worker completion means ready for review, not accepted.

Review the actual diff and relevant evidence once using two lenses in the same pass.

## Lens 1: specification compliance

- Does the implementation satisfy the approved objective and acceptance criteria?
- Did it preserve agreed contracts and stay within scope?
- Are important success and failure paths covered?

## Lens 2: engineering quality and risk

- Check correctness, maintainability, error handling, security and privacy, portability, performance where material, and regression risk.
- Inspect tests for meaningful behavior coverage.
- Check interactions with existing code and shared contracts.

Do not routinely repeat the worker's complete repository discovery, full test suite, or visual QA when adequate evidence exists. Perform targeted independent checks when evidence is missing, a failure is plausible, or risk justifies it.

If changes are required, send all concrete file-level findings in one consolidated correction request to the same worker. Default to one correction cycle.

A second cycle is an exception for a concrete unresolved high-assurance issue involving architecture, authentication or authorization, payments, tenancy, secrets, destructive migrations, production behavior, or high-impact shared infrastructure.

Workers never approve their own changes. Acceptance remains with the planner/reviewer or the user.
