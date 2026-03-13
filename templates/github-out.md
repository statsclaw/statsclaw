# GitHub Output

Use this template to define what `github` must produce.

## Required Outputs

- `.statsclaw/runs/<request-id>/github.md`
- append-only mailbox note when external state changes affect the team

## Required Content

- normalized issue or PR input when work enters the workflow
- target repository owner, name, branch, and local checkout path when applicable
- acquisition or verification result for the target repository
- external ship actions when explicitly requested
- follow-up notes for branch, PR, or issue comment state

## Success Condition

`lead` or the user can understand the external repository state without re-querying GitHub immediately, and the run knows whether it is safe to continue into target-repository work.
