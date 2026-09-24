# GPT Development Orchestrator

A reusable, GPT-only development workflow for Codex projects.

Sol owns the actual plan, architecture, design, routing, integration, and
independent final review. Every code or file implementation task, including
small changes, is implemented by a bounded lower-GPT worker selected from
current host-advertised choices and invoked through native delegation. Check
host capability compatibility once per session, verify identity for each
invocation, and refresh compatibility only after a host change or invocation
failure. Missing evidence means fail fast, not repeated retries or a local
implementation fallback. Read-only questions and reviews need no worker.

An implementation has one initial attempt and at most two correction cycles;
replanning the same outcome does not reset the limit. For visual product work,
Sol approves the direction of one representative production-quality screen
before that direction is scaled. User approval is needed only when the target
repository requires it. Visual acceptance is assessed separately from
structural validation. Worker briefs stay compact and link to authoritative
repository documents instead of repeating their contents.

It is product-neutral. Approval rules and business governance remain in each
target repository.

## What It Provides

- A Codex skill with Sol-led planning, delegation, review, and continuity.
- Session-specific routing that considers task quality, capability, reasoning,
  expected review and retry effort, and cost information when available.
- A strict JSON plan contract and standard-library validator.
- A preview-first installer with explicitly requested global policy integration, atomic writes,
  backups, receipts, and guarded undo.
- A read-only doctor and an automated CLI lifecycle test.

It never grants permission to commit, push, deploy, change credentials, or
perform production operations.

## Requirements

- Python 3.11 or newer.
- A Codex host that supports skills.
- A host with suitable Sol and lower-GPT workers, advertised model choices, and
  native delegation is required for implementation tasks. When any prerequisite
  is missing, the workflow stops and explains the blocker.

The runtime uses only the Python standard library.

## Install

Installation targets `CODEX_HOME` when set, otherwise `~/.codex`. Every install
previews by default and makes no changes.

```powershell
python install.py
```

Apply the skill only:

```powershell
python install.py --apply
```

Apply the skill and explicitly add the owned orchestration block to global
`AGENTS.md`:

```powershell
python install.py --with-policy --apply
```

The policy option preserves content outside its begin/end markers. Applied
changes produce a receipt under
`$CODEX_HOME/.gpt-development-orchestrator/receipts/`.

The global policy is opt-in during installation. Once adopted, doctor reports
missing or stale owned policy as a failure. The policy and skill are strong
process guidance, not technical enforcement across every host or session; a
host-level gate that verifies invocation identity and workflow state is needed
for a technical guarantee.

## Verify And Undo

```powershell
python install.py doctor
python install.py doctor --json
python install.py doctor --policy-file <policy-source>
python install.py undo --receipt <receipt-path>
python install.py undo --receipt <receipt-path> --apply
```

Undo also previews by default. It refuses to overwrite a skill or policy that
changed after the receipt was created.

Doctor compares the installed policy with the same source used by install:
`<source-skill>/../../POLICY.md`. Pass `--policy-file` when installation used a
custom policy source.

## Use

Start a new Codex session after installation. Invoke the skill explicitly with:

```text
$gpt-development-orchestrator plan and execute this development task.
```

The skill governs every code or file implementation task. No implementation
task bypasses the Sol-plan, worker, and independent-Sol-review workflow based
on size.

Validate a machine-readable plan without executing any command in it:

```powershell
python tools/validate_plan.py examples/valid-plan.json
```

The example uses illustrative model IDs. Replace its `model_registry` and task
model IDs with models exposed by your current Codex host before delegation.
The validator checks internal consistency; it cannot query live availability,
prices, or measure answer quality. The skill makes the routing choice from host
descriptions and task evidence, then Sol reviews the result.

## Test

```powershell
python -m unittest discover -s tests -v
```

The suite covers the plan contract, dry-run behavior, installation, policy
ownership, integrity checks, concurrency changes, receipts, rollback, doctor,
idempotent reapply, and undo.

## Documentation

- `docs/ARCHITECTURE.md`: authority, workflow, components, and boundaries.
- `docs/IMPLEMENTATION-PLAN.md`: version 0.1 work packages and acceptance.
- `docs/DECISIONS.md`: architecture decisions and rationale.
- `docs/THREAT-MODEL.md`: assets, threats, controls, and residual risks.
- `CHECKPOINT.md`: current verified state and next action.

After review, record first-pass success, correction cycles, and usage only
when reported by the host; otherwise mark usage unknown. These workflow rules
are guidance, not host enforcement.
