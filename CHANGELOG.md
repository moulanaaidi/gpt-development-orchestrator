# Changelog

## Unreleased

### Token-budget v0.3

- Reduced always-loaded orchestration text while preserving the Sol planner/reviewer and Luna implementation split.
- Made direct Luna implementation the preferred path when an approved specification already exists.
- Added spec-by-reference guidance to avoid repeatedly pasting large workpacks into worker/reviewer prompts.
- Added explicit transcript, repository-discovery, test-log, checkpoint, and completion-report token discipline.
- Added prompt-size regression tests so the core skill, global policy, worker instructions, and task brief do not silently grow without review.

## v0.2

- Reworked the workflow into a thin-root architecture.
- Reused approved external specifications instead of forcing replanning.
- Added a dedicated GPT-6 Luna implementation worker role.
- Consolidated review into one batched independent acceptance pass.
- Defaulted to one correction cycle and removed routine polling/model-ranking overhead.
- Added installer lifecycle and workflow-contract tests.

See repository history for earlier changes.
