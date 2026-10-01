# Routing

The planner/final reviewer is model-agnostic. Use the best suitable available model for the task, risk, and budget.

Selection precedence:

1. explicit user model choice;
2. project-configured planner/reviewer choice;
3. the capable model already selected by the host/session;
4. if that model is unsuitable, require selection of another capable available model outside the skill.

The skill cannot change the active root model. Do not hard-code a planner/reviewer family or model name, and do not silently override an explicit user/project choice.

The bundled implementation worker is `gpt_luna_builder`. It is a package default, not an architectural requirement; a project may use another approved worker role when configured.

Do not perform a fresh model ranking, price comparison, benchmark, or model-registry exercise for every task. Re-evaluate routing only when requirements, host capabilities, configured models, or availability materially change.

## Accepted-work efficiency

Optimize for total accepted-work efficiency, not root-token reduction alone.
Delegation is not automatically better because it makes the root thinner.

Prefer direct implementation when:
- an approved specification already bounds the work;
- the active model is suitable for implementation;
- the change is small or medium enough that a second repository-discovery and
  handoff cycle is likely to cost as much as the implementation.

Prefer delegation when planning is still required, the implementation is large
enough to amortize worker context/discovery, spans substantial cross-module
implementation/test/debug work, or the project explicitly requires a separate
implementation worker.

Do not delegate solely to reduce root-model token usage.

## External-spec path

An approved specification removes the need to replan; it does not force direct
implementation. Choose the implementer with the accepted-work rules above.

For a small/medium bounded change, a suitable active root may implement directly.
For substantial work where worker discovery/implementation can amortize the
handoff, dispatch the approved specification by repository/file reference to one
configured worker without recreating the plan, then perform one batched
independent root review.

## Orchestrated path

Confirm worker availability once per session or after an actual invocation failure. Dispatch one coherent bundle.

If the configured worker is unavailable, use another worker only when the user/project has approved that alternative; otherwise report the blocker. Do not silently substitute models.

Use the configured reasoning effort for the worker. Increase it only for a concrete failed implementation or difficult local diagnosis, not by default.

Workers must not recursively delegate. One worker normally owns one coherent implementation bundle.
