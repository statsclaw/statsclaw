# Profile: C Library

## Repo Markers

Detect this profile when the target repository contains:

- `Makefile`, `CMakeLists.txt`, or `meson.build` (at least one required)
- `*.c` source files
- `*.h` header files
- No `*.cpp`, `*.cc`, or `*.cxx` files (distinguishes from C++ profile)

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Build (Make) | `make` or `make all` | Standard Makefile build |
| Build (CMake) | `cmake -B build && cmake --build build` | Out-of-source CMake build |
| Build (Meson) | `meson setup builddir && meson compile -C builddir` | Meson build |
| Unit tests (Make) | `make test` or `make check` | Run tests via Makefile target |
| Unit tests (CMake) | `ctest --test-dir build` | CTest runner |
| Unit tests (Meson) | `meson test -C builddir` | Meson test runner |
| Static analysis | `cppcheck --enable=all --error-exitcode=1 src/` | Static analysis for common defects |
| Address sanitizer | `make CFLAGS="-fsanitize=address -g" test` | Memory error detection (if supported) |
| Valgrind | `valgrind --leak-check=full --error-exitcode=1 ./test_runner` | Memory leak detection |

## Documentation

- **API docs**: Doxygen comments (`/** */` or `///`) on public functions and types in header files
- **Header docs**: File-level comment blocks at the top of each `.h` file describing the module
- **README**: `README.md` at the repo root
- **Man pages**: Optional `man/` directory with `.3` section pages for library functions
- **Examples**: `examples/` directory with compilable sample programs

## Common Tooling

- `gcc` / `clang` — compilers
- `make` / `cmake` / `meson` — build systems
- `cppcheck` — static analysis
- `valgrind` — memory debugging and profiling
- `gcov` / `lcov` — test coverage
- `doxygen` — documentation generation
- `pkg-config` — dependency discovery
- `AddressSanitizer` / `UndefinedBehaviorSanitizer` — runtime error detectors

## Build Exclusions

**Note**: Workflow logs are synced to the workspace repo; architecture diagrams stay in the local run directory. Neither is stored in the target repo. No build system exclusions are needed for these artifacts. See `skills/workspace-sync/SKILL.md`.

## Builder Notes

- Follow the project's existing naming convention; common C style is `snake_case` for functions, variables, and file names, `SCREAMING_SNAKE_CASE` for macros and constants, and `PascalCase` or `snake_case_t` for typedefs.
- Use `const` correctness on pointer parameters that are not modified.
- Every public function must be declared in a header file with a Doxygen comment documenting parameters, return value, and ownership/lifetime semantics.
- Use include guards (`#ifndef HEADER_H` / `#define HEADER_H` / `#endif`) or `#pragma once` consistent with the project style.
- Avoid undefined behavior: check for NULL pointers, integer overflow, buffer overruns.
- Prefer `size_t` for array sizes and loop counters over bare `int`.
- Use `static` for file-local helper functions that should not be part of the public API.
- Allocations (`malloc`, `calloc`, `realloc`) must have corresponding `free` calls with clear ownership documentation.
- Do not add new external library dependencies without noting it in the mailbox for leader review.
- When writing numerical/statistical code, use numerically stable algorithms (compensated summation, log-space computation for probabilities, guard against division by zero and overflow).
- Provide a clean public API through a single or small set of header files; keep internal implementation headers separate (e.g., `src/internal/`).

## Tester Notes

- The build must complete with zero errors and zero warnings under `-Wall -Wextra -Werror` (or the project's equivalent strict flags).
- All tests must pass with zero failures.
- `cppcheck --enable=all` must produce zero errors; warnings should be reviewed and reported.
- If Valgrind is available, run it on the test suite; treat any memory leaks, invalid reads/writes, or use-after-free as blockers.
- If AddressSanitizer is available, run tests with `-fsanitize=address`; treat any report as a blocker.
- Check that all public functions in header files have Doxygen-style documentation.
- Report test coverage if `gcov`/`lcov` is available.
- Verify no compiler warnings are suppressed via pragmas without justification.
- For numerical code, verify results against known reference values with appropriate tolerances.
