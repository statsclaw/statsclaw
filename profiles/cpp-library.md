# Profile: C++ Library

## Repo Markers

Detect this profile when the target repository contains:

- `CMakeLists.txt`, `Makefile`, or `meson.build` (at least one required)
- `*.cpp`, `*.cc`, or `*.cxx` source files
- `*.hpp`, `*.hh`, `*.hxx`, or `*.h` header files

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Build (CMake) | `cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build` | Out-of-source CMake build |
| Build (Make) | `make` or `make all` | Standard Makefile build |
| Build (Meson) | `meson setup builddir && meson compile -C builddir` | Meson build |
| Unit tests (CMake) | `ctest --test-dir build --output-on-failure` | CTest runner with failure output |
| Unit tests (Make) | `make test` or `make check` | Run tests via Makefile target |
| Unit tests (Meson) | `meson test -C builddir` | Meson test runner |
| Static analysis | `cppcheck --enable=all --std=c++17 --error-exitcode=1 src/` | Static analysis |
| Clang-Tidy | `clang-tidy src/*.cpp -- -std=c++17` | Clang-based linting (if `.clang-tidy` present) |
| Address sanitizer | `cmake -B build -DCMAKE_CXX_FLAGS="-fsanitize=address -g" && cmake --build build && ctest --test-dir build` | Memory error detection |
| Format check | `clang-format --dry-run -Werror src/*.cpp include/*.hpp` | Formatting verification (if `.clang-format` present) |

## Documentation

- **API docs**: Doxygen comments (`/** */` or `///`) on public classes, functions, and type aliases in header files
- **Header docs**: File-level comment blocks describing the module and its purpose
- **README**: `README.md` at the repo root
- **Examples**: `examples/` directory with compilable sample programs
- **Tutorials**: Optional Markdown or Doxygen `@page` tutorials

## Common Tooling

- `g++` / `clang++` — compilers
- `cmake` / `make` / `meson` — build systems
- `cppcheck` — static analysis
- `clang-tidy` — linter and static analyzer
- `clang-format` — code formatter
- `valgrind` — memory debugging and profiling
- `gcov` / `lcov` / `llvm-cov` — test coverage
- `doxygen` — documentation generation
- `Google Test` / `Catch2` / `doctest` — testing frameworks
- `AddressSanitizer` / `UndefinedBehaviorSanitizer` / `ThreadSanitizer` — runtime error detectors

## Build Exclusions

**Note**: Workflow logs are synced to the workspace repo; architecture diagrams stay in the local run directory. Neither is stored in the target repo. No build system exclusions are needed for these artifacts. See `skills/workspace-sync/SKILL.md`.

## Builder Notes

- Follow the project's existing naming convention; common C++ styles include `snake_case` (STL-style), `camelCase`, or `PascalCase` for classes. Be consistent with the existing codebase.
- Use modern C++ idioms appropriate to the project's standard (prefer C++17 or later features when the project supports them).
- Prefer RAII (Resource Acquisition Is Initialization) over manual resource management; use smart pointers (`std::unique_ptr`, `std::shared_ptr`) instead of raw `new`/`delete`.
- Use `const` and `constexpr` where appropriate; prefer `const` references for function parameters that are not modified.
- Use `override` on all virtual function overrides; use `final` when a class or method should not be further overridden.
- Prefer `std::string_view` over `const std::string&` for read-only string parameters (C++17+).
- Avoid raw pointers for ownership; use smart pointers and clearly document ownership semantics.
- Every public class and function must have a Doxygen comment documenting purpose, parameters, return value, exceptions, and thread safety.
- Use `#pragma once` or include guards consistent with the project style.
- Place unit tests alongside source code or in a dedicated `tests/` directory using the project's testing framework (Google Test, Catch2, doctest, etc.).
- Do not add new library dependencies without noting it in the mailbox for leader review.
- When writing numerical/statistical code:
  - Use numerically stable algorithms (Kahan summation, log-sum-exp, Welford's online variance).
  - Guard against division by zero, overflow, and underflow.
  - Prefer `<cmath>` functions over C-style `<math.h>`.
  - Use `std::numeric_limits` for type-specific bounds and epsilon values.
  - Consider using `Eigen`, `Armadillo`, or `Blaze` for linear algebra (if the project uses them).
- Template code should use `static_assert` and concepts (C++20) or SFINAE (pre-C++20) to provide clear error messages for invalid type parameters.
- Prefer `enum class` over unscoped `enum`.
- Use namespaces to organize the public API; avoid `using namespace` in header files.

## Tester Notes

- The build must complete with zero errors and zero warnings under `-Wall -Wextra -Wpedantic -Werror` (or the project's equivalent strict flags).
- All tests must pass with zero failures.
- `cppcheck --enable=all` must produce zero errors; warnings should be reviewed and reported.
- If `clang-tidy` is configured (`.clang-tidy` present), zero diagnostics required on changed files.
- If `clang-format` is configured (`.clang-format` present), formatting compliance is required; treat violations as blockers.
- If Valgrind is available, run it on the test suite; treat memory leaks, invalid reads/writes, or use-after-free as blockers.
- If AddressSanitizer is available, run tests with `-fsanitize=address`; treat any report as a blocker.
- If ThreadSanitizer is available and the code uses threads, run tests with `-fsanitize=thread`.
- Check that all public classes and functions in header files have Doxygen-style documentation.
- Report test coverage if `gcov`/`lcov`/`llvm-cov` is available.
- For numerical code, verify results against known reference values with appropriate tolerances; never relax tolerances to make tests pass.
- Verify no compiler warnings are suppressed via pragmas without justification.
- Check for common C++ pitfalls: uninitialized variables, missing virtual destructors on base classes, slicing, dangling references.
