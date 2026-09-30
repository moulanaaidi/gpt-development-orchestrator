# Routing

Planner/final reviewer: GPT-6.1 Sol (`gpt-6.1-sol`). Implementation worker: installed `gpt_luna_builder`, pinned to GPT-6 Luna at medium reasoning. The skill cannot switch the active root or global defaults. Never silently substitute another model.

Do not run model rankings, price comparisons, quality-floor scoring, or registry discovery per task.

## Approved external specification

An approved external specification bypasses planning regardless of which root model happens to be active.

- In a GPT-6 Luna root session: implement directly.
- In a non-Luna root with native `gpt_luna_builder`: dispatch once without a planning pass. Review inside Codex only when explicitly requested.
- When preserving Codex allowance is the priority, prefer starting with Luna directly so Sol never ingests the implementation context.

Pass a shared spec by path/anchor and a compact task capsule rather than copying the whole artifact.

## New in-Codex work

When planning is actually required, use the Sol root once, then one Luna worker for one coherent bundle. Confirm worker availability once per session or after a real invocation failure; do not repeatedly probe unchanged configuration.

If a required model or delegation path is unavailable, report the blocker. Do not silently fall back.
