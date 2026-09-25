# Development Checkpoint

## Current objective

Version 0.2 is being prepared on branch `v0.2-thin-root`.

The workflow is being changed from strict orchestration of every implementation task to a thin-root model inspired by Astra Flash Orchestrator:

```text
Planner plans once -> GPT-6 Luna implements/tests/debugs -> Reviewer reviews once
```

An approved external specification can bypass in-Codex planning entirely and be implemented directly in a GPT-6 Luna session.

## Completed on the branch

- Rewrote `POLICY.md` for substantial-work-only thin-root orchestration.
- Rewrote worker instructions so Luna owns repository discovery, implementation, testing, debugging, and routine verification inside scope.
- Rewrote `SKILL.md` with external-spec and in-Codex paths.
- Removed per-task model-ranking guidance from runtime routing; Luna is the default worker.
- Changed review guidance to two lenses in one batched pass.
- Changed normal correction budget to one cycle.
- Added explicit no-polling and coherent-bundle guidance.
- Updated README, architecture decisions, templates, changelog, and workflow-contract tests.

## Preserved

- Preview-first installer.
- Optional global policy installation.
- Backups, receipts, guarded undo, and doctor.
- JSON plan schema and validator as optional tooling.
- No automatic commit/push/deploy/credential/production authorization.

## Validation status

The branch content and workflow contract were reviewed through the GitHub connector. A full local test run could not be executed from this ChatGPT environment because the container has no direct network access to clone the GitHub branch.

The unchanged installer/validator implementation is not expected to be affected by the documentation/runtime-contract rewrite, but the full suite should be run locally before merge:

```powershell
python -m unittest discover -s tests -v
```

## Next action

Run the full test suite in the repository checkout, inspect any failures caused by the old v0.1 workflow expectations, then merge the v0.2 branch after review.
