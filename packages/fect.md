# RClaw Package Context — fect

---

## Package

```yaml
Package path: ~/GitHub/fect
Package name: fect
Version: 2.0.5
CRAN: yes
Description: >
  Counterfactual estimators for causal inference with time-series
  cross-sectional (TSCS) panel data. Implements the Fixed Effects
  Counterfactual (FEct), Interactive Fixed Effects Counterfactual
  (IFEct), and Matrix Completion (MC) estimators. Also provides
  a unified DID wrapper, diagnostic tests (placebo, pre-trend,
  carryover), and event-study visualization.
Paper: Liu, Wang & Xu (2022) AJPS — "A Practical Guide to
  Counterfactual Estimators for Causal Inference with TSCS Data"
```

---

## Key Exported Functions

```yaml
- fect / fect.formula / fect.default:
    Main estimation function. Dispatches to FEct (method="fe"),
    IFEct (method="ife"), MC (method="mc"), or polynomial trend.
    Core arguments: formula/Y/D/X, data, index, method, r, lambda,
    CV, force, se, nboots, placeboTest, carryoverTest.

- interFE / interFE.formula / interFE.default:
    Standalone interactive fixed effects estimation. Used inside
    fect but also exposed for direct use.

- effect:
    Aggregates fect output into cumulative or period-by-period ATTs.
    Supports subgroup filtering (id=, period=).

- esplot:
    Standalone event-study plot. Accepts any ATT/CI data frame,
    not just fect output. Highly customizable ggplot2 wrapper.

- get.cohort:
    Creates treatment cohort/timing variables (FirstTreat, Cohort,
    Time_to_Treatment, Time_to_Exit) from a binary treatment D.

- did_wrapper:
    Unified interface to TWFE, Stacked DID, Callaway-Sant'Anna (CS),
    DIDmultiplegtDYN. Consistent output format for comparison.

- fect_sens:
    Sensitivity analysis wrapping HonestDiDFEct. Computes
    robustness bounds under violations of parallel trends.

- plot.fect:
    S3 plot method. Types: gap, equiv, status, exit, factors,
    loadings, calendar, counterfactual, heterogeneous, dynamic.

- print.fect / print.interFE:
    S3 print methods.
```

---

## Source File Map

```yaml
R/:
  default.R:    Main fect() dispatcher; parses input, runs CV, bootstrap,
                calls estimators, assembles output (~2100 lines)
  boot.R:       Bootstrap and jackknife inference; fect_boot() (~2975 lines)
  plot.R:       plot.fect() with 50+ arguments; all plot types (~4020 lines)
  cv.R:         Cross-validation for r (IFEct) and lambda (MC) (~1537 lines)
  fect_gsynth.R: Gsynth/IFE core algorithm; factor extraction (~1281 lines)
  fe.R:         IFE EM-style alternating-least-squares updates (~897 lines)
  mc.R:         Matrix completion nuclear norm minimization (~777 lines)
  polynomial.R: Polynomial/spline trend pre-processing (~845 lines)
  support.R:    get_term() — treatment timing, reversal handling (~637 lines)
  fittest.R:    Wild bootstrap goodness-of-fit tests (~644 lines)
  diagtest.R:   Equivalence tests (TOST), F-tests for no pre-trend (~215 lines)
  permutation.R: Permutation tests for false discovery (~264 lines)
  cumu.R:       att.cumu() cumulative ATT with CI (~206 lines)
  effect.R:     effect() aggregation and optional plotting (~379 lines)
  esplot.R:     esplot() standalone event-study plotting (~902 lines)
  did_wrapper.R: did_wrapper() unified DID interface (~656 lines)
  fect_sens.R:  fect_sens() HonestDiDFEct wrapper (~215 lines)
  getcohort.R:  get.cohort() cohort/timing variables (~339 lines)
  cv_binary.R:  Cross-validation for binary (probit) outcomes (~417 lines)
  interFE.R:    interFE() standalone IFE estimation (~507 lines)
  print.R:      S3 print methods (~111 lines)
  RcppExports.R: Auto-generated Rcpp interface

src/ (C++ via Rcpp/RcppArmadillo):
  ife.cpp:        IFE core algorithm (EM updates, alternating LS)
  ife_sub.cpp:    IFE subroutines (factor/loading updates)
  fe_sub.cpp:     Fixed effect demeaning and residualization
  mc.cpp:         Matrix completion (nuclear norm)
  binary_qr.cpp:  Probit/binary estimation via QR
  binary_sub.cpp: Binary-specific subroutines
  binary_svd.cpp: SVD-based approaches for binary outcomes
  auxiliary.cpp:  Matrix operations, missing-data helpers
  fect.h:         Data structures, function declarations
```

