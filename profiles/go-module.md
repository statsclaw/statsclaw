# Profile: Go Module

## Repo Markers

Detect this profile when the target repository contains:

- `go.mod` file (required)
- `*.go` source files
- `cmd/` or `internal/` directories (common)

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Build | `go build ./...` | Compile all packages |
| Unit tests | `go test ./...` | Run all tests |
| Tests + coverage | `go test -coverprofile=coverage.out ./...` | With coverage output |
| Vet | `go vet ./...` | Static analysis for suspicious constructs |
| Lint | `golangci-lint run` | Comprehensive linting (if installed) |
| Format check | `gofmt -l .` | List files with formatting issues |

## Documentation

- **API docs**: Godoc comments on exported types, functions, and methods
- **README**: `README.md` at the repo root
- **Examples**: `Example*` functions in `*_test.go` files (testable examples)

## Common Tooling

- `go test` — built-in test framework
- `go vet` — built-in static analysis
- `golangci-lint` — aggregated linter
- `gofmt` / `goimports` — formatting
- `go generate` — code generation

## Build Exclusions

**Note**: Workflow logs are synced to the workspace repo; architecture diagrams stay in the local run directory. Neither is stored in the target repo. No exclusions needed. See `skills/workspace-sync/SKILL.md`.

## Builder Notes

- Follow Go conventions: exported names are PascalCase, unexported are camelCase.
- Return errors as the last return value; do not panic in library code.
- Use `context.Context` as the first parameter for functions that do I/O or may block.
- Place tests in the same package (`*_test.go`) or use `_test` suffix for black-box tests.
- Do not add new dependencies to `go.mod` without noting it in the mailbox.
- Use `errors.New` or `fmt.Errorf` with `%w` for wrapping; define sentinel errors for public API.
- Prefer table-driven tests.

## Tester Notes

- `go test ./...` must pass with zero failures.
- `go vet ./...` must produce zero warnings; treat all as blockers.
- If `golangci-lint` is configured, zero issues required.
- Check that all exported types and functions have Godoc comments.
- Run `gofmt -l .` and treat any output as a blocker (unformatted files).
- Report test coverage percentage for changed packages.
