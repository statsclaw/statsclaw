# Profile: stata-project

Use this profile for Stata projects, Stata packages, and research repositories where `.do`, `.ado`, or `.mata` files define the main implementation.

## Repo Markers

- `*.do`
- `*.ado`
- `*.mata`
- `stata.toc`
- `pkg.pkg`

## Typical Validation Commands

- `stata -b do main.do`
- `stata -b do tests/run_tests.do`

Use only commands that exist in the target repo or are explicitly configured in the project context.

## Documentation Conventions

- `README.md`
- package help files such as `.sthlp`
- replication guides
- example `.do` scripts
- papers, appendices, or docs folders when relevant

## Common Tooling

- `stata`
- `stata-mp`
- `stata-se`

## Builder Notes

- preserve project-specific Stata conventions and directory assumptions
- be careful with working-directory assumptions inside `.do` files
- update example scripts and help files when behavior changes
- avoid hidden environment dependencies

## Auditor Notes

- run configured do-file based validation commands
- verify that example scripts and replication scripts still run when required
- treat non-zero batch exits and missing dependency failures as blockers
