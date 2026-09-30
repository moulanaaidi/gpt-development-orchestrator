# Batched independent review

Worker completion means ready for review, not accepted.

Review once with two lenses: specification compliance and engineering quality/security.

## Delta-first review

1. Start with changed-file names and diff statistics.
2. Read relevant diff hunks against the approved contract and worker evidence.
3. Open full changed files, neighboring code, or broader tests only when a concrete dependency, regression path, security concern, or missing evidence justifies it.
4. Do not repeat the worker's full repository discovery, full test logs, or complete validation suite by default.

Check correctness, scope, contracts, success/failure paths, maintainability, error handling, security/privacy, meaningful tests, and material regression/performance risk.

If changes are required, send one findings-only correction request with concrete file/behavior references. Do not resend unchanged contract text. Default to one correction cycle.

A second cycle is reserved for a concrete unresolved high-assurance issue involving architecture, authn/authz, payments, tenancy, secrets, destructive migrations, production behavior, or high-impact shared infrastructure.

Workers never approve their own work.
