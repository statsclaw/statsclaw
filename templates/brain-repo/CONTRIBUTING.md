# Contributing to StatsClaw Brain

## How Contributions Work

This repo is **admin-curated**. You cannot submit PRs directly here. Instead:

1. Enable Brain mode in your StatsClaw session
2. The distiller agent extracts reusable knowledge from your workflows
3. You review and approve the entries (mandatory — nothing is shared without your consent)
4. Your contribution is submitted to [statsclaw/brain-seedbank](https://github.com/statsclaw/brain-seedbank)
5. Admin reviews and transfers accepted entries to this repo

## Quality Standards

Every knowledge entry must meet ALL of these criteria:

1. **Reusable** — useful beyond one specific project
2. **Non-trivial** — requires expertise; a skilled developer wouldn't already know this
3. **Privacy-scrubbed** — zero identifying information (see below)
4. **Correct** — technically accurate, validated in a real workflow
5. **Novel** — not duplicating an existing entry

## Privacy Rules

Entries MUST NOT contain:

- GitHub usernames, repo names, org names, or personal names
- File paths, directory structures, or specific package names
- Issue/PR numbers, commit SHAs, branch names, or GitHub URLs
- Email addresses or any other personal identifiers
- Proprietary code, algorithms, or business logic
- Dataset names, column names, or data file paths

Entries MAY contain:

- Mathematical formulas and statistical methods
- Generic algorithm descriptions and pseudocode
- Coding patterns with placeholder names (e.g., `my_estimator()`, `helper_function()`)
- Performance insights and complexity analysis
- Tolerance calibrations and convergence thresholds
- Well-known public library APIs (e.g., numpy, dplyr)

## Reporting Issues

If you find an entry with privacy violations or quality issues, please report it at [statsclaw/brain-seedbank issues](https://github.com/statsclaw/brain-seedbank/issues).
