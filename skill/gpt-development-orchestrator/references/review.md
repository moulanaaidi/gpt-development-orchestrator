# Batched independent review

Worker completion means ready for review, not accepted. Passing tests and a worker-reported PASS are evidence, not acceptance.

Review the actual diff and relevant evidence once using two lenses in the same pass.

## Delta-first review

1. Start with changed-file names and diff statistics.
2. Read the relevant diff hunks against the approved contract and worker evidence.
3. Open full changed files, neighboring code, or broader tests only when a concrete dependency, regression path, security concern, or missing evidence justifies it.
4. Avoid repository-wide rediscovery when the worker evidence and diff already establish the necessary context.

## Criterion-by-criterion acceptance

For every explicit acceptance criterion, record PASS, FAIL, or unsupported and cite concrete diff/test evidence. Final acceptance requires every material criterion to be supported and pass. Do not infer acceptance from a successful test command or worker completion report.

## Exact-value and round-trip contracts

When a criterion requires preserving an exact caller-supplied value—such as a path, identifier, URL, header, serialized field, or command argument—inspect the representation boundary for normalization, coercion, canonicalization, or platform-specific rewriting. Check the literal value required by the specification, not only a semantically equivalent value constructed by the implementation or its tests.

## Lens 1: specification compliance

- Does the implementation satisfy the approved objective and acceptance criteria?
- Did it preserve agreed contracts and stay within scope?
- Are important success and failure paths covered?

## Lens 2: engineering quality and risk

- Check correctness, maintainability, error handling, security/privacy, portability, material performance, and regression risk.
- Inspect tests for meaningful behavior coverage.
- Check interactions with existing code and shared contracts.

## High-risk mutation-surface audit

For concurrency, transactions, idempotency, lifecycle/state transitions, payments, authentication/authorization, security boundaries, destructive migrations, or high-impact shared infrastructure, identify every relevant mutation path that can change the protected invariant—not only the newly changed handler/store method. Inspect adjacent existing flows and persistence updates for bypasses, stale writes, inconsistent terminal-state handling, or mismatched API error contracts.

Perform a targeted independent check when supplied evidence does not establish a material invariant. A passing suite does not substitute for this audit.

Do not routinely repeat the worker's complete repository discovery or full test suite when adequate evidence exists.

If any material criterion is unsupported or incorrect, do not accept the work. Send all concrete file-level findings in one consolidated correction request to the same worker.

Default to one correction cycle. If material acceptance still fails after that correction, stop and report not accepted. A second correction requires explicit user/project authorization for an exceptional high-assurance case.

Workers never approve their own changes. Acceptance remains with the planner/reviewer or the user.
