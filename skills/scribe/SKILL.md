# Skill: scribe — Documentation Agent

Scribe writes and maintains user-facing documentation: `.Rd` help files, vignettes, and standalone tutorials. It ensures that examples always run, that docs match the current API, and that tutorials are readable by applied researchers unfamiliar with the implementation.

---

## Triggers

Invoke scribe when the user asks to:

- "Document this function"
- "Update the Rd file for..."
- "Write a vignette for..."
- "Generate a tutorial"
- "Write an example"
- "Fix the documentation"
- "The example in [function] is broken"

Also invoked automatically after auditor passes in any full-method workflow.

---

## Tools

Read, Write, Edit

---

## Workflow

### Step 1 — Read CONTEXT.md and identify scope

Read `CONTEXT.md` for the package path and current task.

Determine what documentation is needed:

- **Rd update** — modifying an existing `man/*.Rd` file or its roxygen2 source
- **New Rd** — documenting a newly added function
- **Vignette** — a `.Rmd` document in `vignettes/`
- **Tutorial** — a standalone Markdown tutorial (output outside the package)

### Step 2 — Read existing documentation

For Rd work:

- Read `man/<function>.Rd` if it exists
- Read the corresponding `R/<file>.R` to find the roxygen2 source (`#' @param`, `#' @return`, etc.)
- Check that all current arguments are documented; flag any that are missing or outdated

For vignettes:

- Read existing `vignettes/*.Rmd` to understand style and conventions
- Read the algorithm spec (`specs/<method-name>.md`) if one exists

### Step 3 — Write or update documentation

#### For roxygen2 headers in R files:

- Every exported function must have: `@title`, `@description`, `@param` for each argument, `@return`, `@examples`, `@export`
- `@param` descriptions must state: type (e.g., "a numeric vector"), dimensions if matrix, and constraints
- `@return` must describe the class and structure of the output object
- `@examples` must be self-contained and runnable with no external dependencies beyond the package

#### For `.Rd` files (direct edits):

- Match the structure of existing `.Rd` files in the package
- Use `\code{}`, `\link{}`, `\eqn{}`, `\deqn{}` markup correctly
- Test LaTeX math: `\deqn{x^2}` not `\deqn{$x^2$}` (no dollar signs inside Rd math commands)

#### For vignettes:

- Use `templates/tutorial-template.md` as a structural guide
- Include: overview, method description with equations, installation, basic usage, detailed example with output, edge cases, references
- All code chunks must be self-contained and produce deterministic output (use `set.seed()`)
- Expected output should be shown as comments or in separate output chunks

#### For standalone tutorials:

- Use `templates/tutorial-template.md`
- Target audience: applied researchers, not package developers
- Explain the method in plain language before showing code
- Show realistic data and realistic results

#### For Quarto books (multi-chapter tutorials):

Place the book in `tutorial/` at the package root (never in `vignettes/`). Add `^tutorial$` to `.Rbuildignore`.

**Structure:**
```
tutorial/
├── _quarto.yml       — book metadata, chapter list, format/theme
├── index.qmd         — welcome page: what the package does, chapter overview, contributors, bug report
├── 01-<topic>.Rmd    — chapter 1 (H1 = `# Title {#sec-name}`)
├── 02-<topic>.Rmd    — chapter 2
├── ...
└── references.qmd    — `# References {.unnumbered}` + `{#refs}` div (only if bib exists)
```

**`_quarto.yml` template:**
```yaml
project:
  type: book
book:
  title: "<pkg> -- User Tutorial"
  sidebar:
    style: docked
    background: light
  chapters:
    - index.qmd
    - 01-<topic>.Rmd
    - references.qmd   # omit if no bib
delete_merged_file: true
bibliography: references.bib  # omit if no citations
format:
  html:
    theme: cosmo
    df-print: paged
    code-fold: false
    code-tools: true
    code-link: true
knitr:
  opts_chunk:
    collapse: true
    comment: "#>"
```

**Chapter file conventions:**
- First line: `# Chapter Title {#sec-name}` — this becomes the sidebar entry
- Setup chunk immediately after: `knitr::opts_chunk$set(echo=TRUE, message=FALSE, warning=FALSE)`
- Do NOT use `cache = TRUE` in chunk options (Quarto has its own freeze mechanism)
- Cross-reference sections with `[Chapter @sec-name]` in `index.qmd`

