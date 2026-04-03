# Contributing to StatsClaw Brain Seedbank

## How to Contribute

Contributions are automated through StatsClaw:

1. **Enable Brain mode** when prompted at session start
2. **Do your work** — StatsClaw handles the rest
3. **Review the extraction** — after noteworthy workflows, StatsClaw shows you the extracted knowledge and asks your permission
4. **Approve or decline** — nothing is shared without your explicit consent
5. **PR is created automatically** — StatsClaw creates a PR from your fork to this repo
6. **Admin reviews** — accepted entries are transferred to `statsclaw/brain`

## Quality Criteria (The 5-Question Gate)

Every knowledge entry must pass ALL five questions:

| # | Question | If NO |
| --- | --- | --- |
| 1 | Is this reusable beyond one specific project? | Entry rejected |
| 2 | Is this non-trivial (requires expertise)? | Entry rejected |
| 3 | Has all identifying info been removed? | Entry rejected |
| 4 | Is this technically correct (validated in workflow)? | Entry rejected |
| 5 | Is this NOT a duplicate of existing brain entries? | Entry rejected |

## Privacy Scrub Checklist

Before submitting (automated by distiller, verified by reviewer):

- [ ] No GitHub usernames, repo names, or organization names
- [ ] No file paths, directory structures, or package names
- [ ] No issue/PR numbers, commit SHAs, or branch names
- [ ] No GitHub URLs or email addresses
- [ ] All code examples use generic placeholder names
- [ ] No dataset names, column names, or data file paths
- [ ] No proprietary algorithms or business logic

## What Makes a Good Contribution

**Good entries:**
- A mathematical insight about convergence properties of a class of estimators
- A numerical stability technique for matrix inversion in panel data models
- A DGP design pattern for heterogeneous treatment effects simulation
- A validation strategy for testing asymptotic properties in finite samples
- A performance optimization pattern for sparse matrix operations in R/Python

**Not good entries:**
- How to install a package (too trivial)
- A bug fix for a specific function (too project-specific)
- Configuration settings (not reusable knowledge)
- Copy-pasted documentation (not original insight)

## Reporting Issues

If you find a contribution with privacy violations or quality problems, [open an issue](https://github.com/statsclaw/brain-seedbank/issues/new?template=quality-report.yml).
