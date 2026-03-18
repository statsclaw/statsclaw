# Profile: Rust Crate

## Repo Markers

Detect this profile when the target repository contains:

- `Cargo.toml` file (required)
- `src/lib.rs` or `src/main.rs`
- `tests/` directory (common for integration tests)

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Build | `cargo build` | Compile the crate |
| Unit tests | `cargo test` | Run all tests (unit + integration) |
| Check | `cargo check` | Fast type-check without codegen |
| Lint | `cargo clippy -- -D warnings` | Lint with warnings as errors |
| Format check | `cargo fmt -- --check` | Verify formatting |
| Doc build | `cargo doc --no-deps` | Build documentation |

## Documentation

- **API docs**: `///` doc comments on public items, rendered by `cargo doc`
- **Module docs**: `//!` comments at the top of `lib.rs` or module files
- **README**: `README.md` at the repo root
- **Examples**: `examples/` directory with runnable examples

## Common Tooling

- `cargo` — build system and package manager
- `rustfmt` — code formatter
- `clippy` — linter
- `rustdoc` — documentation generator
- `miri` — undefined behavior detector (for unsafe code)

## Build Exclusions

**Note**: Architecture diagrams and workflow logs are NOT stored in the target repo — they are synced to the brain repo (`[owner]/statsclaw-brain`). No `Cargo.toml` exclusions are needed for these artifacts. See `skills/brain-sync/SKILL.md`.

## Builder Notes

- Follow Rust conventions: snake_case for functions/variables, PascalCase for types, SCREAMING_SNAKE_CASE for constants.
- Use `Result<T, E>` for fallible operations; avoid `unwrap()` in library code.
- Prefer `&str` over `String` in function parameters when ownership is not needed.
- Place unit tests in a `#[cfg(test)] mod tests` block within the source file.
- Place integration tests in `tests/` directory.
- Do not add dependencies to `Cargo.toml` without noting it in the mailbox.
- Use `thiserror` for library error types and `anyhow` for application error handling (if the project follows this pattern).

## Auditor Notes

- `cargo test` must pass with zero failures.
- `cargo clippy -- -D warnings` must produce zero warnings; treat all as blockers.
- `cargo fmt -- --check` must pass; treat formatting violations as blockers.
- If the crate has `unsafe` blocks, verify they are documented and justified.
- Check that all public items have doc comments.
- Run `cargo doc --no-deps` and verify it builds without warnings.
- Report test coverage if `cargo-tarpaulin` or `cargo-llvm-cov` is available.
