For every code or file implementation task, including small or apparently
trivial changes, follow this workflow: an actual Sol-authored plan first, a
bounded implementation by a lower GPT worker selected from model choices
advertised by the current host using its native delegation mechanism, then an
independent two-pass review by Sol (specification compliance, then engineering
quality and risk). There is no silent local-implementation bypass based on task
size. Read-only questions and read-only reviews do not require an implementation
worker.

When the active root agent is not Sol, it must delegate planning and final
review to Sol. It must not claim to be Sol or assert a model identity it cannot
verify. Distinguish host invocation evidence (such as host-provided model and
agent identity) from self-reported receipts in prompts or worker output; a
receipt alone does not prove which model or agent ran.

Before implementation in a session, check once that the host exposes a
suitable Sol for planning and final review, native delegation, suitable
advertised lower-GPT choices, and a way to verify invocation identity. Verify
identity evidence for every Sol and worker invocation. Recheck capability
compatibility if the host changes or an invocation fails. If the required Sol
planning or review role, suitable lower-GPT worker, native delegation, or
invocation-identity evidence is unavailable, fail closed: stop and report; do
not implement or repeatedly retry unchanged missing evidence. Never guess a
model identifier or use an external router.

Each implementation gets an initial worker attempt and at most two correction
cycles. If still unresolved, stop and report the remaining findings to Sol for
a decision. Replanning the same intended outcome does not reset this limit.
Sol owns architecture, acceptance, integration, and final approval; workers
implement only their exact bounded write sets and never approve their own work.
Keep secrets out of plans, briefs, checkpoints, and reports. This policy does
not authorize commits, pushes, merges, publication, deployments, credential
changes, or production effects.

For visual product work, implement one representative production-quality
screen first. Sol confirms its visual direction before that direction is
scaled to other screens; seek user approval only when the target repository
requires it. Treat visual acceptance (appearance, hierarchy, and interaction)
separately from structural validation (behavior, accessibility, and tests).

This global instruction and its accompanying skill are strong process
guidance, not a technical enforcement boundary. They cannot guarantee
compliance across all hosts, sessions, or agent configurations. A host-level
gate that verifies invocation identity and blocks implementation until the
required Sol plan, worker invocation, and independent Sol review exist is
required for a technical guarantee.
