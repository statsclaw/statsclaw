# Profile: R Package

## Repo Markers

Detect this profile when the target repository contains:

- `DESCRIPTION` file (required)
- `NAMESPACE` file
- `R/` directory
- `man/` directory

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Build | `R CMD build .` | Produces the source tarball |
| Check | `R CMD check --as-cran <tarball>` | Full CRAN-style check |
| Unit tests | `Rscript -e "devtools::test()"` | Runs testthat suite |
| Examples | `Rscript -e "devtools::run_examples()"` | Exercises all `@examples` blocks |
| Document | `Rscript -e "devtools::document()"` | Regenerates NAMESPACE and man/*.Rd |

## Documentation

- **API docs**: roxygen2 comments in `R/*.R` files, rendered to `man/*.Rd`
- **Vignettes**: R Markdown or Quarto files under `vignettes/`
- **Tutorials**: Optional Quarto book under `tutorial/` or `tutorials/`
- **README**: `README.Rmd` or `README.md` at the repo root
- **NEWS**: `NEWS.md` for user-visible changelog

## Common Tooling

- `devtools` — development workflow
- `roxygen2` — inline documentation to `.Rd`
- `testthat` — unit testing framework (edition 3 preferred)
- `quarto` — vignette and tutorial rendering
- `usethis` — package scaffolding helpers
- `covr` — test coverage reporting

## Build Exclusions

The following development-only artifacts MUST be excluded from CRAN tarballs via `.Rbuildignore`:

| Pattern | Purpose |
| --- | --- |
| `^architecture\.md$` | Architecture diagram (development-only) |
| `^log$` | Change log entries with handoff docs and design notes (development-only) |

Scribe and github teammates are responsible for appending these patterns. Check before appending to avoid duplicates.

## Builder Notes

- Respect the existing exported API; do not rename or remove exports without explicit request.
- Use numerically stable R idioms (avoid `1 - p` when `p` is near 1; prefer `log1p`, `expm1`, `.Machine$double.eps` guards).
- When adding or changing function signatures, update the corresponding roxygen2 block and run `devtools::document()`.
- Place internal helpers in files prefixed with `utils-` or mark them with `@noRd` / `@keywords internal`.
- Use `testthat` edition 3 conventions (`test_that()`, `expect_*()`) unless the package explicitly uses an earlier edition.
- Do not add new package dependencies without noting it in the mailbox for lead review.

## Auditor Notes

- Prefer `R CMD check --as-cran` over a plain `R CMD check`; the stricter flags catch issues that CRAN submission would reject.
- Treat all WARNINGs as blockers. NOTEs should be reviewed and reported but are not automatic blockers.
- Run `devtools::test()` separately to capture granular test output even when `R CMD check` also runs tests.
- If the package has vignettes, confirm they render without error.
- Check for undocumented exported functions (`devtools::check_man()`).
- Report test coverage numbers when `covr` is available.

---

## CRAN Submission Checklist

This checklist is derived from the [CRAN Cookbook](https://contributor.r-project.org/cran-cookbook/). Auditor MUST verify all applicable items during `R CMD check --as-cran`. Builder MUST follow these rules when writing code. Theorist SHOULD reference these constraints when producing specs for R packages.

### DESCRIPTION File

| Rule | Details |
| --- | --- |
| Description field | Must be 2+ sentences describing purpose, motivation, and optionally references. Model after established packages. |
| Title case | Package title must use Title Case (except articles: "a", "the", "of"). Use `tools::toTitleCase()` to verify. |
| Software names in quotes | Wrap all software, package, and API names in single quotes in Description (e.g., `'ggplot2'`, `'Python'`) to avoid spell-check NOTEs. |
| Acronyms | Document non-obvious acronyms in `cran-comments.md`. Common ones (OLS, DNA) are fine without explanation. |
| `Authors@R` field | Use `person()` format: `Authors@R: person("First", "Last", email = "...", role = c("aut", "cre"))`. Do not use deprecated `Author`/`Maintainer` fields. |
| LICENSE file | Only include `+ file LICENSE` if the license requires additional attribution (MIT, BSD). Most standard licenses do not need a separate file. |
| References | Use `<doi:...>` or `<https:...>` format with no trailing spaces for auto-linking. Include at least one reference for methodology packages. |

### Code Rules

| Rule | Details | BLOCK on violation? |
| --- | --- | --- |
| `TRUE`/`FALSE` not `T`/`F` | Never use `T`/`F` as abbreviations or variable names — they are reassignable. | Yes |
| No hardcoded `set.seed()` in functions | Seeds in functions must be user-controllable via a `seed` parameter (default `NULL`). Seeds in examples/tests/vignettes are fine. | Yes |
| No unsuppressable output | Replace `print()`/`cat()` with `message()`, `warning()`, `stop()`, or wrap in `if(verbose)`. Exception: print/summary methods. | Yes |
| Restore options/par/wd | After modifying `par()`, `options()`, or `setwd()`, immediately call `on.exit()` to restore. In examples: save and restore manually. | Yes |
| No writing to home filespace | Never write to user's home dir, package dir, or `getwd()` by default. Use `tempdir()` in examples/tests. | Yes |
| Clean up temp files | Remove files created in `tempdir()` after use. Use `withr::local_tempfile()` in tests. NOTEs about "detritus in temp directory" are blockers. | Yes |
| No `.GlobalEnv` modification | Do not use `<<-` or assign to `.GlobalEnv`. Never modify `.Random.seed`. Exception: Shiny packages. | Yes |
| No `installed.packages()` | Use `requireNamespace("pkg")` or `find.package()` instead — `installed.packages()` is extremely slow. | Yes |
| No `options(warn = -1)` | Use `suppressWarnings()` on specific expressions instead of globally disabling warnings. | Yes |
| No installing packages | Do not call `install.packages()` in functions, examples, tests, or vignettes. Dedicated install functions (e.g., `install_*()`) are acceptable but must not auto-run. | Yes |
| Max 2 cores | Examples, vignettes, and tests must not use more than 2 CPU cores. Provide a user-configurable core count parameter. | Yes |

### Examples Structure

| Wrapper | When to use |
| --- | --- |
| Unwrapped | Short demos on toy data; CRAN runs these automatically |
| `\donttest{}` | Long-running examples (>5 sec), data downloads |
| `\dontrun{}` | Truly unexecutable code (missing API/software); auto-labeled "Not run:" |
| `if(interactive()){}` | Shiny apps, interactive plots |
| `try()` | Intentional error demonstrations |
| `if(requireNamespace("pkg")){}` | Examples needing suggested packages |
| `\dontshow{}` | Hidden setup/teardown code |

All wrappers must be inside `\examples{}`. Prefer unwrapped examples for fast code; use `\donttest{}` over `\dontrun{}` when code is runnable but slow.

### Package Size

- Target under 5 MB; absolute CRAN maximum is 10 MB.
- Host large datasets externally (GitHub, separate data package).
- Document size justification in `cran-comments.md` if over 5 MB.

### Auditor CRAN Verification Steps

In addition to the standard validation commands, auditor MUST check:

1. **`R CMD check --as-cran` output**: Zero ERRORs, zero WARNINGs. Review all NOTEs.
2. **DESCRIPTION compliance**: Verify Description length (2+ sentences), Title Case, `Authors@R` format, quoted software names.
3. **Code scan for CRAN violations**: Grep for `T`/`F` used as logicals, hardcoded `set.seed()` in non-test code, bare `print()`/`cat()`, `options(warn = -1)`, `installed.packages()`, `<<-`, unrestored `par()`/`options()`/`setwd()`.
4. **Example review**: Confirm examples are properly wrapped, fast examples are unwrapped, `\dontrun{}` is not used where `\donttest{}` suffices.
5. **Temp file cleanup**: Verify no leftover files in `tempdir()` after tests/examples.
6. **Core usage**: Confirm parallel operations use ≤2 cores in examples/vignettes/tests.
7. **Package size**: Check tarball size; flag if >5 MB.

### Builder CRAN Compliance Notes

In addition to the standard builder notes:

- Always use `TRUE`/`FALSE`, never `T`/`F`.
- When modifying `par()`, `options()`, or `setwd()`, add `on.exit()` restoration immediately.
- Use `message()` for informational output, not `print()` or `cat()`.
- Use `tempdir()` for any file I/O in examples and tests; clean up with `on.exit(unlink(...))`.
- Provide a `seed` parameter (default `NULL`) for any function that uses random number generation.
- Cap parallel workers at 2 in examples/vignettes/tests; expose a `cores`/`nthreads` parameter for user control.
- Use `requireNamespace("pkg", quietly = TRUE)` to check for suggested packages, not `installed.packages()`.
