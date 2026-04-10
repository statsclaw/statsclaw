# Branch Protection — statsclaw/brain-seedbank

## Branch Model

Single branch: `main`. Protected — changes via PR only (fork-based).

```
main ── contributions land here via PR
 ▲
 │  PR (fork-based)
 │
user's fork → branch → PR to main
```

## Protection Rules

| Rule | Setting | Rationale |
| --- | --- | --- |
| Require pull request | **Yes** | All contributions via PR |
| Required approvals | **1** (@xuyiqing) | Admin reviews every contribution |
| Require status checks to pass | **Yes** | CI validates entry format and PII |
| Required status checks | `Validate entries` | Must pass before merge |
| Allow force pushes | **No** | Protect history |
| Allow deletions | **No** | Protect main |
