# Delegation

Delegate a coherent implementation outcome, not a sequence of tiny coding steps.

One configured implementation worker should normally own the full in-scope loop: relevant repository discovery, implementation, focused tests, debugging, and routine verification. Preserve unrelated user changes and inspect only the repository area required by the approved bundle.

## Worker brief

A useful brief contains:

- the approved goal;
- exact contracts and important assumptions;
- bounded write scope;
- repository instructions or authoritative links;
- acceptance criteria;
- focused validation commands;
- concise completion-report requirements.

Do not reproduce large architecture or policy documents when a path or link is enough. Target at most 500 words for a normal worker handoff, excluding paths and commands; exceed that only when the contract genuinely cannot be expressed safely within the limit.

## High-risk mutation surface

For lifecycle/state, transactions, idempotency, auth, payments, or another material invariant, the worker should first identify every relevant writer of the protected state inside the bounded area, including adjacent existing flows. A new guarded path is insufficient if another existing path can bypass the same invariant. Focused tests should cover each material mutation path, failure contract, and concurrency/atomicity behavior named by the specification.

## Context discipline

Batch related searches and reads when practical. Do not repeatedly reread unchanged files, rerun an already-passing broad suite during debugging, or expand repository discovery without a concrete failing dependency. Prefer focused tests during iteration and one broad validation at the end. If the same failure survives two targeted debug attempts, return the evidence as a blocker rather than starting open-ended discovery.

Avoid splitting one vertical feature into separate workers for DTOs, entities, services, controllers, UI, and tests unless those pieces are genuinely independent. Each additional dispatch creates context and coordination overhead.

After dispatch, let the worker finish. Do not poll for routine progress or perform overlapping repository investigation while the worker owns the bundle. Prefer a blocking host wait when available.

Use one writer by default. Parallelize only when tasks are independent, write sets are disjoint, and separate workspaces are verified.

If the worker discovers a material contract conflict or needs a product, architecture, security, or shared-interface decision, it should stop and return one batched blocker report.
