# Planning

Planning exists to remove decisions from the implementation worker, not to duplicate implementation detail.

Reuse an approved specification or repository plan whenever one already settles the relevant product and architecture decisions. Do not create a competing plan just because this skill is active.

For new substantial work, the Sol-class planner should establish only what the worker needs to execute safely:

- observable objective and non-goals;
- relevant repository evidence and existing conventions;
- interfaces, invariants, data or API contracts;
- failure behavior and material security or production constraints;
- one coherent implementation bundle or a small number of dependency-ordered bundles;
- bounded write scope;
- acceptance criteria and focused validation commands.

Prefer vertical bundles that can be implemented and verified end to end. Do not divide work by every file, function, or five-minute step.

A task is ready when GPT-6 Luna can discover the local implementation details, make routine coding choices from repository conventions, implement, test, and debug without inventing product or architecture decisions.

Keep plans concise. Link to authoritative repository documents instead of copying them.
