# Profile: Stata Project

## Repo Markers

Detect this profile when the target repository contains:

- `*.do` files (do-files)
- `*.ado` files (ado-files / program definitions)
- `*.sthlp` files (help files)

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Run master | `stata -b do master.do` | Execute the main entry point in batch mode |
| Run specific | `stata -b do <file>.do` | Execute a specific do-file |
| Log check | Inspect `*.log` for `r(...)` errors | Stata writes batch output to log files |

If the system uses `stata-mp` or `stata-se` instead of `stata`, substitute accordingly.

## Documentation

- **Help files**: `.sthlp` files providing Stata-native help for each command/ado
- **README**: `README.md` at the repo root
- **Comments**: In-file comments in do-files (`//`, `/* */`, `*` at line start)

## Common Tooling

- `stata` (or `stata-mp`, `stata-se`) — runtime
- `adopath` — custom ado search paths
- `log using` — execution logging within do-files

## Builder Notes

- Preserve existing naming conventions for ado-files and their companion sthlp files.
- Use `version X.Y` at the top of ado-files and do-files to pin Stata version compatibility.
- Prefer `tempfile` and `tempvar` for intermediate objects to avoid polluting the namespace.
- Use `capture` and return-code checking (`if _rc != 0`) for robust error handling.
- Keep do-files modular: one logical task per do-file, orchestrated by a master do-file.
- Do not hard-code file paths; use relative paths or globals set in the master do-file.

## Auditor Notes

- Run `stata -b do master.do` and check the resulting log file for any `r(...)` return-code errors.
- Treat any non-zero return code in the log as a blocker.
- Verify that all ado-files have a corresponding sthlp file when the project follows that convention.
- Check that `version` is declared at the top of each ado-file.
- If the project includes example data or output, verify that results are reproducible.
