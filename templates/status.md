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

## State Machine (Two-Pipeline Architecture)

```
CREDENTIALS_VERIFIED → NEW → PLANNED → SPEC_READY → PIPELINES_COMPLETE → DOCUMENTED? → REVIEW_PASSED → READY_TO_SHIP → DONE
```

- `SPEC_READY` requires BOTH `spec.md` AND `test-spec.md` from theorist
- `PIPELINES_COMPLETE` requires BOTH `implementation.md` (builder) AND `audit.md` (auditor)
- Builder and auditor run in parallel after SPEC_READY

## Ownership Ledger

| Artifact | Owner | Pipeline | State | Completed |
| --- | --- | --- | --- | --- |
| credentials.md | lead | — | pending | |
| request.md | lead | — | pending | |
| impact.md | lead | — | pending | |
| comprehension.md | theorist | Comprehension | pending | |
| spec.md | theorist | → Code | pending | |
| test-spec.md | theorist | → Test | pending | |
| implementation.md | builder | Code | pending | |
| audit.md | auditor | Test | pending | |
| architecture.md | scribe | Architecture | pending | |
| docs.md | scribe | Code | pending | |
| review.md | skeptic | Convergence | pending | |
| github.md | github | — | pending | |

## Pipeline Isolation Status

| Check | Status |
| --- | --- |
| Builder received only spec.md (not test-spec.md) | pending |
| Auditor received only test-spec.md (not spec.md) | pending |
| Skeptic received ALL artifacts from both pipelines | pending |

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
