# Repository Context

```yaml
RepoName: ""
RepoURL: ""
RepoCheckout: ""
ActiveRun: ""
DefaultWorkflow: agent-teams
DefaultProfile: ""
DefaultBranch: "main"
Language: ""
Version: ""
CredentialStatus: ""          # PASS / FAIL / UNTESTED
CredentialMethod: ""          # PAT / SSH / gh-cli / env-token
CredentialVerifiedAt: ""      # YYYY-MM-DD HH:MM
CommitTrailers: "statsclaw"   # co-author trailers appended to commits; set to "" to disable
```

## Request Defaults

- Default acceptance criteria: all profile validation commands pass with zero errors
- Default write surface: determined by impact.md per run
- Default validation level: full (build + check + test)

## Key Functions

_List key public functions, entry points, or exported symbols relevant to ongoing work._

## Constraints

_List architectural constraints, compatibility requirements, or conventions that all runs must respect._

## Known Issues

_List known bugs, limitations, or technical debt relevant to planning._

## Session Notes

_No notes yet._
