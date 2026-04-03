# Branch Protection — statsclaw/brain

## Branch Model

Single branch: `main`. Admin-only push.

```
main ← curated knowledge (admin pushes approved entries)
```

## Protection Rules

| Rule | Setting | Rationale |
| --- | --- | --- |
| Require pull request | **No** | Admin pushes directly when transferring from brain-seedbank |
| Allow force pushes | **No** | Protect history |
| Allow deletions | **No** | Protect main |
| Restrict push access | **Yes — admin only** | Only @xuyiqing can push |

## How Entries Arrive

1. Users contribute via PRs to `statsclaw/brain-seedbank`
2. Admin reviews and merges PRs on brain-seedbank
3. Admin copies approved entries to this repo, commits, and pushes to main
4. Admin updates CONTRIBUTORS.md with badges
