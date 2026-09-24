# Continuity

For work likely to outlive the current session, keep one concise checkpoint in the target repository's agreed location. Update it after a meaningful plan, implementation, or review milestone, and before handing work to another model or session.

Record:

- objective and current status;
- decisions and assumptions that affect implementation;
- completed work and verified evidence;
- active task, owner/model, and write set;
- pending tasks, dependencies, and blockers;
- tests run, results, and known gaps;
- whether the initial implementation met acceptance, correction count, and
  usage reported by the host (otherwise `unknown`);
- the next concrete action and any authorization boundary.

Use [../templates/checkpoint.md](../templates/checkpoint.md) as a starting point. Prefer links to authoritative repository documents over copying their full contents. Never include secrets, tokens, or credential values. A checkpoint transfers context; it does not create new authorization or override newer user direction.
