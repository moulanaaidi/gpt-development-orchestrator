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

## External-spec path

When an approved external specification is supplied and the active session is suitable for implementation, implement directly. No planning subagent is required.

## Orchestrated path

Confirm worker availability once per session or after an actual invocation failure. Dispatch one coherent bundle.

If the configured worker is unavailable, use another worker only when the user/project has approved that alternative; otherwise report the blocker. Do not silently substitute models.

Use the configured reasoning effort for the worker. Increase it only for a concrete failed implementation or difficult local diagnosis, not by default.

Workers must not recursively delegate. One worker normally owns one coherent implementation bundle.
