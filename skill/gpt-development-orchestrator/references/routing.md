# Model Routing

Choose a model for the task at hand from capabilities the current Codex host
actually exposes. Model names and relative strengths can change; do not infer
quality, price, or reasoning support from a name or a previous session.

## Discover the current choices

Before the first delegation in a session, inspect the native delegation tool's
available model overrides and descriptions. Use the exact advertised IDs and
supported reasoning levels. Include the current controller as a candidate for
keeping work local. Refresh this view if the host changes or a model call fails
because an override is unavailable. A plan's `model_registry` is a snapshot of
these choices for that plan, not a permanent catalogue.

If the host does not expose delegation or enough capability information, keep
the task local or use an explicitly available model that meets the task's
requirements. Never invent a model, query credentials, or use an external
router to fill a gap.

## Choose for outcome and total effort

1. Describe the task's difficulty, blast radius, ambiguity, and acceptance
   checks. Decide whether independent implementation and review add value.
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

Sol owns the plan and final acceptance. For exceptionally hard planning or
review, Sol can obtain a second opinion from the strongest suitable model the
host exposes, then inspect and decide. Worker models do not approve their own
changes. A main-session model selected in the Codex UI may not be changeable by
this skill; in that case use available delegation for bounded assistance.

## Learn from actual work

After review, note whether the worker met acceptance on the first attempt,
which checks ran, what corrections were needed, and whether routing saved
effort. Use these observations for comparable tasks in the same project.
Do not store secrets or claim a measured cost when the host has not supplied
one. A single success or failure is weak evidence; do not turn it into a
permanent model ranking.

Keep delegation bounded. One or two independent workers are usually enough;
parallelism is useful only when write sets are disjoint and its coordination
cost is lower than the time saved. Small, clear edits should remain local.
