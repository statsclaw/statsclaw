# Profile: Julia Package

## Repo Markers

Detect this profile when the target repository contains:

- `Project.toml` file (required, with `name` and `uuid` fields)
- `src/` directory with `<PackageName>.jl` entry point
- `test/` directory

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Instantiate | `julia --project -e 'using Pkg; Pkg.instantiate()'` | Resolve and download dependencies |
| Precompile | `julia --project -e 'using <PkgName>'` | Verify package loads cleanly |
| Unit tests | `julia --project -e 'using Pkg; Pkg.test()'` | Runs `test/runtests.jl` |
| Format check | `julia --project -e 'using JuliaFormatter; exit(!format("src/", overwrite=false))'` | If `JuliaFormatter` is a dependency |
| Aqua check | `julia --project=test -e 'using Aqua, <PkgName>; Aqua.test_all(<PkgName>)'` | API quality (if `Aqua` is a test dep) |
| Docs build | `julia --project=docs docs/make.jl` | If `docs/` exists with `Documenter.jl` |

## Documentation

- **API docs**: Docstrings in source files (Julia docstring format with triple-quoted markdown)
- **Manual/Tutorials**: `Documenter.jl` pages under `docs/src/`
- **README**: `README.md` at the repo root
- **CHANGELOG**: `CHANGELOG.md` or `NEWS.md`

## Common Tooling

- `Pkg` (stdlib) — built-in package manager
- `Test` (stdlib) — built-in test framework
- `Documenter.jl` — documentation site generation
- `JuliaFormatter.jl` — code formatting
- `Aqua.jl` — automated package quality checks (undefined exports, dependency compatibility, ambiguous methods)
- `Coverage.jl` / `LocalCoverage.jl` — coverage reporting
- `JET.jl` — static type inference analysis (optional)

## Build Exclusions

**Note**: Workflow logs are synced to the workspace repo; architecture diagrams stay in the local run directory. Neither is stored in the target repo. No exclusions needed. See `skills/workspace-sync/SKILL.md`.

## Builder Notes

- The entry file must be `src/<PackageName>.jl`, matching the `name` field in `Project.toml`.
- Use `export` to explicitly export the public API; use the `public` keyword for non-exported but public symbols (Julia 1.11+).
- Prefer multiple dispatch over if-else branching for type-specific behavior.
- Use `struct` (immutable, preferred) or `mutable struct` for type definitions.
- Use `where` clauses for parametric types: `function foo(x::AbstractArray{T}) where T`.
- In numerical code, use `one(T)` / `zero(T)` for type stability — avoid hardcoding `1.0` or `0.0`.
- Prefix internal functions with `_` (e.g., `_helper()`) or place them in non-exported submodules.
- Do not add new dependencies to `Project.toml` without noting it in the mailbox for leader review.
- Avoid type-unstable code — this is the primary performance concern in Julia.
- If using random number generation, accept an `rng::AbstractRNG` parameter (default `Random.default_rng()`).

## Tester Notes

- `Pkg.test()` must pass with zero failures.
- If `Aqua.jl` is a test dependency, `Aqua.test_all()` must pass — checks for undefined exports, dependency compatibility, ambiguous methods, and more.
- If `JuliaFormatter.jl` is present, the format check must pass.
- Check that all exported functions and types have docstrings.
- If `docs/` directory exists, confirm `docs/make.jl` builds without errors.
- Report test coverage percentage when `Coverage.jl` is available.
- Check that `Project.toml` has a `[compat]` section with version bounds for all direct dependencies (required by the General Registry).

---

## Julia General Registry Checklist

This checklist references the [Julia General Registry guidelines](https://github.com/JuliaRegistries/General#registration-guidelines). Tester MUST verify all applicable items during validation. Builder MUST follow these rules when writing code. Planner SHOULD reference these constraints when producing specs for Julia packages.

### Project.toml Requirements

| Rule | Details |
| --- | --- |
| `name` field | Package name should be CamelCase, no `.jl` suffix |
| `uuid` field | Must exist and be unique (generate with `uuidgen` or `Pkg.generate()`) |
| `version` field | Follow SemVer (start at 0.1.0) |
| `[compat]` section | All direct dependencies must have version bounds; `julia` itself should have bounds |
| `[deps]` section | List only direct dependencies; test-only dependencies go in `test/Project.toml` or in `[extras]`+`[targets]` sections |

### Code Rules

| Rule | Details | BLOCK on violation? |
| --- | --- | --- |
| No side effects in `__init__()` | `__init__()` should not make irreversible global state changes | Yes |
| No type piracy | Do not define methods on types you do not own with functions you do not own | Yes |
| No `eval` at load time | Avoid `eval`/`@eval` to define methods during package loading | Yes (except metaprogramming) |
| Precompilation compatible | Package must precompile cleanly (`using Pkg; Pkg.precompile()`) | Yes |
| Package size | Keep source lean; use `Artifacts` for large datasets | If unreasonably large |

### Tester Registry Verification Steps

In addition to the standard validation commands, tester MUST check:

1. **`Pkg.test()` output**: Zero test failures.
2. **`Project.toml` compliance**: Verify `name` (CamelCase, no `.jl`), `uuid` present, `version` follows SemVer.
3. **`[compat]` completeness**: Every direct dependency in `[deps]` has a corresponding entry in `[compat]`. The `julia` compat bound is present.
4. **Code scan for registry violations**: Grep for type piracy patterns, `eval`/`@eval` at top level (outside `__init__`), mutable global state.
5. **Docstring coverage**: Confirm all exported symbols have docstrings.
6. **Test-only dependencies**: Confirm test-only packages are in `test/Project.toml` or in `[extras]`+`[targets]` sections of the main `Project.toml` — not in the main `[deps]`.

### Builder Registry Compliance Notes

In addition to the standard builder notes:

- Always use CamelCase for the package name; the module name must match `Project.toml` `name` exactly.
- Place test-only dependencies in `test/Project.toml` or in `[extras]`+`[targets]` sections — not in the main `[deps]`.
- Set `[compat]` bounds for every dependency, including `julia` itself.
- Use the `Artifacts` system for large data files instead of bundling them in the package.
- If implementing `__init__()`, limit it to non-destructive setup (registering `atexit` hooks, initializing caches).
