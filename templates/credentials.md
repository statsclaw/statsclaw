# Credential Verification

## Target Repository (HARD GATE)

```
Target Repository: [owner/repo]
Remote URL Tested: [url]
Method: [PAT / SSH / gh-cli / env-token]
Test Command: git push --dry-run origin [branch]
Test Location: [path to target repo checkout — MUST be the target repo, NOT StatsClaw]
Result: [PASS / FAIL]
Timestamp: [YYYY-MM-DD HH:MM]
```

### Verification Log

[Paste exact output of git push --dry-run or git ls-remote here]

### Permissions Verified

- [ ] Write access confirmed (`git push --dry-run` succeeded in target repo checkout)
- [ ] Read access confirmed (`git ls-remote` succeeded)

## Workspace Repository (SOFT GATE — warning only)

```
Workspace Repository: [user-specified workspace repo, e.g. owner/workspace]
Workspace Repo Status: [PASS / FAIL / NOT_AVAILABLE]
Method: [same as target / separate]
Test Command: git push --dry-run origin main
Test Location: .repos/workspace
Result: [PASS / FAIL — reason]
Timestamp: [YYYY-MM-DD HH:MM]
User Notified: [yes / no — required if FAIL or NOT_AVAILABLE]
```

### Workspace Repo Notes

[If FAIL: reason for failure and confirmation that user was warned. If NOT_AVAILABLE: workspace repo could not be created — user was notified that workflow logs will not be recorded.]

## Gate Rules

- **Target repo**: HARD GATE — no teammates may be dispatched without PASS. PASS must be against the actual target repo.
- **Workspace repo**: SOFT GATE — workflow proceeds if FAIL, but user MUST be explicitly warned that logs will not be synced. Never silently skip.
- If target repo FAIL: leader must ask user for credentials via AskUserQuestion before proceeding
- If target repo PASS: workflow may proceed to PLANNED (step 5)
