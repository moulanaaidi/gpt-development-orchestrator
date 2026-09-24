# Delegation

Sol delegates implementation, not authority. Give each worker one outcome and a finite write set. Use the host's native delegation mechanism when present; otherwise make the assignment actionable for the available workflow without claiming a subagent was run.

## Task brief

Each assignment should state:

- goal and relevant repository context;
- exact owned paths and paths that must remain untouched;
- interfaces, constraints, and important assumptions;
- acceptance criteria and focused validation commands;
- required return format: status, changed paths, commands/results, deviations, unresolved risks, and follow-up needs.

Use [../templates/task-brief.md](../templates/task-brief.md) when it helps. Do not include secrets or unnecessary sensitive data.

## Ownership and parallel work

- Assign one writer to each path at a time. Explicitly list all paths, including tests and generated artifacts that the task may change.
- Parallelize only when write sets are disjoint and shared contracts are already defined. If two tasks need the same path, serialize them or have Sol redefine the split before dispatch.
- Require workers to stop and report if the implementation needs an unowned path, changes a shared contract, contradicts repository policy, or invalidates a plan assumption.
- Workers do not commit, push, merge, deploy, or broaden their assignment. They return changes and evidence for Sol to inspect.

## Evidence return

Ask for concise, verifiable evidence: changed paths, tests or checks actually run and their results, known gaps, and deviations from the brief. A claimed test pass is not a substitute for Sol's inspection or combined validation.
