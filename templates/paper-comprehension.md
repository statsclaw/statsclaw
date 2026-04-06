# Paper Comprehension: {paper_title}

> Source: `{source_file}` ({total_pages} pages)
> Parsed at: {parsed_at}
> Comprehension verdict: {verdict}

---

## Input Materials

| Material | Type | Content |
| --- | --- | --- |
| {source_file} | PDF paper | {brief_description} |

---

## Core Estimator(s)

### Estimator 1: {name}

- **Full name**: ...
- **Definition (LaTeX)**: $...$
- **Parameters**: ...
- **Key properties**: consistency, asymptotic normality, efficiency, ...
- **Variance estimation**: ...

_Repeat for each estimator identified._

---

## Assumptions

1. **{assumption_name}**: {formal statement}
   - Interpretation: ...
   - Testable: yes / no
2. ...

---

## Algorithm

### Algorithm 1: {name}

**Input**: ...
**Output**: ...

1. ...
2. ...
3. ...

**Convergence criterion**: ...
**Complexity**: ...

---

## Simulation Design (if present)

### DGP

- Model: ...
- Error distributions: ...
- Covariate structure: ...

### Parameters

| Parameter | Symbol | Values |
| --- | --- | --- |
| Sample size | N | ... |
| Replications | R | ... |
| ... | ... | ... |

### DGP Variants

| Variant | Description | Purpose |
| --- | --- | --- |
| Baseline | ... | Verify basic properties |
| ... | ... | ... |

### Metrics Reported

- Bias, RMSE, coverage, size, power, ...

---

## Data Structure

- **Type**: panel / cross-section / time-series / other
- **Required variables**: ...
- **Dimensions**: N = ..., T = ..., p = ...
- **Special structure**: balanced/unbalanced, clustering, ...

---

## Theorems and Results

### Theorem 1: {name}

- **Statement**: ...
- **Conditions**: ...
- **Implications for implementation**: ...

---

## Notation Table

| Symbol | Type | Dimensions | Definition |
| --- | --- | --- | --- |
| ... | scalar/vector/matrix | ... | ... |

---

## Comprehension Self-Test

1. **Core requirement (restated)**: ...
2. **Formulas verified**: yes / no — discrepancies: ...
3. **Undefined symbols**: none / list
4. **Judgment calls needed**: none / list
5. **Intuition explanation**: ...
6. **Implicit assumptions**: none / list

---

## Questions for User (if HOLD)

_Only populated when verdict is PARTIALLY UNDERSTOOD._

1. ...
2. ...

---

## Uncertainties

_Items where planner's understanding may be incomplete, noted for reviewer._

- ...

---

## Comprehension Record

- Verdict: `{verdict}` (FULLY UNDERSTOOD / UNDERSTOOD WITH ASSUMPTIONS / PARTIALLY UNDERSTOOD / UNSPECIFIABLE)
- HOLD rounds used: {rounds}/3
- Assumptions made (if any): ...
- Timestamp: {timestamp}
