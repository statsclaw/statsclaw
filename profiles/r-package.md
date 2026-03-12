# Profile: r-package

Use this profile for standard R packages.

## Repo Markers

- `DESCRIPTION`
- `NAMESPACE`
- `R/`
- `man/`

## Typical Validation Commands

- `Rscript --vanilla -e "devtools::check('<pkg>', args = '--as-cran', quiet = FALSE)"`
- `Rscript --vanilla -e "devtools::test('<pkg>')"`
- `Rscript --vanilla -e "devtools::run_examples('<pkg>')"`

## Documentation Conventions

- roxygen2 headers
- `.Rd` files in `man/`
- `vignettes/`
- optional `tutorial/` Quarto book

## Common Tooling

- `devtools`
- `roxygen2`
- `testthat`
- `quarto`

## Builder Notes

- respect existing package API and exported surface
- use numerically stable R idioms
- update roxygen or `.Rd` when public API changes

## Auditor Notes

- prefer `--as-cran`
- render `tutorial/` if present and relevant
- treat warnings as blockers unless explicitly waived by the user
