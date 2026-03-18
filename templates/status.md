# Run Status

```
Request ID: [request-id]
Package: [package-name]
Current State: NEW
Current Owner: leader
Next Step: [action]
Active Profile: [profile]
Target Repository: [owner/repo or local path]
Target Checkout: [absolute path]
Credentials: [VERIFIED / NOT_VERIFIED]
Credential Method: [PAT / SSH / gh-cli / env-token]
Last Updated: [YYYY-MM-DD HH:MM]
```

## State Machine (Two-Pipeline Architecture)

```
CREDENTIALS_VERIFIED → NEW → PLANNED → SPEC_READY → PIPELINES_COMPLETE → DOCUMENTED → REVIEW_PASSED → READY_TO_SHIP → DONE
```

- `SPEC_READY` requires `comprehension.md`, `spec.md`, AND `test-spec.md` from planner
- `PIPELINES_COMPLETE` requires BOTH `implementation.md` (builder) AND `audit.md` (tester)
- Builder and tester run in parallel after SPEC_READY

Interrupt states:
- `HOLD` — waiting for user input (only user can unblock)
- `BLOCKED` — tester validation failed (respawn upstream teammate)
- `STOPPED` — reviewer quality gate failed (respawn per routing)

## Ownership Ledger

| Artifact | Owner | Pipeline | State | Completed |
| --- | --- | --- | --- | --- |
| credentials.md | leader | — | pending | |
| request.md | leader | — | pending | |
| impact.md | leader | — | pending | |
| comprehension.md | planner | Comprehension | pending | |
| spec.md | planner | → Code | pending | |
| test-spec.md | planner | → Test | pending | |
| implementation.md | builder | Code | pending | |
| audit.md | tester | Test | pending | |
| architecture.md | recorder | Architecture | pending | |
| log-entry.md | recorder | Process Record | pending | |
| docs.md | recorder | Code | pending | |
| review.md | reviewer | Convergence | pending | |
| shipper.md | shipper | — | pending | |

## Pipeline Isolation Status

| Check | Status |
| --- | --- |
| Builder received only spec.md (not test-spec.md) | pending |
| Tester received only test-spec.md (not spec.md) | pending |
| Reviewer received ALL artifacts from both pipelines | pending |

## Active Isolation

| Teammate | Isolation | Worktree Path |
| --- | --- | --- |
| builder | worktree | |
| recorder | worktree | |

## Open Risks

_No open risks._

## Blocking Reason

_Not blocked._

## Repo Boundary

- Framework repo: StatsClaw (runtime state only, no target code changes)
- Target repo: [target repository] (code + user-facing docs only)
- Brain repo: [owner]/statsclaw-brain (workflow logs, architecture diagrams, process records)
- Ship target: [target repository]

## Persistence Rule

All state transitions must be written to this file immediately. Only `leader` may update this file.
