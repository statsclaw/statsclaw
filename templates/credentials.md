# Credential Verification

```
Target Repository: [owner/repo]
Remote URL Tested: [url]
Method: [PAT / SSH / gh-cli / env-token]
Test Command: git push --dry-run origin [branch]
Test Location: [path to target repo checkout — MUST be the target repo, NOT StatsClaw]
Result: [PASS / FAIL]
Timestamp: [YYYY-MM-DD HH:MM]
```

## Verification Log

[Paste exact output of git push --dry-run or git ls-remote here]

## Permissions Verified

- [ ] Write access confirmed (`git push --dry-run` succeeded in target repo checkout)
- [ ] Read access confirmed (`git ls-remote` succeeded)

## Notes

- If FAIL: lead must ask user for credentials via AskUserQuestion before proceeding
- If PASS: workflow may proceed to PLANNED (step 5)
- **This file is a hard gate** — no teammates may be dispatched without PASS
- **PASS must be against the actual target repo** — a PASS on a different repo is INVALID
