# RClaw Package Context — panelView

---

## Package

```yaml
Package path: ~/GitHub/panelView
Package name: panelView
CRAN: yes (v1.1.18)
Description: Visualizes panel data — treatment status, outcome trajectories, and bivariate relationships between treatment and outcome.
Paper: Mou, Liu & Xu (2022) JSS doi:10.18637/jss.v107.i07
```

---

## Key Functions

```yaml
- panelview: main (and only) exported function; dispatches on type=
    "treat"     — treatment status / missingness heatmap
    "missing"   — missingness-only plot (alias: "miss")
    "outcome"   — outcome trajectories by unit (alias: "raw")
    "bivariate" — Y vs D over time, aggregate or by unit (alias: "bivar")
```

Internal helpers (not exported):
```yaml
- .pv_plot_treat(s)     — in R/plot-treat.R; renders type="treat" / "missing"
- .pv_plot_outcome(s)   — in R/plot-outcome.R; renders type="outcome"
- .pv_subplot(...)      — in R/plot-outcome.R; helper for by.group subplots
- .pv_plot_bivariate(s) — in R/plot-bivariate.R; renders type="bivariate"
```

Each plot function receives `s = as.list(environment())` from `panelview()` dispatch point
and accesses all pre-computed variables via `with(s, {...})`.

---

## Known Issues / Ongoing Work

```yaml
- Syntax table in vignette fetched from external URL (fragile); tutorial/ uses markdown table instead
```

---

## Numerical Constraints & Assumptions

```yaml
- Handles balanced and unbalanced panels
- NA handling: units with missing index variables are dropped with a warning
- leave.gap=TRUE shows time gaps as white bars; default FALSE skips gaps with a warning
- axis.lab.angle must be in {0, 45, 90}
- type="missing" cannot be combined with ignore.treat=TRUE
- by.cohort=TRUE only valid with type="outcome"
- Continuous treatment (>5 unique values): rendered as gradient, legend suppressed
```

---

## File Map

```yaml
R/panelView.R:     orchestrator: arg parsing, data wrangling, dispatch (~1160 lines)
R/plot-outcome.R:  .pv_plot_outcome() + .pv_subplot()
R/plot-treat.R:    .pv_plot_treat()
R/plot-bivariate.R: .pv_plot_bivariate()
R/zzz.r:           .onAttach startup message
data/:             turnout.rda, capacity.rda, simdata.rda
man/panelview.Rd:  Rd documentation
tests/testthat/test-panelview.R: 36 tests (all passing, 0 errors/warnings)
tutorial/:         Quarto book (added 2026-03-10; in .Rbuildignore)
examples.R:        standalone usage script (in .Rbuildignore)
```

---

## Current Task

```yaml
Task: Refactor complete. Tutorial created. All committed and pushed.
      Next possible task: CRAN patch release (bump version, NEWS entry)
```

---

## Session Notes

```
2026-03-10 — RClaw audit session
  Improvements made:
  1. DESCRIPTION: RoxygenNote 6.0.1→7.3.2, added Encoding: UTF-8, Suggests: testthat
  2. R/panelView.R: replaced manual type check with match.arg() + alias normalization
     (miss→missing, bivar→bivariate, raw→outcome); removed 4+ redundant alias comparisons
  3. R/zzz.r: updated startup URL to canonical package page
  4. tests/testthat/test-panelview.R: 36 tests covering all 4 types + error paths
  5. tests/testthat.R: standard test_check() harness
  6. tutorial/: Quarto book with 3 content chapters + index + references
  devtools::check() result: 0 errors, 0 warnings, 1 note (timestamp verification — network)
  devtools::test() result: 36 pass, 0 fail
```
