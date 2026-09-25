# Delegation

Delegate a coherent implementation outcome, not a sequence of tiny coding steps.

One GPT-6 Luna worker should normally own the full in-scope loop: relevant repository discovery, implementation, focused tests, debugging, and routine verification.

## Worker brief

A useful brief contains:

- the approved goal;
- exact contracts and important assumptions;
- bounded write scope;
- repository instructions or authoritative links;
- acceptance criteria;
- focused validation commands;
- concise completion-report requirements.

Do not reproduce large architecture or policy documents when a path or link is enough.

Avoid splitting one vertical feature into separate workers for DTOs, entities, services, controllers, UI, and tests unless those pieces are genuinely independent. Each additional dispatch creates context and coordination overhead.

After dispatch, let the worker finish. Do not poll for routine progress, ask for play-by-play updates, or perform overlapping repository investigation while the worker owns the bundle.

Use one writer by default. Parallelize only when tasks are independent, write sets are disjoint, and separate workspaces are verified.

If the worker discovers a material contract conflict or needs a product, architecture, security, or shared-interface decision, it should stop and return one batched blocker report.
