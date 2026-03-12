# StatsClaw Local Context

```yaml
ActivePackage: .statsclaw/packages/example-package.md
ActiveRun: ""
DefaultWorkflow: standard
DefaultProfile: ""
GitHubIssueSchedule: ""
GitHubIssueFilter: ""
GitHubAutoSolve: ""
LastGitHubIssueScanAt: ""
```

## Notes

- This file is auto-managed by StatsClaw.
- `ActivePackage` points to the project context currently in use.
- `ActiveRun` may be left empty until `triage` creates a request run.
- `DefaultWorkflow` is optional and can remain `standard`.
- `DefaultProfile` may be left empty and inferred from the project.
- `GitHubIssueSchedule` may store a schedule like `daily 00:00 America/Los_Angeles`.
- `GitHubIssueFilter` may store a normalized issue filter such as `label:bug` or `is:open label:bug`.
- `GitHubAutoSolve` may store `true` or `false`.
- `LastGitHubIssueScanAt` records the most recent completed scan.
