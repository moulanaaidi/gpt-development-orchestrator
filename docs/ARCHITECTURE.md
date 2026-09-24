# Architecture

## 1. Purpose

GPT Development Orchestrator is a reusable workflow package for substantial
software work in Codex. It separates planning and acceptance from bounded
implementation without introducing an external model router, background
service, or product-specific governance.

The first release optimizes for correctness, auditability, portability, and a
small maintenance surface.

## 2. Authority Model

The active Sol-class model is the controlling role. Sol owns:

- repository orientation and requirement clarification;
- product and technical design when design is part of the assignment;
- architecture, interfaces, invariants, and acceptance criteria;
- task decomposition and model selection;
- review of every delegated change;
- integration, correction decisions, and final reporting.

Workers do not redefine the plan or approve their own work. They implement a
bounded task brief and return evidence.

## 3. Model Routing

| Model | Default assignment |
| --- | --- |
| Terra-class worker | High-complexity or high-risk implementation, cross-module behavior, security, authentication, payments, migrations, concurrency, native lifecycle, or difficult debugging |
| Luna-class worker | Normal bounded implementation, UI components and flows, API wiring, focused refactors, accessibility, and ordinary tests |
| Approved lower-cost GPT worker | Low-risk mechanical work, fixtures, repetitive tests, narrow transformations, documentation normalization, and deterministic scaffolding |
| Sol-class controller | Planning, architecture, design, ambiguous or critical decisions, integration, and final review; trivial edits may remain local |

Routing is risk-based, not a reward hierarchy. Sol resolves role aliases against
the models actually exposed by the host and can raise a task whenever
uncertainty, blast radius, or review cost warrants it. An unavailable model is
never guessed or invoked through an unapproved external service.

## 4. Runtime Workflow

1. **Orient:** Sol reads repository policy, documentation, status, and the
   relevant implementation surface.
2. **Specify:** Sol writes a structured plan with boundaries, interfaces,
   acceptance criteria, validation commands, and risks.
3. **Validate:** The deterministic plan validator rejects missing or
   contradictory execution fields before delegation.
4. **Route:** Sol assigns each ready task to the least costly suitable model.
5. **Implement:** A worker changes only its declared write set and reports
   changed paths, commands, results, unresolved risks, and deviations.
6. **Review:** Sol inspects the actual diff and evidence first for specification
   compliance, then for quality, security, maintainability, and regressions.
7. **Correct:** Sol either fixes small issues directly or sends one consolidated
   correction brief to a worker. Additional cycles require a concrete reason.
8. **Integrate:** Sol runs repository-level validation and resolves interaction
   failures between otherwise valid task bundles.
9. **Continue:** Sol updates a checkpoint when work will span sessions or
   contexts, then reports the verified outcome.

## 5. Concurrency And Write Ownership

- One active writer owns a path at a time.
- Parallel tasks must have disjoint write sets and independently testable
  contracts.
- Shared contracts are defined before parallel implementation starts.
- Sol remains the integration owner and never delegates final acceptance.
- A worker must stop and report when a required change falls outside its write
  set or invalidates a plan assumption.

## 6. Components

### Codex Skill

`skill/gpt-development-orchestrator/` contains the discoverable workflow,
focused references, templates, and UI metadata. It tells Sol when and how to
orchestrate work while preserving normal Codex behavior for small tasks.

### Plan Contract

`schemas/plan.schema.json` defines the machine-readable task plan. The schema
captures task identity, readiness, dependencies, model assignment, write set,
acceptance criteria, validation, and risk. `tools/validate_plan.py` performs
schema-independent standard-library validation so installation has no runtime
package dependency.

### Safe Installer

`install.py` previews changes by default. `--apply` installs the versioned skill
and, when requested, a marked global policy block. Mutations are atomic,
backed up, and recorded in an undo receipt. The installer never reads secrets
or edits authentication state.

### Doctor

The doctor checks Python, source package integrity, installed skill integrity,
policy markers, configuration, and validator behavior. It reports actionable
failures and does not mutate the environment.

## 7. Safety Boundaries

The orchestrator does not imply permission to:

- commit, push, merge, publish, or deploy;
- create or rotate credentials;
- mutate production data or infrastructure;
- bypass repository policies or user approval requirements;
- expose secrets to workers or logs;
- let a worker broaden its own assignment.

External effects still require the authorization that the host Codex session
and target project require.

## 8. Portability

The implementation uses Python 3.11+ and the standard library, with explicit
Windows, macOS, and Linux path handling. The repository stores no machine-
specific absolute paths. Installation destinations are derived from
`CODEX_HOME`, then fall back to `~/.codex`.

## 9. Non-Goals For Version 0.1

- A hosted orchestration service or web dashboard.
- A separate model API gateway or billing layer.
- Custom agent TOML files whose host schema has not been verified.
- Autonomous background execution.
- Product-specific executive approval workflows.
- Automated source-control or production operations.
