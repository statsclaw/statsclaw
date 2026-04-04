<div align="center">

<img src="https://avatars.githubusercontent.com/u/271365820?s=120" alt="StatsClaw" width="120">

# StatsClaw Brain

**Curated knowledge repository — reusable methods, patterns, and techniques contributed by the community**

[StatsClaw](https://github.com/statsclaw/statsclaw) · [Contribute](https://github.com/statsclaw/brain-seedbank) · [Leaderboard](CONTRIBUTORS.md)

</div>

---

The curated knowledge repository for [StatsClaw](https://github.com/statsclaw/statsclaw). This repo contains validated, privacy-scrubbed knowledge entries contributed by the StatsClaw community.

## What is this?

When StatsClaw users opt into Brain mode, their agents can read knowledge entries from this repo to enhance their capabilities — better math formulations, coding patterns, validation strategies, simulation designs, and more. Every entry here has been:

1. Extracted from a real workflow by the distiller agent
2. Privacy-scrubbed (no repo names, file paths, usernames, or proprietary code)
3. Approved by the contributing user
4. Reviewed and curated by admin

## How to Use

StatsClaw agents read from this repo automatically when Brain mode is enabled. You can also browse entries directly:

- `planner/` — Mathematical methods, statistical techniques, spec patterns
- `builder/` — Language-specific coding patterns, numerical stability, API design
- `tester/` — Validation strategies, tolerance calibration, benchmark patterns
- `simulator/` — DGP patterns, harness designs, convergence diagnostics
- `scriber/` — Architecture patterns, documentation styles
- `reviewer/` — Convergence failure patterns, quality checks
- `general/` — Cross-agent knowledge, language guides, debugging patterns

See `index.md` for a searchable index of all entries.

## How to Contribute

**Do NOT create PRs directly to this repo.** Contributions flow through [statsclaw/brain-seedbank](https://github.com/statsclaw/brain-seedbank):

**Automatic** — Use StatsClaw with Brain mode enabled. After noteworthy workflows, the distiller agent extracts knowledge automatically.

**Manual** — Run the `/contribute` command at any time during a session. It summarizes what you learned — what worked, what required manual intervention, and what domain-specific patterns emerged — and submits a structured report.

Either way:

1. The distiller agent extracts reusable knowledge
2. You review and approve the extracted entries — nothing is shared without your explicit consent
3. Your contribution is submitted as a PR to `statsclaw/brain-seedbank`
4. Admin reviews, then transfers accepted entries here

See [CONTRIBUTING.md](CONTRIBUTING.md) for quality standards.

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the badge leaderboard.

## License

Knowledge entries are shared under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
