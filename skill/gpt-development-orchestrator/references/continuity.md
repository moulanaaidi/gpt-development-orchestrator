# Continuity

Create or update continuity state only when work is likely to cross sessions or models. Do not checkpoint every turn.

Keep the checkpoint concise (target 300 words) and record only:

- objective/current status;
- decisions or assumptions that still affect implementation;
- completed work and verified evidence;
- active owner/write scope;
- pending dependencies/blockers;
- checks run and known gaps;
- correction count and host-reported usage when available;
- next concrete action and authorization boundary.

Reference authoritative artifacts by path instead of copying them. Never include secrets or credentials. A checkpoint transfers context; it does not create authorization or override newer user direction.
