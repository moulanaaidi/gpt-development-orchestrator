# Orchestration Policy

Use the `gpt-development-orchestrator` skill for substantial work when explicit planning, bounded implementation, and independent review add value. Handle small, self-contained, low-risk changes directly.

The active Sol-class model owns repository orientation, design, architecture, acceptance criteria, task/model selection, integration, and final review. Workers implement only ready, bounded tasks and return evidence. They do not redefine requirements, expand their write set, or approve their own work.

Before delegation, check the models and native delegation capabilities exposed by the current host. Select only available GPT models; never guess a model identifier or use an unapproved external router. Keep one writer per path. Parallel work requires disjoint write sets and settled shared interfaces.

Sol reviews every delegated diff in two passes: specification compliance, then engineering quality and risk. Sol integrates and records actual validation results. Follow repository-specific instructions and authorization requirements.

This policy does not authorize automatic commits, pushes, merges, publication, deployments, credential changes, or production effects. Do not put secrets in plans, worker briefs, checkpoints, or reports.
