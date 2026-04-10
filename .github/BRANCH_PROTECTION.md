# Branch Protection & Branching Strategy

This document defines the branching model, protection rules, versioning scheme, and release process for StatsClaw.

---

## Branch Model

StatsClaw uses a simple two-branch model:

```
dev ──PR──▶ main
 ▲              │
 │              ▼
 │           releases (tags)
 │
all development
happens here
```

| Branch | Purpose | Protection |
| --- | --- | --- |
| `main` | Production-ready. Every commit is a tested, stable version of the framework. Only receives merges from `dev` via reviewed PRs. | Fully protected |
| `dev` | Active development. All changes land here first — features, fixes, docs, CI. PRs required. | PR + CI must pass |

### Flow

1. All development work happens on branches merged into `dev` via reviewed PRs
2. When `dev` is stable, create a PR from `dev` → `main`
3. PR requires: CI pass + 1 approval
4. Squash merge into `main`
5. Tag releases from `main`

No other long-lived branches. Feature branches are merged into `dev` via PRs, then deleted.

---

## Branch Protection Rules

### `main` Branch (Strict)

| Rule | Setting | Rationale |
| --- | --- | --- |
| Require pull request | **Yes** | No direct pushes — only from `dev` |
| Required approvals | **1** | Every promotion to production is reviewed |
| Dismiss stale reviews on push | **Yes** | New pushes require re-review |
| Require status checks to pass | **Yes** | CI must be green |
| Required status checks | `Validate structure`, `Lint Markdown`, `Validate YAML` | All 3 must pass |
| Require branches up to date | **Yes** | Prevent stale merges |
| Require linear history | **Yes** | Enforces squash merge |
| Allow force pushes | **No** | Never |
| Allow deletions | **No** | Protect main |

### `dev` Branch (Protected)

| Rule | Setting | Rationale |
| --- | --- | --- |
| Require pull request | **Yes** | All changes go through review |
| Required approvals | **1** | Every change is reviewed |
| Dismiss stale reviews on push | **Yes** | New pushes require re-review |
| Require status checks to pass | **Yes** | CI catches breakage early |
| Required status checks | `Validate structure`, `Lint Markdown`, `Validate YAML` | Same checks as main |
| Allow force pushes | **No** | Protect shared history |
| Allow deletions | **No** | Protect dev |

---

## Versioning Scheme

StatsClaw uses **Semantic Versioning** (semver):

```
vMAJOR.MINOR.PATCH[-prerelease]
```

| Component | When to bump | Examples |
| --- | --- | --- |
| **MAJOR** | Breaking changes to CLAUDE.md protocol, agent interface changes, removed skills | `v1.0.0`, `v2.0.0` |
| **MINOR** | New agents, new skills, new profiles, new workflows, backward-compatible CLAUDE.md updates | `v0.2.0`, `v1.3.0` |
| **PATCH** | Bug fixes, typo fixes, documentation improvements, CI changes | `v0.1.1`, `v1.3.2` |
| **Pre-release** | Alpha/beta/RC for major releases | `v1.0.0-alpha.1`, `v1.0.0-rc.1` |

### What counts as "breaking"

Since StatsClaw is consumed by Claude Code (reading CLAUDE.md and agent definitions), breaking changes include:

- Renaming or removing agent files that CLAUDE.md references
- Changing the state machine (adding/removing required states)
- Changing artifact names (e.g., `spec.md` → `specification.md`)
- Removing or renaming skills
- Changing the mandatory execution protocol steps

Non-breaking additions:

- New agent files (as long as existing ones are unchanged)
- New skills, profiles, templates
- New workflow numbers
- Relaxing constraints

---

## PR Merge Strategy

| Target Branch | Merge Method | Rationale |
| --- | --- | --- |
| `main` (from `dev`) | **Squash and merge** | Clean linear history, one commit per promotion |

**Commit message format** (from PR title):

```
<type>: <short description> (#PR)

Types: feat, fix, docs, chore, refactor, ci
```

---

## Release Process

### Cutting a Release

1. Ensure `dev` is stable — all CI checks pass.
2. Create a PR from `dev` → `main`. Get it reviewed and merged.
3. Tag the release on `main`:

```bash
git checkout main
git pull origin main
git tag -a v0.2.0 -m "v0.2.0: description"
git push origin v0.2.0
```

4. GitHub Actions automatically creates the GitHub Release.

### Pre-release Tags

For major releases, use pre-release tags to get early feedback:

```
v1.0.0-alpha.1  →  v1.0.0-beta.1  →  v1.0.0-rc.1  →  v1.0.0
```

Pre-release tags are marked as "Pre-release" on GitHub automatically.

---

## CI Pipeline Summary

Every push to `dev` and every PR to `main` runs:

| Job | What it checks |
| --- | --- |
| **Validate structure** | All cross-references resolve, required files exist, agent sections present, no runtime artifacts committed |
| **Lint Markdown** | Consistent formatting across all `.md` files |
| **Validate YAML** | Issue templates and workflow files are valid YAML |

Tag pushes (`v*`) additionally trigger:

| Job | What it does |
| --- | --- |
| **Create GitHub Release** | Auto-generates release notes, counts framework components, publishes release |
