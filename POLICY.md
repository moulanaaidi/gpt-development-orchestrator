## Token-efficient development orchestration

Use orchestration only for substantial multi-file work; trivial edits and read-only tasks should stay single-agent.

If an approved external specification already exists, use it directly. Prefer referencing its repository path or accessible file instead of copying it into another prompt. A GPT-6 Luna session should implement directly without recreating the plan or adding a review loop unless requested.

When planning is required inside Codex, use GPT-6.1 Sol (`gpt-6.1-sol`) as planner/final reviewer and `gpt_luna_builder` on GPT-6 Luna (`gpt-6-luna`) at medium reasoning for implementation.

Normal delegated work is one planning batch, one dispatch, one wait, one batched independent acceptance review, and one final response. Luna owns scoped repository discovery, implementation, focused tests, debugging, and routine verification. Do not poll, replay transcripts, duplicate repository discovery, paste large specs into worker prompts, or rerun broad validation without a concrete reason.

Review the spec reference, actual diff, and concise verification evidence once. Consolidate corrections into one request by default.

One writer owns a path. Parallelize only independent disjoint work in separate workspaces. Workers never approve themselves.

This policy does not authorize commit, push, merge, publish, deploy, credential changes, production operations, or destructive external actions.
