## Thin-root development orchestration

Use the orchestration skill for substantial multi-file features, migrations, refactors, or builds. Do not force orchestration onto trivial edits, read-only questions, or explicitly single-agent work.

There are two supported paths.

1. External approved specification.
When the user supplies an approved implementation specification from outside Codex, treat that specification as authoritative. If the active Codex session is already using the implementation model, implement it directly. Do not recreate the architecture, re-plan the feature, or add an independent review unless the user explicitly asks for one.

2. In-Codex thin-root orchestration.
When planning is being done inside Codex, keep a planner/reviewer root focused on scope, architecture, contracts, acceptance criteria, material risk, and final acceptance. After the contract is ready, delegate one coherent implementation bundle through the native `gpt_luna_builder` role, which is pinned to GPT-6 Luna. Luna owns in-scope repository discovery, implementation, testing, debugging, and routine verification.

For a normal delegated phase, target one planning batch, one dispatch, one wait, one batched independent acceptance review, and one final response. Do not poll a healthy worker, request play-by-play status, duplicate its repository exploration, or split one coherent feature into tiny worker calls for visibility.

Review specification compliance and engineering quality as two lenses in one batched independent review. Send all findings in one correction request and default to at most one correction cycle. A second correction cycle is reserved for a concrete high-assurance issue involving architecture, authentication or authorization, payments, tenancy, secrets, destructive migrations, production behavior, or high-impact shared infrastructure.

Use GPT-6 Luna as the default implementation worker when available. Do not run per-task model ranking, cost analysis, quality-floor comparisons, or model-registry discovery when the approved workflow already names Luna. If the required model or native delegation path is unavailable, report the blocker rather than silently switching models.

One writer owns a path at a time. Parallel workers are optional and should be used only for genuinely independent work with disjoint write sets and separate workspaces. Workers do not approve their own changes.

This workflow does not authorize commits, pushes, merges, publication, deployments, credential changes, production operations, or destructive external actions. Repository policy and explicit user authorization remain authoritative.
