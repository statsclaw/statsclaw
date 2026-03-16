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
