# Skill: scout — Repository Agent

Scout maps an R package's structure: what it exports, how its functions depend on each other, and which files would be touched by a proposed change.

---

## Triggers

Invoke scout when the user asks:

- "Map the package"
- "What functions are affected by this change?"
- "What does this package export?"
- "List dependencies between functions"
- "Which files would I need to touch to modify X?"
- "Show me the package structure"

Also invoke scout at the start of any full-method workflow to establish the landscape before theorist and builder operate.

---

## Tools

Bash, Read, Glob, Grep

---

## Workflow

### Step 1 — Read CONTEXT.md

Read `CONTEXT.md` to get the package path. If the path is missing, stop and ask the user.

### Step 2 — Read DESCRIPTION and NAMESPACE

```r
# Read these files from the package root:
# DESCRIPTION  — package name, version, dependencies, imports
# NAMESPACE    — exports, imports, S3/S4 methods
```

Extract:

- Package name and version
- Imports and Suggests
- All `export()`, `exportMethods()`, `S3method()` entries from NAMESPACE

### Step 3 — Glob all source files

```r
# Glob these patterns relative to the package root:
R/*.R
src/*.c
src/*.cpp
src/*.f
tests/testthat/test-*.R
man/*.Rd
vignettes/*.Rmd
vignettes/*.R
```

### Step 4 — Build function inventory

For each `R/*.R` file:

- Extract all function definitions: `^[a-zA-Z._][a-zA-Z0-9._]* <- function`
- Classify as exported or internal (cross-reference NAMESPACE)

### Step 5 — Build dependency map

For each function, scan function bodies to detect calls to other package functions.
Map: `caller → [called_functions]`.

If a specific change is proposed, identify the transitive closure of affected functions.

### Step 6 — Output structured summary

Return the report in the Output Format below.

---

## Output Format

```markdown
## Package: [name] [version]

### Exported Functions
- `function_a()` — [R/file.R, line N]
- `function_b()` — [R/file.R, line N]

### Internal Functions
- `.helper_x()` — [R/file.R, line N]

### Dependencies (Imports)
- pkg1 (>= x.y)
- pkg2

### Function Dependency Map
- `function_a()` calls: `.helper_x()`, `pkg1::foo()`
- `function_b()` calls: `function_a()`

### Files Affected by Change to [target]
- R/[file.R]
- man/[file.Rd]
- tests/testthat/test-[file.R]
```

---

## Quality Checks

- Do not guess function locations; verify by reading the file.
- If NAMESPACE is absent, note it and infer exports from `@export` roxygen tags in `R/*.R`.
- Flag unexported functions that appear in `man/` (documentation inconsistency).
- Flag functions in NAMESPACE that do not exist in `R/` (broken export).

---

## Example

**User:** "Map the fect package at ~/GitHub/fect"

**Scout:**

1. Reads `CONTEXT.md` or uses the path provided inline.
2. Reads `DESCRIPTION` and `NAMESPACE`.
3. Globs `R/*.R`, `man/*.Rd`, `tests/testthat/`.
4. Returns a structured summary: exported functions, internals, dependency map, file list.
