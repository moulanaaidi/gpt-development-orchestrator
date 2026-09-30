# Routing

The planner and final reviewer use GPT-6.1 Sol (`gpt-6.1-sol`). Select that model for the root session; the skill does not change the active root or global model defaults. If the requested planner/reviewer is unavailable, report the blocker rather than silently substituting another model.

The normal implementation worker is the installed native `gpt_luna_builder` role, pinned to GPT-6 Luna.

Do not perform a fresh model ranking, price comparison, quality-floor calculation, or model-registry exercise for each task. The workflow already separates high-leverage planning and acceptance from high-volume implementation.

## External-spec path

When an approved external specification is supplied and the active Codex session is GPT-6 Luna, implement directly. No subagent is required.

## In-Codex path

When a GPT-6.1 Sol root is orchestrating, confirm once per session that the host exposes the installed `gpt_luna_builder` role and native delegation. Recheck only after the host changes or a real invocation fails.

If Luna is unavailable, report the blocker. Do not silently substitute another model.

Use medium reasoning for the Luna worker, matching the installed role. Increase effort only for a concrete failed implementation or difficult local diagnosis, not by default.

The worker must not recursively delegate. One Luna worker normally owns one coherent implementation bundle.
