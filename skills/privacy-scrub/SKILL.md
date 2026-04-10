---
name: privacy-scrub
description: "PII removal for brain knowledge contributions"
user-invocable: false
disable-model-invocation: true
---
# Skill: Privacy Scrub — PII Removal for Brain Contributions

This skill defines the mandatory privacy scrubbing protocol applied to all knowledge entries before they are proposed for contribution to the shared brain. The distiller agent applies these rules when extracting knowledge; the reviewer agent verifies compliance.

---

## Purpose

Knowledge entries contributed to `statsclaw/brain-seedbank` and ultimately curated into `statsclaw/brain` must contain ZERO identifying information about the source project, user, or organization. The knowledge must be fully genericized — reusable by anyone without revealing its origin.

---

## Mandatory Scrub Categories

### Category 1 — Identifiers (ALWAYS strip)

| Type | Examples | Action |
| --- | --- | --- |
| GitHub usernames | `@xuyiqing`, `@jdoe` | Remove entirely |
| Repository names | `xuyiqing/fect`, `org/project` | Replace with "the target package" or "the project" |
| Organization names | `UCSD`, `MIT`, `CompanyX` | Remove entirely |
| Email addresses | `user@domain.com` | Remove entirely |
| Personal names | `John Doe`, `Prof. Smith` | Remove entirely |

### Category 2 — Paths and References (ALWAYS strip)

| Type | Examples | Action |
| --- | --- | --- |
| File paths | `/R/fect.R`, `src/estimator.py` | Replace with "the estimation module", "the test file" |
| Directory structures | `R/`, `src/core/`, `tests/` | Use generic: "the source directory", "the test directory" |
| Package names | `fect`, `panelView`, `numpy` | Use generic or keep only if it's a well-known public library |
| Issue/PR numbers | `#42`, `PR #15` | Replace with "the reported issue", "the fix PR" |
| Commit SHAs | `abc1234` | Remove entirely |
| Branch names | `fix/issue-42`, `cfe` | Remove entirely |
| GitHub URLs | `https://github.com/owner/repo` | Remove entirely |

### Category 3 — Code References (ALWAYS genericize)

| Type | Examples | Genericized Form |
| --- | --- | --- |
| Function names (user code) | `est_fect()`, `panel_matrix()` | `my_estimator()`, `helper_function()` |
| Variable names (user code) | `fect_result`, `panel_data` | `result`, `input_data` |
| Class names (user code) | `FectEstimator`, `PanelModel` | `MyEstimator`, `BaseModel` |
| Data column names | `gdp_growth`, `treatment_status` | `outcome_var`, `treatment_var` |
| Dataset names | `democracy_panel.csv` | "the input dataset" |

**Exception**: Well-known public library names and their APIs (e.g., `numpy`, `dplyr`, `torch`) may be kept as-is since they are public knowledge.

### Category 4 — Data References (ALWAYS strip)

| Type | Examples | Action |
| --- | --- | --- |
| Dataset names | `world_bank_2020.csv` | "the input dataset" |
| Column names | `gdp_per_capita`, `country_code` | "the outcome variable", "the grouping variable" |
| Data file paths | `data/raw/panel.csv` | Remove entirely |
| Database names | `production_db` | Remove entirely |

---

## What to KEEP

The following are safe to include in knowledge entries and should be preserved:

- **Mathematical formulas**: LaTeX notation, matrix operations, statistical estimators
- **Statistical methods**: Method names (e.g., "difference-in-differences", "matrix completion", "LASSO")
- **Algorithm descriptions**: Pseudocode, convergence criteria, iteration strategies
- **Generic coding patterns**: Design patterns, numerical stability techniques, error handling strategies (with genericized names)
- **Performance insights**: Complexity analysis, memory optimization, parallelization strategies
- **Tolerance calibrations**: Numerical precision findings, convergence thresholds
- **DGP designs**: Data generating processes (with generic variable names)
- **Well-known library APIs**: How to use public libraries effectively

---

## Genericization Table (Quick Reference)

| Original Pattern | Genericized Form |
| --- | --- |
| `est_fect()` | `my_estimator()` |
| `R/fect.R` | "the estimation module" |
| `xuyiqing/fect` | "the target package" |
| `issue #42` | "the reported issue" |
| `panel_matrix()` | `helper_function()` |
| `FectEstimator` | `MyEstimator` |
| `tests/test_fect.R` | "the test file" |
| `democracy_panel.csv` | "the input dataset" |
| `treatment_status` | `treatment_var` |
| `gdp_growth` | `outcome_var` |

---

## Verification Protocol

The reviewer agent MUST verify privacy scrub compliance for every proposed brain contribution:

1. **Scan for GitHub patterns**: URLs (`github.com`), usernames (`@`), issue references (`#\d+`)
2. **Scan for path patterns**: Forward slashes with extensions (`/something.R`), home directories (`/home/`, `~/`)
3. **Scan for email patterns**: `@` followed by domain
4. **Scan for specific names**: Cross-reference against known repo names, function names from the current workflow
5. **Verify genericization**: All code examples use placeholder names, not actual project names

If ANY identifying information is detected: **STOP — privacy scrub incomplete. Route to distiller.**

---

## CI Validation (brain-seedbank repo)

The `statsclaw/brain-seedbank` repo runs automated PII scanning on all PRs via `.github/workflows/validate-entry.yml`. The CI checks:

- GitHub URL patterns: `github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+`
- File path patterns: `[/\\][a-zA-Z0-9_-]+\.[a-zA-Z]{1,4}` (with allowlist for generic examples)
- Email patterns: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Home directory patterns: `/home/`, `~/`, `C:\\Users\\`

These are catch-all checks — the distiller and reviewer are expected to catch issues before CI does.
