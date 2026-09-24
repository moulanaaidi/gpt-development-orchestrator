# Threat Model

## Assets

- Existing user instructions in `$CODEX_HOME/AGENTS.md`.
- Existing personal skills and Codex configuration.
- Source repositories delegated workers can modify.
- Credentials and authentication material stored near Codex configuration.
- The integrity of plans, task boundaries, evidence, and undo receipts.

## Trust Boundaries

Sol is trusted to define scope and accept work. Workers are trusted only inside
their explicit task and write set. The installer is trusted only for the target
paths it previews. Plan files and undo receipts are untrusted input and must be
validated before they influence file operations.

## Principal Threats And Controls

| Threat | Required control |
| --- | --- |
| Installer overwrites unrelated global instructions | Edit only an owned marker block; preserve all surrounding bytes where practical; back up before mutation |
| Crafted destination or receipt escapes Codex home | Resolve paths and enforce containment before writes, restores, or removal |
| Partial write corrupts configuration | Write a sibling temporary file, flush it, then atomically replace the target |
| Repeated installation duplicates policy | Marker-aware idempotent replacement and content comparison |
| Undo destroys newer user changes | Receipt records before/after digests; refuse unsafe restore unless the current managed artifact matches the receipt |
| Source symlink or special file redirects copying | Reject unsupported file types and validate copied relative paths |
| Secrets leak into logs or workers | Never read `auth.json`, environment secret values, credential stores, or unrelated configuration; output paths and statuses only |
| Worker modifies undeclared files | Explicit write sets, one owner per path, worker evidence, and Sol diff review |
| Parallel workers overwrite each other | Validator detects intersecting write sets inside a parallel group; Sol defines shared contracts first |
| Malicious or stale plan triggers unsafe action | Strict plan schema, known roles/models, dependency validation, and no plan-driven shell execution |
| Validation command becomes arbitrary execution | Commands remain review information; the plan validator does not execute them |
| Delegation silently gains external authority | No automatic commits, pushes, deployments, credentials, or production mutations |

## Installer Invariants

1. Dry run is the default and has no filesystem side effects.
2. Mutation requires an explicit apply operation.
3. Every changed pre-existing file has recoverable prior content.
4. Every created or replaced artifact is listed in an undo receipt.
5. Undo validates the receipt and current artifact state before mutation.
6. No operation traverses outside the resolved Codex home and repository source.
7. Diagnostics are read-only.

## Residual Risks

- A capable worker can still produce a logically incorrect patch inside its
  write set. Sol review and repository tests reduce but cannot eliminate this.
- Global instructions can interact with later Codex versions. The installer is
  reversible, and the skill must be tested again when host behavior changes.
- Model names and capabilities are host-dependent. Routing must discover or use
  configured available models rather than assuming a historical model exists.
