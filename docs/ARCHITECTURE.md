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

For every code or file implementation task, including small tasks, a lower GPT
worker implements a bounded task brief and returns evidence. Workers do not
redefine the plan or approve their own work. Read-only questions and reviews do
not require a worker. A non-Sol root delegates plan authorship and final review
to Sol and must not claim Sol identity.

## 3. Model Routing

Sol is a responsibility in this workflow: planning, design, integration, and
final acceptance. Worker names do not encode a permanent intelligence or price
ranking. For each session, Sol reads the host's exact available model overrides,
descriptions, and supported reasoning levels. A plan records the selected IDs
as a session snapshot; the package itself has no versioned routing table.

For each bounded task, Sol sets a quality floor from risk, difficulty, and
acceptance checks. It then chooses among eligible models using host capability
descriptions, any disclosed usage or cost class, and observed results on similar
tasks. The estimate includes execution, review, retries, and integration. If
cost matters and the host has no figures, current official pricing can be
checked for the actual billing mode. API prices must not be used as Codex
subscription consumption estimates. Missing information stays unknown. Stronger
reasoning is used when necessary for the quality floor, rather than by default.

If a suitable Sol, lower GPT worker, native delegation mechanism, or adequate
host identity evidence is unavailable, implementation fails closed. Never
guess model IDs or use an external router. Host-provided invocation evidence is
distinct from self-reported receipts; receipts alone do not prove identity.

After review, Sol records whether the first attempt passed and the corrections
required. This informs later comparable tasks without creating a permanent
ranking from one outcome. One or two independent workers are normally enough;
parallelism is optional, but worker implementation is mandatory for every task.

## 4. Runtime Workflow

1. **Orient:** Sol reads repository policy, documentation, status, and the
   relevant implementation surface.
2. **Specify:** Sol writes a structured plan with boundaries, interfaces,
   acceptance criteria, validation commands, and risks.
3. **Validate:** The deterministic plan validator rejects missing or
   contradictory execution fields before delegation.
4. **Route:** Sol selects an available model likely to clear the task's quality
   floor with the lowest expected total effort, recording uncertainty.
5. **Implement:** A worker changes only its declared write set and reports
   changed paths, commands, results, unresolved risks, and deviations.
6. **Review:** Sol independently inspects every actual diff and evidence first
   for specification compliance, then for quality, security, maintainability,
   and regressions.
7. **Correct:** Sol sends a consolidated correction brief to a worker for any
   required implementation changes. Additional cycles require a concrete reason.
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
focused references, templates, and UI metadata. It requires orchestration for
all implementation tasks, including small tasks.

### Plan Contract

`schemas/plan.schema.json` defines the machine-readable task plan. The schema
captures task identity, readiness, dependencies, session model assignment,
optional routing evidence, write set, acceptance criteria, validation, and risk.
`tools/validate_plan.py` performs
schema-independent standard-library validation so installation has no runtime
package dependency.

### Safe Installer

`install.py` previews changes by default. `--apply` installs the versioned skill
and, when requested, a marked global policy block. Mutations are atomic,
backed up, and recorded in an undo receipt. The installer never reads secrets
or edits authentication state.

### Doctor

The doctor checks Python, source package integrity, installed skill integrity,
the exact installed global policy against its source, configuration, and
validator behavior. Missing or stale owned policy fails strict-workflow
diagnostics. It reports actionable failures and does not mutate the environment.

The global instruction and skill are strong process guidance, not technical
hard enforcement across all hosts or sessions. A host-level gate that verifies
invocation identity and blocks implementation until the required Sol plan,
worker invocation, and independent Sol review exist is required for a
technical guarantee.

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
