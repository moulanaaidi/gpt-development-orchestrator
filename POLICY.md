## Token-efficient development orchestration

Use orchestration only for substantial multi-file work; trivial edits and read-only tasks stay single-agent.

An approved external spec skips replanning; it does not force Direct. A suitable root may implement small/medium bounded work. Substantial work may go to the configured worker when discovery/implementation can amortize the handoff. Reference specs by path/file instead of copying them.

For high-risk lifecycle/state, transaction, idempotency, auth, or payment changes, inventory every relevant mutation path, including adjacent existing flows. Apply the same transition, concurrency, atomicity, and error-contract rules to each and cover material paths with focused tests.

When planning is needed, use the best suitable available planner/reviewer for task, risk, and budget. Explicit user/project model choices take precedence; do not hard-code a model.

Normal delegated work is one planning batch, one dispatch, one blocking wait, one batched independent review, and one final response. The worker owns scoped discovery, implementation, focused tests, debugging, and verification. Do not poll, replay transcripts, duplicate broad discovery, paste large specs, reread unchanged files, or repeatedly rerun broad passing validation.

Review the spec reference, diff, and concise evidence once. Send one consolidated correction by default. If material acceptance still fails, stop and report not accepted. A second correction requires explicit user/project authorization for an exceptional high-assurance case.

One writer owns a path. Parallelize only independent disjoint work in separate workspaces. Workers never approve themselves.

This policy does not authorize commit, push, merge, publish, deploy, credential changes, production operations, or destructive external actions.
