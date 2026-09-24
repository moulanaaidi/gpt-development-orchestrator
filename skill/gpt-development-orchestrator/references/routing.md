# Model Routing

Choose by task risk and complexity, not by a fixed ladder or model name alone. Before routing, inspect the current host's available models, native delegation tools, and supported model-override values. Treat role names as intent labels; use only exact capabilities the host exposes. Never guess an unavailable model or route through an unapproved external service.

| Role intent | Suitable work |
| --- | --- |
| Sol controller | Repository orientation, requirements, architecture, design, task decomposition, ambiguous or critical decisions, integration, and final review. Keep trivial edits local. |
| Terra-class worker | High-risk or difficult implementation, cross-module behavior, security boundaries, authentication/authorization, payments, migrations, concurrency, native lifecycle, or hard debugging. |
| Luna-class worker | Normal bounded implementation, UI flows/components, API wiring, focused refactors, accessibility, and ordinary tests. |
| Lower-cost GPT worker | Low-risk mechanical documentation, fixtures, repetitive tests, narrow transformations, or deterministic scaffolding. |

## Adapt to host capability

- If a preferred role/model is unavailable, reassess the task against available GPT-capable workers. Reduce scope, keep work with Sol, or ask for a decision if no safe route exists.
- Do not assume that a model available in one Codex session is available in another. Record the actual selected model in the plan or task result when useful.
- Delegate only when the work is bounded and independent review is worthwhile. Delegation overhead is not justified for every edit.
- Increase the level of review and validation as blast radius, uncertainty, or reversibility decreases.
