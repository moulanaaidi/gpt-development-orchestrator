# Model Routing

Choose a model for the task at hand from capabilities the current Codex host
actually exposes. Model names and relative strengths can change; do not infer
quality, price, or reasoning support from a name or a previous session.

## Discover the current choices

Before implementation begins in a session, inspect whether the host exposes
native delegation, suitable advertised lower-GPT choices, and adequate
invocation-identity evidence. This is a session compatibility check: make it
once, then verify identity evidence on every Sol and worker invocation. Use
exact advertised IDs and supported reasoning levels. Refresh compatibility
only if the host changes or an invocation fails (including an unavailable
override). If required evidence is absent, stop promptly; do not retry the
same missing check. A plan's `model_registry` is a snapshot, not a permanent
catalogue.

Every code or file implementation task requires host-native delegation to a
suitable lower GPT worker. Do not keep implementation local as a fallback.
Read-only questions and read-only reviews need no implementation worker. Never
invent a model, query credentials, or use an external router to fill a gap.

## Choose for outcome and total effort

1. Assess the task's difficulty, blast radius, ambiguity, and acceptance
   checks to determine the quality floor and suitable worker capability.
2. Set a quality floor. Security boundaries, irreversible operations, complex
   architecture, and difficult debugging require stronger reasoning and closer
   review. A bounded fixture or documentation edit usually does not.
3. Compare eligible candidates using *available evidence*: host capability
   descriptions, supported reasoning levels, disclosed cost or usage class,
   and recent results on comparable tasks. Treat unknown cost or quality as
   unknown, not as free or sufficient.
   When price materially affects the choice and the host supplies no cost
   data, consult current official pricing if available. Match the user's
   actual billing mode: API token prices are not Codex subscription usage.
4. Choose the lowest expected **total** effort among candidates likely to
   clear the quality floor. Include prompt/context size, execution, tests,
   review, retries, and integration in that estimate. Prefer a stronger model
   when a cheap first attempt is likely to create more correction work.
5. Use the lowest reasoning level likely to clear the floor. Increase it for a
   specific hard decision or failed attempt, then return to the normal level.
6. Record the selected exact model, reasoning level when configurable, short
   reason, and uncertainty in the task brief or plan. Reassess after evidence
   arrives rather than treating the first choice as permanently correct.

Sol owns the actual plan and final acceptance. If the root agent is not Sol, it
must delegate plan authorship and final review to Sol and must not claim Sol
identity. For exceptionally hard planning or
review, Sol can obtain a second opinion from the strongest suitable model the
host exposes, then inspect and decide. Worker models do not approve their own
changes. A main-session model selected in the Codex UI may not be changeable by
this skill; use advertised native delegation for bounded implementation and
fail closed if no suitable worker is available.

## Learn from actual work

After review, note whether the worker met acceptance on the first attempt,
which checks ran, what corrections were needed, and whether routing saved
effort. Use these observations for comparable tasks in the same project.
Do not store secrets or claim a measured cost when the host has not supplied
one. A single success or failure is weak evidence; do not turn it into a
permanent model ranking.

Keep delegation bounded. One or two independent workers are usually enough;
parallelism is useful only when write sets are disjoint and its coordination
cost is lower than the time saved. Every implementation task still requires a
worker, even when it is too small to benefit from parallelism.
