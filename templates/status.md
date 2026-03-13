# Run Status

```
Request ID: [request-id]
Package: [package-name]
Current State: NEW
Current Owner: lead
Next Step: [action]
Active Profile: [profile]
Target Repository: [owner/repo or local path]
Target Checkout: [absolute path]
Credentials: [VERIFIED / NOT_VERIFIED]
Credential Method: [PAT / SSH / proxy / none]
Last Updated: [YYYY-MM-DD HH:MM]
```

## Ownership Ledger

| Artifact | Owner | State | Completed |
| --- | --- | --- | --- |
| credentials.md | lead | pending | |
| request.md | lead | pending | |
| impact.md | lead | pending | |
| spec.md | theorist | pending | |
| implementation.md | builder | pending | |
| audit.md | auditor | pending | |
| docs.md | scribe | pending | |
| review.md | skeptic | pending | |
| github.md | github | pending | |

## Active Isolation

| Teammate | Isolation | Worktree Path |
| --- | --- | --- |
| builder | worktree | |
| scribe | worktree | |

## Open Risks

_No open risks._

## Blocking Reason

_Not blocked._

## Repo Boundary

- Framework repo: StatsClaw (runtime state only, no target code changes)
- Target repo: [target repository]
- Ship target: [target repository]

## Persistence Rule

All state transitions must be written to this file immediately. Only `lead` may update this file.
