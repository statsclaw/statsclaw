# RClaw Package Context — fdid

---

## Package

```yaml
Package path: ~/GitHub/fdid
Package name: fdid
Version: 1.0.0
CRAN: submission in progress
Description: >
  Factorial Difference-in-Differences. Implements the Comparative
  Interruption Design (CID) framework for causal inference with
  panel data, identifying effects of a baseline factor G in the
  presence of a universal interruption Z.
Paper: Xu, Zhao & Ding (2026) "Multiple faces of difference-in-differences"
  DOI: 10.1080/01621459.2026.2628343
```

---

## Key Exported Functions

```yaml
- fdid(s, tr_period, ref_period, method, vartype, target.pop, ...):
    Main estimation function. Six methods: ols1, ols2, did, ebal, ipw, aipw.
    Three variance types: robust (HC0), bootstrap, jackknife.
    target.pop: "all" (ATE), "1" (ATT), "0" (ATC). Default: "all".
    Parallel support via parallel=TRUE, cores=N, nsims=N.
    Returns fdid object with: est (pre/event/post), dynamic, raw_means.

- fdid_prepare(data, Y_label, X_labels, G_label, unit_label, time_label, cluster_label):
    Reshapes long-format panel to wide format required by fdid().
    Averages time-varying covariates over pre-period; renames columns
    to unit, x1/x2/..., G, c (cluster).

- fdid_list(...):
    Bundles multiple fdid objects for comparison plots.
    Input: any number of fdid objects.
    Returns fdid_list object.

- print.fdid / summary.fdid:
    S3 methods. summary() shows pre/event/post aggregates + dynamic table.

- plot.fdid(x, type):
    Types: "raw" (raw means by group), "dynamic" (treatment effects over
    time), "overlap" (propensity score overlap, ipw/aipw only).

- plot.fdid_list(x):
    Comparison plot of multiple fdid estimates (vertical/horizontal layout).
```

---

## Mathematical Framework (from Xu, Zhao & Ding 2026)

### Setup (two-period case)
- Binary baseline factor: G_i ∈ {0,1} (time-invariant)
- One-time interruption at t_0; exposure Z_i ∈ {0,1}
- Potential outcomes: (Y_i^pre(g,z), Y_i^post(g,z)) for (g,z) ∈ {0,1}²
- CID assumption: Z_i = 1 for all i (ubiquitous exposure)
- DiD estimand: τ_did = E(Y^post - Y^pre | G=1) − E(Y^post - Y^pre | G=0)

### Key estimands
- **Effect modification (τ_a):** How G moderates the effect of Z (identified under PTA alone)
- **Causal moderation / interaction (τ_c):** Counterfactual effect of intervening on G (requires additional assumptions)
- **Marginal effects of G:** Requires exclusion restriction or as-if randomization

### Identification assumptions
1. **No anticipation:** Y^pre(g,0) = Y^pre(g,1)
2. **Parallel trends (PTA):** E{Y^post(G_i,0) − Y^pre(G_i,0) | G=1} = same | G=0
3. **Ubiquitous exposure:** Z_i = 1 for all i
4. **Exclusion restriction (optional):** Y^post(g,1) = Y^post(g,0) for G=0 (recreates canonical DiD)
5. **As-if randomization (optional):** Y(g,z) ⊥ G_i | X_i (implies τ_a = τ_c)

### Connection to canonical DID
Canonical DID = CID + exclusion restriction (G=0 group exposed but unaffected by Z).

---

## Source File Map

```yaml
R/:
  fdid.R:            Main estimation engine; all 6 methods; 3 variance types (~665 lines)
  fdid_prepare.R:    Data reshaping long→wide; covariate averaging (~130 lines)
  fdid_list.R:       Bundle multiple fdid objects with validation (~35 lines)
  plot.R:            plot.fdid() — raw/dynamic/overlap plots (~210 lines)
  plot.fdid_list.R:  Comparison plots for fdid_list (~142 lines)
  summary.R:         summary.fdid() formatted output (~101 lines)
  print.R:           print.fdid() brief overview (~25 lines)
  data.r:            mortality dataset documentation
  package.R:         Package-level imports (roxygen)
```

---

## Data

```yaml
data/fdid.RData:
  mortality: 11973 rows × 16 columns
    - Panel: county-year (China, 1954-1966)
    - Outcome: mortality (mortality rate)
    - Group: pczupu (genealogy book density; binarize at median for G)
    - Unit IDs: provid, countyid
    - Time: year
    - Covariates (9): avggrain, nograin, urban, dis_bj, dis_pc,
                      rice, minority, edu, lnpop
    - Context: Great Famine (1958-1961); clan/social capital mechanism
    - Source: Cao et al. (2022)
```

---

## Known Issues / Ongoing Work

```yaml
- If CRAN: create vignettes/ with a single-file intro Rmd (proper vignette headers)
- R CMD check --as-cran pending
```

---

## Pre-Release Checklist

```yaml
Completed:
  - [x] Fix ATT = TRUE → target.pop = "1" in demonstration.Rmd
  - [x] Fix mortality.Rd X/Y placeholder dimensions
  - [x] Add NEWS.md
  - [x] Run devtools::check() cleanly (0 errors, 0 warnings, 1 env note)
  - [x] Proofread tutorial/ Rmd files (typos, grammar, code bug in 03-visualization.Rmd)
  - [x] Rename "fdid - User tutorial" → tutorial/ (and .Rproj)
  - [x] Delete Table1.dta, demonstration.Rmd, test.R, test2.R
  - [x] Add tests/testthat/ suite (54 tests; all 6 methods + structure + plotting)
  - [x] Fix bug in summary.R (bare tr_period → object$tr_period)
  - [x] Add \examples{} to fdid.Rd, plot.fdid.Rd, summary.fdid.Rd (and R source)
  - [x] Add testthat to Suggests in DESCRIPTION
  - [x] Add tutorial/ to .Rbuildignore; clean up .Rbuildignore of deleted files
  - [x] Update .gitignore for knitr/Quarto build artifacts

  - [x] Render tutorial/ end to end — all 5 files, 0 errors (Quarto 1.8.25)

Still needed:
  - [ ] Run R CMD check --as-cran
  - [ ] If CRAN: create vignettes/ with a proper single-file intro Rmd
```

---

## Current Task

```yaml
Task: Run R CMD check --as-cran; if passing, submit to CRAN (add vignettes/ first).
```

---

## Session Notes

```
2026-03-10: Full pre-release audit and cleanup.
- 54 testthat tests passing; 0 errors, 0 warnings, 1 env note.
- Tutorial renamed (tutorial/), proofread, rendered clean (Quarto 1.8.25).
- Stale files deleted; examples added to 3 Rd files; summary.R scoping bug fixed.
- v1.0.0 committed and pushed. CRAN submission next.
```
