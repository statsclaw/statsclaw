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
| sim-spec.md | planner | → Simulation | pending | |
| implementation.md | builder | Code | pending | |
| simulation.md | simulator | Simulation | pending | |
| audit.md | tester | Test | pending | |
| ARCHITECTURE.md | scriber | Architecture | pending | |
| log-entry.md | scriber | Process Record | pending | |
| docs.md | scriber | Code | pending | |
| review.md | reviewer | Convergence | pending | |
| shipper.md | shipper | — | pending | |

## Pipeline Isolation Status

| Check | Status |
| --- | --- |
| Builder received only spec.md (not test-spec.md or sim-spec.md) | pending |
| Tester received only test-spec.md (not spec.md or sim-spec.md) | pending |
| Simulator received only sim-spec.md (not spec.md or test-spec.md) | pending |
| Reviewer received ALL artifacts from all pipelines | pending |

## Active Isolation

| Teammate | Isolation | Worktree Path |
| --- | --- | --- |
| builder | worktree | |
| simulator | worktree | |
| scriber | worktree | |

## Open Risks

_No open risks._

## Blocking Reason

_Not blocked._

## Repo Boundary

- Framework repo: StatsClaw (orchestration rules only, no runtime state, no target code changes)
- Target repo: [target repository] (code + user-facing docs only)
- Workspace repo: [user-specified workspace repo] (runtime state + workflow logs + process records)
- Runtime directory: .repos/workspace/[repo-name]/ (runs, logs, tmp)
- Ship target: [target repository]

## Persistence Rule

All state transitions must be written to this file immediately. Only `leader` may update this file.
