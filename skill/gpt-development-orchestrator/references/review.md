# Batched independent review

Worker completion means ready for review, not accepted. Passing tests and a
worker-reported PASS are evidence, not acceptance.

Review the actual diff and relevant evidence once using two lenses in the same pass.

## Delta-first review

1. Start with changed-file names and diff statistics.
2. Read the relevant diff hunks against the approved contract and worker evidence.
3. Open full changed files, neighboring code, or broader tests only when a concrete dependency, regression path, security concern, or missing evidence justifies it.
4. Avoid repository-wide rediscovery when the worker evidence and diff already establish the necessary context.

## Criterion-by-criterion acceptance

For every explicit acceptance criterion, record PASS, FAIL, or unsupported and
cite the concrete diff/test evidence. Final acceptance requires every material
criterion to be supported and pass. Do not infer acceptance from a successful
test command or from the worker's completion report.

## Lens 1: specification compliance

- Does the implementation satisfy the approved objective and acceptance criteria?
- Did it preserve agreed contracts and stay within scope?
- Are important success and failure paths covered?

## Lens 2: engineering quality and risk

- Check correctness, maintainability, error handling, security and privacy, portability, performance where material, and regression risk.
- Inspect tests for meaningful behavior coverage.
- Check interactions with existing code and shared contracts.

## High-risk invariants

For concurrency, transactions, idempotency, lifecycle/state transitions,
payments, authentication/authorization, security boundaries, destructive
migrations, or high-impact shared infrastructure, inspect the relevant invariant
and mutation path directly. A passing test suite does not substitute for this
check.

Perform a targeted independent check when supplied evidence does not establish a
material invariant—for example, verify the stale-write guard protects the full
version/equivalent mutation contract rather than only one visible state field.
Keep this targeted: do not repeat broad repository discovery or rerun full suites
without a concrete reason.

Do not routinely repeat the worker's complete repository discovery, full test suite, or visual QA when adequate evidence exists. Perform targeted independent checks when evidence is missing, a failure is plausible, or risk justifies it.

If any material criterion is unsupported or incorrect, do not accept the work.
Send all concrete file-level findings in one consolidated correction request to
the same worker. Default to one correction cycle.

A second cycle is an exception for a concrete unresolved high-assurance issue involving architecture, authentication or authorization, payments, tenancy, secrets, destructive migrations, production behavior, or high-impact shared infrastructure.

Workers never approve their own changes. Acceptance remains with the planner/reviewer or the user.
