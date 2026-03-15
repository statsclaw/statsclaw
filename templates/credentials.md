# Credential Verification

```
Target Repository: [owner/repo]
Remote URL Tested: [url]
Method: [PAT / SSH / gh-cli / env-token]
Test Command: git ls-remote [url]
Result: [PASS / FAIL]
Timestamp: [YYYY-MM-DD HH:MM]
```

## Verification Log

[Paste exact output of git ls-remote or error message here]

## Notes

- If FAIL: lead must ask user for credentials via AskUserQuestion before proceeding
- If PASS: workflow may proceed to CREATE RUN (step 4)
- This file is a hard gate for the entire workflow — no run may be created without PASS
