# Lead Input

Use this template to understand what `lead` is allowed to consume before planning or routing work.

## Required Inputs

- user request
- `.statsclaw/CONTEXT.md`
- active package context under `.statsclaw/packages/`
- active run status if continuing work

## Shared Runtime Templates Used

- `templates/context.md`
- `templates/package.md`
- `templates/status.md`
- `templates/task.md`
- `templates/mailbox.md`
- `templates/lock.md`

## Optional Inputs

- `.statsclaw/runs/<request-id>/github.md`
- target repo metadata needed for profile detection
- normalized GitHub URL or repository reference
- target checkout path and remote verification state

## Required Decisions

- target package and profile
- target repository identity and local checkout path
- acceptance criteria
- workflow path
- required teammates
- isolation mode: worktrees or locks

## Must Not Decide Twice

- request scope after it is written
- impact map after it is written unless the request actually changed

## Hard Gate

- do not route implementation, validation, or ship work until the target repository exists locally and the repo boundary is recorded
