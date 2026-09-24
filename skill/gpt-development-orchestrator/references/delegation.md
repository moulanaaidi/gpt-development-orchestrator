# Delegation

Sol delegates implementation, not authority. Every implementation task, including small tasks, must be assigned to a lower GPT worker using the host's native delegation mechanism. If native delegation or suitable advertised workers are unavailable, stop without implementing and explain the blocker. Give each worker one outcome and a finite write set. Never imply delegation occurred when it did not.

## Task brief

Each assignment should state:

- goal and relevant repository context;
- exact owned paths and paths that must remain untouched;
- interfaces, constraints, and important assumptions;
- acceptance criteria and focused validation commands;
- required return format: status, changed paths, commands/results, deviations, unresolved risks, and follow-up needs.

Keep the brief compact. Link to authoritative repository instructions,
architecture, design, or policy documents instead of copying their contents;
include only task-specific context needed to implement safely. Use
[../templates/task-brief.md](../templates/task-brief.md) when it helps. Do not
include secrets or unnecessary sensitive data.

Host-provided invocation evidence (for example, agent/model metadata supplied
by the host) is distinct from a worker's self-reported receipt. Do not treat
the latter as proof of the former. The active root agent must not claim Sol
identity unless the host establishes that identity; a non-Sol root delegates
plan authorship and final review to Sol.

## Ownership and parallel work

- Assign one writer to each path at a time. Explicitly list all paths, including tests and generated artifacts that the task may change.
- Parallelize only when write sets are disjoint and shared contracts are already defined. If two tasks need the same path, serialize them or have Sol redefine the split before dispatch.
- Require workers to stop and report if the implementation needs an unowned path, changes a shared contract, contradicts repository policy, or invalidates a plan assumption.
- Workers do not commit, push, merge, deploy, or broaden their assignment. They return changes and evidence for Sol to inspect.

## Evidence return

Ask for concise, verifiable evidence: changed paths, tests or checks actually run and their results, known gaps, and deviations from the brief. A claimed test pass is not a substitute for Sol's inspection or combined validation.

Each implementation gets one initial worker attempt and at most two correction
cycles. Sol sends one consolidated correction brief per cycle. If acceptance is
still unmet after the second correction, stop editing and report findings for
Sol's decision. Renaming or splitting the same acceptance outcome into a new
plan cannot restart the correction budget. Resume implementation only under a
materially new, explicitly authorized objective; preserve the earlier attempt
and correction history in the report.
