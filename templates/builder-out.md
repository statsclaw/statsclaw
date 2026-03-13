# Builder Output

Use this template to define what `builder` must produce after implementation.

## Required Outputs

- target source and test changes inside the assigned write surface
- `.statsclaw/runs/<request-id>/implementation.md`
- append-only mailbox note for interface changes, blockers, or handoff

## Required Content

- changed files and why
- behavior changes
- test updates
- unresolved implementation risks

## Success Condition

`auditor` can validate the change without rediscovering intent or file ownership.
