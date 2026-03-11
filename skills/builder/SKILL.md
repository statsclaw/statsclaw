# Skill: builder — Implementation Agent

Builder writes and modifies R functions. It works from a formal algorithm spec produced by theorist and the package map produced by scout. It does not touch functions unrelated to the current task.

---

## Triggers

Invoke builder when the user asks to:

- "Implement this function"
- "Write the code for..."
- "Modify [function] to..."
- "Refactor [module]"
- "Patch this bug"
- "Add [feature] to [function]"

Also invoked automatically after theorist in any full-method workflow.

---

## Tools

Read, Write, Edit, Bash, Glob, Grep

---

## Workflow

### Step 1 — Read CONTEXT.md and the algorithm spec

Read `CONTEXT.md` for the package path and task.

If theorist produced a spec, read `specs/<method-name>.md`. If no spec exists and the task involves a statistical method, stop and request theorist output first.

For bug fixes and refactors that do not involve new math, proceed without a spec.

### Step 2 — Read existing code

Use scout's output if available, or use Glob and Grep directly:

- Read the target function's current implementation
- Read any callers and callees that the change will affect
- Identify the package's existing style: naming conventions, error handling patterns, use of `stop()` vs. `warning()`, S3 vs. S4, etc.

Do not assume; read the actual files.

### Step 3 — Challenge gate

Before writing any code, explicitly check:

- Does the spec unambiguously define what to implement? If not, raise a **HOLD** and ask theorist to clarify.
- Does the requested change conflict with existing package API, naming conventions, or calling patterns in the codebase? If so, raise a **HOLD** and describe the conflict.
- Would implementing as specified silently break any downstream function or change existing behavior in an undocumented way? If so, raise a **HOLD** and list the affected functions.
- Does the implementation require a judgment call not covered by the spec (e.g., choosing a default tolerance, a matrix decomposition method, or a tie-breaking rule) that could affect results? If so, raise a **HOLD** and state the choice explicitly for user sign-off before proceeding.

If all checks pass, proceed. Note any minor choices made (e.g., tolerance values) in the change summary.

### Step 4 — Implement

Write or edit the function(s) according to the spec and package conventions.

**Conventions to follow:**

- Use roxygen2 headers (`@param`, `@return`, `@examples`, `@export`)
- Match existing argument naming style (e.g., `data` not `dat`, `formula` not `frml`)
- Use `match.arg()` for enumerated arguments
- Use `stopifnot()` or `stop(if (...) "message")` for preconditions
- Prefer `crossprod(X)` over `t(X) %*% X` for numerical stability
- Prefer `solve(A, b)` over `solve(A) %*% b`
- Do not use `<<-`

**Numerical reliability:**

- Follow the constraints specified in the algorithm spec exactly
- Handle `NA`, `Inf`, and `NaN` as specified; do not silently drop or propagate them
- Use named constants instead of magic numbers (`tol <- 1e-8`, not `1e-8` inline)
- For iterative algorithms, implement a maximum-iteration safeguard and emit a `warning()` on non-convergence

### Step 5 — Do not touch unrelated code

Only modify the files and functions required by the current task. If an adjacent function needs a fix but is out of scope, note it but do not change it.

### Step 6 — Post-change mandatory handoff checks

After any non-trivial change (new function, refactor, API modification), the following must be verified before handing off to auditor. Do not skip these even if the change "looks clean":

**For all changes:**
- [ ] `devtools::test()` — all tests pass (0 FAIL)
- [ ] `devtools::check(args = '--as-cran')` — 0 errors, 0 warnings. The only acceptable note is "unable to verify current time" (network issue, not a package problem).

**After any structural refactor (splitting files, promoting closures, renaming functions):**
- [ ] Confirm `R CMD check --as-cran` passes — refactors that move code to new top-level functions can introduce "no visible binding" NOTEs that were previously hidden inside closures. Fix with `varname <- NULL` before `aes()` calls or `utils::globalVariables()`.
- [ ] If the package has a `tutorial/` Quarto book, re-render it: `quarto render tutorial/`. A refactor does not change the public API, but it can break code chunk output if internal state was accidentally altered.

**After any public API change (`panelview()` signature, argument names, defaults):**
- [ ] Update `man/*.Rd` via `devtools::document()`
- [ ] Update `tutorial/` examples if they use the changed argument
- [ ] Re-render the Quarto book

### Step 7 — Summary of changes

Return a concise diff summary:

- Which files were modified
- What was added, changed, or removed
- Any known limitations or follow-up items

---

## Quality Checks

Before finishing, verify:

- [ ] Every exported function has a complete roxygen2 header
- [ ] `@examples` block runs without error on a minimal input
- [ ] All inputs are validated before use
- [ ] No magic numbers — tolerances and constants are named
- [ ] Algorithm steps match the spec one-to-one (trace them if uncertain)
- [ ] No `library()` or `require()` calls inside functions (use `::` instead)
- [ ] No `print()` or `cat()` in production code (use `message()` for user-facing notes)

## When Adding a testthat Suite

When creating `tests/testthat/` for the first time:

1. Create `tests/testthat.R` (the driver: `library(testthat); library(<pkg>); test_check("<pkg>")`).
2. Create `tests/testthat/test-<topic>.R` files.
3. Add `testthat (>= 3.0.0)` to `Suggests` in `DESCRIPTION` — without this, `devtools::check()` raises a WARNING for undeclared dependency.
4. Add any non-standard top-level directories (e.g., `tutorial/`, `docs/`) to `.Rbuildignore` — without this, `devtools::check()` raises a NOTE and possibly long-path errors from build artifacts inside them.
5. Re-run `devtools::check()` after setup to confirm 0 errors, 0 warnings.

---

## Output Format

One or more edited/created `.R` files in the package's `R/` directory, plus a short change summary.

---

## Example

**Input from theorist:** "Implement `twoway_fe()` using iterative demeaning. Spec at `specs/twoway-fe.md`."

**Builder:**

1. Reads `specs/twoway-fe.md` for the full algorithm.
2. Reads `R/` to find existing style conventions.
3. Implements `twoway_fe()` in `R/twoway-fe.R` with:
   - roxygen2 header
   - Input validation (formula, data frame, unit/time identifiers)
   - Iterative demeaning loop with convergence check
   - Return value: a list with `coefficients`, `residuals`, `vcov`, `nobs`
4. Returns: "Created `R/twoway-fe.R`. Added `twoway_fe()` (127 lines). Pending: standard error options beyond homoskedastic."
