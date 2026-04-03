# StatsClaw Brain Seedbank

The contribution staging repo for [StatsClaw Brain](https://github.com/statsclaw/brain). When StatsClaw users opt into Brain mode, noteworthy knowledge from their workflows is extracted, privacy-scrubbed, and submitted here as PRs. Admin reviews contributions and transfers accepted entries to the curated `statsclaw/brain` repo.

## How It Works

```
Your StatsClaw workflow
        │
        ▼
  Distiller agent extracts knowledge
        │
        ▼
  You review and approve (mandatory)
        │
        ▼
  PR created here (brain-seedbank)  ──→  Admin reviews  ──→  statsclaw/brain
        │                                                          │
        ▼                                                          ▼
  Public, transparent                                    Curated knowledge
  (everyone can see who contributed what)                (agents read from here)
```

## Privacy Guarantees

Every contribution is automatically privacy-scrubbed before submission:

- **Stripped**: repo names, file paths, usernames, org names, GitHub URLs, issue numbers, commit SHAs, email addresses, dataset names, proprietary code
- **Kept**: mathematical formulas, statistical methods, algorithms, generic coding patterns, performance insights
- **Genericized**: project-specific names → placeholder names (e.g., `my_estimator()`)

CI validates every PR for common PII patterns. See [CONTRIBUTING.md](CONTRIBUTING.md) for full rules.

## Badge Rewards

Accepted contributions earn a virtual badge on [statsclaw/brain CONTRIBUTORS.md](https://github.com/statsclaw/brain/blob/main/CONTRIBUTORS.md). See the badge tiers there.

## For Admins

1. Review incoming PRs for quality and privacy compliance
2. Merge acceptable PRs to main
3. Transfer approved entries to `statsclaw/brain` (copy files, commit, push)
4. Update `statsclaw/brain/CONTRIBUTORS.md` with badges

## License

Contributions are shared under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