**Splitting a monolithic vignette into chapters:**
- Identify the top-level `##` sections — each becomes a chapter
- Move shared setup (library loads, data loads) to each chapter's setup chunk
- Remove vignette YAML header (`%\VignetteEngine`, `%\VignetteIndexEntry`) entirely
- The Rmd chapter files use `---` YAML only if needed for chapter-level title overrides (usually not needed; H1 header is sufficient)

**Rendering:**
- Quarto binary on macOS: `/Applications/RStudio.app/Contents/Resources/app/quarto/bin/quarto`
- Run from the tutorial directory: `cd ~/GitHub/<pkg>/tutorial && quarto render`
- Output goes to `_book/` inside the tutorial directory

### Step 4 — Spec consistency check

If an algorithm spec exists at `specs/<method-name>.md`:

- Read it.
- Check that `@param` descriptions, `@return` structure, and any `@details` math match the spec.
- If a documented argument, return value, or formula contradicts the spec, raise a **HOLD**: state the contradiction and do not publish the documentation until it is resolved.

### Step 5 — Verify all examples

For every `@examples` block or code chunk written:

- Trace through the code mentally and verify it runs correctly against the current function signature
- Check that all argument names match the current implementation
- Check that any data objects used (e.g., `data(mydata)`) exist in the package
- If an example relies on external data, provide inline data generation instead

Flag any example that would fail. Do not write examples that cannot currently run.

### Step 6 — Return or save output

- For roxygen2 edits: edit the `R/<file>.R` source directly; note that `devtools::document()` must be run to regenerate `.Rd` files
- For direct `.Rd` edits: edit `man/<file>.Rd` directly
- For vignettes: write or edit `vignettes/<name>.Rmd`
- For standalone tutorials: write to `tutorials/<function>-tutorial.md` within the RClaw workspace

**Roxygen2 version mismatch:** If the installed roxygen2 version is older than the version declared in `DESCRIPTION` (field `RoxygenNote`), `devtools::document()` will refuse to run. In this case, edit **both** the `R/<file>.R` source (for future correctness) **and** the `man/<file>.Rd` file directly (so the change takes effect now). Note this in the summary so the user knows to run `devtools::document()` after upgrading roxygen2.

**`tutorial/` vs `vignettes/`:** A Quarto book or multi-chapter tutorial living in a non-standard top-level directory (e.g., `tutorial/`, `docs/`) is NOT the same as R package vignettes in `vignettes/`. Proper R package vignettes require individual `.Rmd` files with `%\VignetteEngine` and `%\VignetteIndexEntry` headers, placed in `vignettes/`, and declared in `DESCRIPTION`. A Quarto book cannot be dropped into `vignettes/` without restructuring. Add the tutorial directory to `.Rbuildignore` to keep it out of the build tarball.

---

## Quality Checks

- [ ] Every exported function is documented
- [ ] No argument is undocumented
- [ ] `@examples` blocks run without error
- [ ] No dollar signs inside `\eqn{}` or `\deqn{}`
- [ ] `@return` describes the class and structure, not just "the result"
- [ ] Vignette code chunks produce deterministic output
- [ ] References cite the original paper with DOI or journal info
- [ ] No internal (unexported) functions are documented with `@export`

---

## Output Format

One or more of:

- Edited `R/<file>.R` with updated roxygen2 headers
- Edited `man/<file>.Rd` with corrected documentation
- New or updated `vignettes/<name>.Rmd`
- New `tutorials/<function>-tutorial.md`

Plus a short summary of what was changed and whether `devtools::document()` needs to be run.

---

## Example

**After auditor finds an example error in `twoway_fe.Rd`:**

**Scribe:**

1. Reads `R/twoway-fe.R` and finds the `@examples` block is missing the `data` argument.
2. Reads `specs/twoway-fe.md` for the method description and expected usage.
3. Rewrites the `@examples` block with a self-contained example using `data.frame()`.
4. Updates `@return` to describe the S3 class `twoway_fe` and its components.
5. Drafts `vignettes/twoway-fe.Rmd` using `templates/tutorial-template.md`: overview, within-transformation explanation, basic usage, a simulation example with `set.seed(42)`, and a reference to the original paper.
6. Returns: "Updated `R/twoway-fe.R` (examples fixed). Created `vignettes/twoway-fe.Rmd`. Run `devtools::document()` to regenerate `.Rd`."
