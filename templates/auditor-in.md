# Auditor Input

Use this template to define what `auditor` may consume.

## Required Inputs

- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md`
- `.statsclaw/runs/<request-id>/test-spec.md` (from theorist — test pipeline specification)
- `.statsclaw/runs/<request-id>/mailbox.md`

## Forbidden Inputs (Pipeline Isolation)

- `.statsclaw/runs/<request-id>/spec.md` — NEVER read (belongs to code pipeline)
- `.statsclaw/runs/<request-id>/implementation.md` — NEVER read (belongs to code pipeline)

## Optional Inputs

- target repo source files (for understanding current behavior, NOT for implementation details)
- active profile (for validation commands)

## Required Preconditions

- test-spec.md exists and contains concrete test scenarios
- validation commands are known from profile or package context
- target repo has builder's changes merged back (worktree merge-back complete)
