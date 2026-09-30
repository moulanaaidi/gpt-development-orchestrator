# Planning

Planning removes product, architecture, contract, and acceptance ambiguity from implementation; it should not duplicate implementation detail.

Reuse approved repository plans and designs. For new substantial work, establish only:

- observable outcome and non-goals;
- authoritative paths/sections and relevant repository evidence;
- interfaces, invariants, data/API contracts, and failure behavior;
- material security/production constraints;
- bounded write scope;
- one coherent vertical bundle unless a real dependency boundary requires more;
- acceptance criteria and focused validation commands.

Prefer paths and anchors to copied prose. Prefer targeted searches/ranges to broad repository reads.

Target at most 600 words for the plan, excluding paths and commands. Expand only when necessary to make a material contract unambiguous.

A task is ready when GPT-6 Luna can discover local implementation details and make routine coding choices from repository conventions without inventing product or architecture decisions.
