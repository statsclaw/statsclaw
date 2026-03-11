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

### Step 3 — Implement

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

### Step 4 — Do not touch unrelated code

Only modify the files and functions required by the current task. If an adjacent function needs a fix but is out of scope, note it but do not change it.

### Step 5 — Summary of changes

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
