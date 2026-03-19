# Profile: Python Package

## Repo Markers

Detect this profile when the target repository contains:

- `pyproject.toml` or `setup.py` or `setup.cfg` (at least one required)
- `src/` directory or a top-level package directory with `__init__.py`
- `tests/` directory

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Unit tests | `pytest` | Core test suite |
| Tests + coverage | `pytest --cov` | With coverage reporting |
| Type check | `mypy .` or `mypy src/` | Static type analysis |
| Lint | `ruff check .` | Fast linting |
| Format check | `ruff format --check .` | Formatting verification |
| Build | `python -m build` | Produces sdist and wheel |

## Documentation

- **API docs**: Docstrings in source files (NumPy or Google style)
- **Type annotations**: Inline type hints on all public functions and methods
- **Docs site**: Sphinx (`docs/`) or MkDocs (`mkdocs.yml`) when present
- **README**: `README.md` or `README.rst` at the repo root
- **CHANGELOG**: `CHANGELOG.md` or `CHANGES.rst` for user-visible changelog

## Common Tooling

- `pytest` — test framework
- `mypy` — static type checker
- `ruff` — linter and formatter
- `uv` or `pip` — dependency management
- `sphinx` or `mkdocs` — documentation site generation
- `coverage` / `pytest-cov` — test coverage reporting

## Build Exclusions

**Note**: Workflow logs are synced to the workspace repo; architecture diagrams stay in the local run directory. Neither is stored in the target repo. No `MANIFEST.in` or setuptools exclusions are needed for these artifacts. See `skills/workspace-sync/SKILL.md`.

## Builder Notes

- Follow PEP 8 style conventions; prefer `ruff` auto-formatting when the project uses it.
- Use type hints on all public function signatures; prefer `from __future__ import annotations` for modern annotation syntax.
- Place tests in `tests/` mirroring the source layout (e.g., `tests/test_module.py` for `src/package/module.py`).
- Do not add new dependencies to `pyproject.toml` without noting it in the mailbox for leader review.
- Use `__all__` in `__init__.py` to control the public API when the package follows that convention.
- Prefer raising specific exception types over bare `Exception`.
- Use `pathlib.Path` over `os.path` for filesystem operations unless the project has an established convention.

## Tester Notes

- Run `pytest` with coverage (`--cov`) and report the coverage percentage for changed modules.
- `mypy` must pass with zero errors on the changed files at minimum; prefer whole-project type check.
- `ruff check` must pass with zero errors; treat all lint violations as blockers.
- If the project uses `ruff format`, verify formatting compliance.
- If Sphinx or MkDocs docs exist, confirm they build without warnings.
- Check that all new public functions have docstrings.
