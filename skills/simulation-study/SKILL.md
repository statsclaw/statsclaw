---
name: simulation-study
description: "Designs and executes Monte Carlo simulation studies evaluating finite-sample properties (bias, RMSE, coverage, size, power) of statistical estimators. Dispatches builder and simulator in parallel from independent specs, then validates results via tester against acceptance criteria. Use when the user requests simulation evidence, finite-sample evaluation, or Monte Carlo experiments for new or existing estimators."
user-invocable: false
disable-model-invocation: true
---
# Skill: Simulation Study — Monte Carlo Evaluation of Estimator Properties

Designs and executes Monte Carlo simulation studies that evaluate finite-sample properties of statistical estimators. Given a DGP specification and an estimator, produces simulation code via an isolated simulator agent, runs the study through the tester, and reports results on consistency, bias, RMSE, coverage, size, and power.

## When to Use

Activate when the user's intent involves any of the following (leader routes semantically — exact wording not required):

- Running a simulation study or Monte Carlo experiments for an estimator
- Evaluating finite-sample properties, small-sample behavior, or convergence rates
- Checking consistency, coverage, bias, RMSE, size, or power of an estimator
- Designing a DGP and evaluating estimator performance against it

---

## What This Skill Does

1. **Design** — Planner analyzes the estimator and produces a simulation specification (`sim-spec.md`) alongside the standard `spec.md` and `test-spec.md`
2. **Implement** — Builder implements the estimator (code pipeline), Simulator implements the DGP and simulation harness (simulation pipeline), both from independent specs
3. **Execute** — Tester runs the full simulation and validates results against theoretical expectations (test pipeline)
4. **Report** — Scriber records the simulation design, results, and convergence diagnostics
5. **Review** — Reviewer cross-compares all three pipelines for convergence

---

## Workflows That Use Simulation

### Workflow 11: Simulation Study (New Estimator)

**Trigger**: User requests implementation of a new estimator AND wants simulation evidence of its properties.

**Agent Sequence**:
```
leader → planner → [builder ∥ simulator] → tester → scriber → reviewer → shipper?
```

**What happens**:
1. Planner produces THREE specs: `spec.md` (estimator implementation), `test-spec.md` (unit tests + simulation validation), `sim-spec.md` (DGP + scenario grid + metrics)
2. Builder implements the estimator from `spec.md` (in worktree) — runs in parallel with simulator
3. Simulator implements the DGP and simulation harness from `sim-spec.md` (in worktree) — runs in parallel with builder
4. After both builder and simulator complete and merge back, tester validates the fully merged code: runs unit tests from `test-spec.md` AND executes the full simulation, comparing results against acceptance criteria
5. Scriber records everything including simulation results tables
6. Reviewer cross-compares all three pipelines

### Workflow 12: Simulation Only (Existing Estimator)

**Trigger**: User wants simulation study for an already-implemented estimator (no code changes needed).

**Agent Sequence**:
```
leader → planner → simulator → tester → scriber → reviewer → shipper?
```

**What happens**:
1. Planner produces TWO specs: `sim-spec.md` (DGP + scenarios) and `test-spec.md` (simulation validation criteria)
2. Simulator implements the DGP and harness from `sim-spec.md` (in worktree)
3. After simulator completes and merges back, tester executes the full simulation and validates from `test-spec.md`
4. Scriber records results
5. Reviewer reviews

No builder is dispatched since the estimator already exists.

### Integration with Existing Workflows

Simulation can also be **added to** standard code workflows (1, 2, 4, 5) when the user's request includes simulation intent. In that case:

- Planner produces all three specs
- Builder AND simulator are dispatched in parallel; after both complete, tester is dispatched
- The rest of the pipeline proceeds normally with the additional `simulation.md` artifact

---

## Simulation Specification (`sim-spec.md`)

Planner produces `sim-spec.md` containing:

### 1. DGP Definition

```markdown
## Data Generating Process

### Model
Y_i = X_i'β + ε_i

### Parameters
| Parameter | Symbol | True Value(s) | Type |
| --- | --- | --- | --- |
| Coefficients | β | (1.0, 0.5, -0.3) | vector |
| Error SD | σ | 1.0 | scalar |

### Distributions
| Component | Distribution | Parameters |
| --- | --- | --- |
| X | N(0, Σ) | Σ = I_p |
| ε (baseline) | N(0, σ²) | σ = 1.0 |
| ε (heavy-tailed) | t(3) scaled to σ² | df = 3 |
| ε (skewed) | χ²(1) centered and scaled | — |

### Dimensions
| Variable | Values |
| --- | --- |
| N (sample size) | 100, 200, 500, 1000, 5000 |
| p (covariates) | 3 |
```

### 2. Estimator Interface

```markdown
## Estimator Interface

Function: `my_estimator(Y, X, ...)`
Returns: list with components `$coefficients`, `$std_errors`, `$conf_int`, `$p_values`
```

### 3. Scenario Grid

```markdown
## Scenario Grid

| Dimension | Values | Total Levels |
| --- | --- | --- |
| Sample size (N) | 100, 200, 500, 1000, 5000 | 5 |
| Error distribution | Normal, t(3), χ²(1) | 3 |
| Correlation (ρ) | 0.0, 0.5, 0.9 | 3 |

Total scenarios: 5 × 3 × 3 = 45
Replications per scenario: R = 2000
Total simulation runs: 90,000
```

