# Builder Input (Code Pipeline)

Use this template to define what `builder` may consume before editing code.

## Required Inputs

- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md`
- `.statsclaw/runs/<request-id>/spec.md` (from theorist — implementation specification)
- `.statsclaw/runs/<request-id>/mailbox.md`
- assigned task record

## Forbidden Inputs (Pipeline Isolation)

- `.statsclaw/runs/<request-id>/test-spec.md` — NEVER read (belongs to test pipeline)
- `.statsclaw/runs/<request-id>/audit.md` — NEVER read (test pipeline output)

## Required Preconditions

- spec.md exists and contains implementation specification
- assigned write paths are explicit
- required lock is assigned
- no broader repo scan is needed