---

## Mathematical Framework (from Liu, Wang & Xu 2022)

### Identification

Three assumptions:
1. **Functional form:** Y_it(0) = f(X_it) + h(U_it) + ε_it (additive separability)
2. **Strict exogeneity:** ε_it ⊥ {D_js, X_js, U_js} for all i,j,s,t (no feedback, no carryover)
3. **Low-dimensional decomposition:** h(U_it) = L_it where rank(L_{N×T}) ≪ min(N,T)

### Estimation strategy (4 steps)
1. Fit response surface on untreated observations O = {(i,t): D_it = 0}
2. Predict counterfactual Ŷ_it(0) for treated observations M = {(i,t): i∈T, D_it=1}
3. Estimate individual effects δ̂_it = Y_it − Ŷ_it(0)
4. Average δ̂_it for ATT, ATT_s (period-specific), etc.

### Three estimators
- **FEct:** Y_it(0) = X'_it β + α_i + ξ_t + ε_it (TWFE-based counterfactual; DID is a special case)
- **IFEct:** Y_it(0) = X'_it β + α_i + ξ_t + λ'_i f_t + ε_it (factor-augmented; hard-impute)
- **MC:** Y(0) = Xβ + L + ε, where L̂ = argmin Σ(Y_it−L_it)²/|O| + λ_L‖L‖ (soft-impute)

### Diagnostic tests
- **Placebo test:** Hide S pre-treatment periods; test if fake ATT ≈ 0 (DIM + TOST)
- **No pre-trend test:** Leave-one-period-out; equivalence test across all s≤0
- **No carryover test:** Hide periods after treatment ends; test if prediction error ≈ 0
- **Equivalence range:** Default [−0.36σ̂_ε, 0.36σ̂_ε] where σ̂_ε is SD of TWFE residuals

---

## Numerical Constraints & Assumptions

```yaml
- Data format: long-form panel; index = c(unit_id, time_id)
- Balanced and imbalanced panels both supported
- Treatment: binary (0/1); can switch on and off (general panel treatment structure)
- Always-treated and never-treated units are dropped at pre-processing
- Factor number r: selected by k-fold CV on triplets from treatment group
- Lambda (MC): selected by k-fold CV; same test set construction
- Binary outcomes: probit link; QR decomposition for numerical stability
- Bootstrap clustering: unit-level block bootstrap or jackknife
- Jackknife recommended when number of treated units is small
- Strict exogeneity rules out: feedback (Y_{t-1} → D_t), anticipation,
  carryover, lagged dependent variables
- IFEct outperforms MC when factors are strong and sparse; MC otherwise
```

---

## Test Suite

```yaml
tests/testthat/:
  test-fect-basic.R:          Basic fect() formula and default interfaces
  test-fect-sens.R:           fect_sens() sensitivity wrapper
  test-cumu-effect-esplot.R:  effect() and esplot()
  test-plot-fect.R:           plot.fect() S3 method
  test-did-wrapper.R:         did_wrapper() unified DID
  test-getcohort.R:           get.cohort()
  helper-data.R:              Shared test data
```

---

## Vignettes

```yaml
vignettes/:
  01-start.Rmd:     Quick-start guide
  02-fect.Rmd:      Main fect() tutorial (most important)
  03-plots.Rmd:     Visualization and plot customization
  04-gsynth.Rmd:    Gsynth/IFE deep-dive
  05-panel.Rmd:     Panel data preparation
  06-sens.Rmd:      Sensitivity analysis (HonestDiDFEct)
  07-cheetsheet.Rmd: Quick reference
```

---

## Known Issues / Ongoing Work

```yaml
- (Add issues here as they arise)
```

---

## Current Task

Update this section at the start of each session.

```yaml
Task: (none — fill in before starting)
```

---

## Session Notes

```
(fill in per session)
```
