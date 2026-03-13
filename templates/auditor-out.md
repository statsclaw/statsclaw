# Auditor Output

Use this template to define what `auditor` must produce.

## Required Outputs

- `.statsclaw/runs/<request-id>/audit.md`
- append-only mailbox note for failing checks, routes, or handoff

## Required Content

- commands run
- exact evidence
- failures and routes
- validation verdict

## Success Condition

`skeptic` can judge whether the evidence is sufficient without rerunning the whole validation stage by default.
