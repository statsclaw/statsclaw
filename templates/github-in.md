# GitHub Input

Use this template to define what `github` may consume.

## Required Inputs

- `.statsclaw/CONTEXT.md`
- active package context
- `.statsclaw/runs/<request-id>/mailbox.md`
- target repository reference or GitHub URL when the run starts externally

## Optional Inputs

- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/review.md`
- target repository git and GitHub metadata

## Required Decision

- whether the task is issue intake, check inspection, or explicit ship work
- whether the target repository is available locally and verified as the correct checkout