### 4. Performance Metrics

```markdown
## Required Metrics

- Bias (absolute and relative)
- Standard deviation of estimates
- RMSE
- Coverage of 95% CI
- Size at α = 0.05 (test H₀: β₁ = β₁_true)
- Power at α = 0.05 (test H₀: β₁ = 0 when β₁ = 0.5)
- SE ratio (estimated SE / empirical SD)
- Failure rate
```

### 5. Acceptance Criteria

```markdown
## Acceptance Criteria

| Criterion | Threshold | At N ≥ |
| --- | --- | --- |
| Relative bias | < 5% | 500 |
| Coverage (95% CI) | ∈ [0.93, 0.97] | 500 |
| Size (α = 0.05) | ∈ [0.03, 0.07] | 500 |
| SE ratio | ∈ [0.95, 1.05] | 500 |
| RMSE convergence rate | slope ∈ [-0.6, -0.4] on log-log | all |
| Failure rate | < 1% | all |
```

### 6. Seed Strategy

```markdown
## Reproducibility

Master seed: 20260326
Per-scenario seed: master_seed + (scenario_index - 1) * R + replication
RNG type: Mersenne-Twister (R) / numpy.random.default_rng (Python)
```

---

## Three-Pipeline Architecture (With Simulation)

When simulation is active, the two-pipeline architecture extends to three pipelines:

```
                      planner (bridge)
                     /    |          \
          spec.md   / test-spec.md    \  sim-spec.md
                   /      |            \
            builder ─ ─(parallel)─ ─ simulator
       (code pipeline)    |    (simulation pipeline)
                   \      |            /
      implementation.md   |   simulation.md
                    \     |          /
                     \    v         /
                       tester           <-- sequential, after merge-back
                    (test pipeline)
                         |
                      audit.md
                         |
                    scriber (recording)
                         |
                    reviewer (convergence)
                         |
                       shipper
```

**Key properties**:
1. Builder and simulator are dispatched in PARALLEL (both in the same message). Tester is dispatched AFTER both complete and merge back.
2. Builder receives ONLY `spec.md`
3. Simulator receives ONLY `sim-spec.md`
4. Tester receives ONLY `test-spec.md` (which includes simulation validation criteria)
5. Tester validates the fully merged code — both the unit tests AND the simulation results
6. Pipeline isolation is maintained across all three pipelines

---

## Tester's Role in Simulation Workflows

In simulation workflows, tester has expanded responsibilities:

1. **Unit test validation** — standard test scenarios from `test-spec.md`
2. **Full simulation execution** — run the simulation harness with full replications (R = 2000+)
3. **Result validation** — compare simulation outputs against acceptance criteria from `test-spec.md`
4. **Convergence verification** — check that metrics converge as N grows

Tester's `test-spec.md` includes a dedicated **Simulation Validation** section (produced by planner) that specifies:
- Expected convergence patterns
- Exact acceptance thresholds for each metric
- How to interpret the simulation output tables

Tester produces the simulation results tables in `audit.md`, along with pass/fail assessments for each acceptance criterion.

---

## Reviewer's Role in Simulation Workflows

Reviewer cross-compares THREE pipelines:

1. **Code ↔ Test convergence**: Does the implementation match the test expectations?
2. **Simulation ↔ Theory convergence**: Do the finite-sample properties match theoretical predictions?
3. **Code ↔ Simulation consistency**: Does the estimator behave the same in unit tests and simulation?
4. **DGP correctness**: Is the DGP implementation faithful to `sim-spec.md`?

Reviewer checks:
- Simulation results are within acceptance thresholds
- Convergence rates match theory (e.g., √N-consistency)
- No suspicious patterns (e.g., coverage exactly at nominal — suggests test is not discriminating)
- Simulator did not read `spec.md` or `test-spec.md` (pipeline isolation)
- Tester did not read `sim-spec.md` or `spec.md` (pipeline isolation)

---

## Safety Rules

- **Honest reporting**: Simulator MUST report all results honestly, including unfavorable ones. Cherry-picking scenarios or replications is forbidden.
- **No tolerance inflation**: Neither simulator nor tester may relax acceptance criteria to make results pass.
- **Reproducibility**: All simulation code MUST produce identical results when re-run with the same seeds.
- **Resource awareness**: For large simulation grids, estimate total computation time in `simulation.md` and warn if it exceeds 1 hour.
- **Pipeline isolation**: Simulator never sees `spec.md` or `test-spec.md`. The simulation study is designed from mathematical principles (`sim-spec.md`), not from knowledge of implementation details.

---

## Example User Prompts

All of these should trigger simulation workflows:

```
"Implement the panel data estimator from the paper and run Monte Carlo simulations"
"Study the finite-sample properties of the new robust estimator"
"Run a simulation study: DGP is linear model with heteroskedastic errors, evaluate OLS vs GLS"
"Check if the confidence intervals have correct coverage for small samples"
"Monte Carlo: test consistency and coverage of the bootstrap estimator"
"Evaluate the new method's bias and RMSE across different sample sizes"
```
