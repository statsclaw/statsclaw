---
name: profile-detection
description: "Automatic language profile selection for target repositories"
user-invocable: false
disable-model-invocation: true
---
# Shared Skill: Profile Detection — Automatic Language Profile Selection

This skill determines the correct language profile for a target repository by inspecting file markers.

---

## Trigger

This skill is invoked automatically by leader during Session Startup (step 6) and Leader Planning (step 5) when the profile is not already set in the package context.

---

## Detection Algorithm

Leader checks for repo markers in order. The **first matching profile** is selected.

### Step 1 — Check for Profile Override

If the repo context file (`.repos/workspace/<repo-name>/context.md`) already has a `Profile` field set, use it directly. Skip detection.

### Step 2 — Scan Repo Root for Markers

Check the target repository root for the following files. Match the first profile whose **required marker** is present:

| Priority | Required Marker | Supporting Markers | Profile |
| --- | --- | --- | --- |
| 1 | `DESCRIPTION` (with `Package:` field) | `NAMESPACE`, `R/`, `man/` | `profiles/r-package.md` |
| 2 | `pyproject.toml` or `setup.py` or `setup.cfg` | `src/` or `*/__init__.py`, `tests/` | `profiles/python-package.md` |
| 3 | `package.json` + `tsconfig.json` | `src/`, `*.ts` files | `profiles/typescript-package.md` |
| 4 | `go.mod` | `*.go` files, `cmd/`, `internal/` | `profiles/go-module.md` |
| 5 | `Project.toml` (with `name` and `uuid` fields) | `src/`, `test/` | `profiles/julia-package.md` |
| 6 | `Cargo.toml` | `src/lib.rs` or `src/main.rs`, `tests/` | `profiles/rust-crate.md` |
| 7 | `CMakeLists.txt` or `Makefile` or `meson.build` + `*.cpp`/`*.cc`/`*.cxx` | `*.hpp`/`*.hxx`, `tests/` | `profiles/cpp-library.md` |
| 8 | `CMakeLists.txt` or `Makefile` or `meson.build` + `*.c` (no C++ sources) | `*.h`, `tests/` | `profiles/c-library.md` |
| 9 | `*.ado` or `*.do` files | `*.sthlp` files | `profiles/stata-project.md` |

### Step 3 — Disambiguation

If multiple markers match (e.g., a repo has both `pyproject.toml` and `package.json`):

1. Check which language has more source files
2. Check the primary README for language references
3. If still ambiguous, use `AskUserQuestion` to ask the user

### Step 4 — Write Profile

Once detected, write the profile to:
1. The repo context file (`.repos/workspace/<repo-name>/context.md`): set the `Profile` field
2. The run's `status.md`: set the `Active Profile` field

---

## Fallback

If no markers match any profile, log a note in `.repos/workspace/<repo-name>/logs/` and proceed without a profile. Teammates will use general-purpose conventions. Leader should mention the missing profile to the user.
