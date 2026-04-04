<div align="center">

<img src="https://avatars.githubusercontent.com/u/271365820?s=120" alt="StatsClaw" width="120">

# StatsClaw Brain Seedbank

**Contribution staging — submit knowledge entries here via PR**

[StatsClaw](https://github.com/statsclaw/statsclaw) · [Brain (curated)](https://github.com/statsclaw/brain) · [How to Contribute](CONTRIBUTING.md)

</div>

---

The contribution staging repo for [StatsClaw Brain](https://github.com/statsclaw/brain). When StatsClaw users opt into Brain mode, noteworthy knowledge from their workflows is extracted, privacy-scrubbed, and submitted here as PRs. Admin reviews contributions and transfers accepted entries to the curated `statsclaw/brain` repo.

## How It Works

```
Your StatsClaw workflow          OR          /contribute command
        │                                        │
        ▼                                        ▼
  Distiller agent extracts knowledge    Distiller summarizes session lessons
        │                                        │
        └────────────┬───────────────────────────┘
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

### Two Ways to Contribute

1. **Automatic** — After noteworthy workflows, StatsClaw automatically extracts knowledge and asks for your consent
2. **Manual** — Run `/contribute` at any time to summarize what you learned during your session — what worked, what required manual intervention, and what domain-specific patterns emerged — and submit it as a structured report

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
