# StatsClaw Local Context

```yaml
ActivePackage: .statsclaw/packages/example-package.md
ActiveRun: ""
DefaultWorkflow: agent-teams
DefaultProfile: ""
GitHubIssueSchedule: ""
GitHubIssueFilter: ""
GitHubAutoSolve: ""
GitHubScheduleMode: ""
GitHubScheduledPrompt: ""
LastGitHubIssueScanAt: ""
```

## Notes

- This file is auto-managed by StatsClaw.
- `ActivePackage` points to the project context currently in use.
- `ActiveRun` may be left empty until `lead` starts a request run.
- `DefaultWorkflow` is optional and can remain `agent-teams`.
- `DefaultProfile` may be left empty and inferred from the project.
- `GitHubIssueSchedule` may store a schedule like `daily 00:00 America/Los_Angeles`.
- `GitHubIssueFilter` may store a normalized issue filter such as `label:bug` or `is:open label:bug`.
- `GitHubAutoSolve` may store `true` or `false`.
- `GitHubScheduleMode` may store `desktop-scheduled-task`, `session-loop`, or `manual`.
- `GitHubScheduledPrompt` may store the exact prompt used for the native Claude Code scheduled task.
- `LastGitHubIssueScanAt` records the most recent completed scan.
- Team-based runs may maintain a shared task list under `.statsclaw/runs/<request-id>/tasks/` and a shared message log under `.statsclaw/runs/<request-id>/mailbox.md`.
- Hard-isolation runs may also maintain `.statsclaw/runs/<request-id>/locks/` so only one teammate owns a write surface at a time.
