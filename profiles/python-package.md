# Profile: python-package

Use this profile for Python packages, libraries, and research repositories with Python as the main implementation language.

## Repo Markers

- `pyproject.toml`
- `requirements.txt`
- `setup.py`
- `setup.cfg`
- `pytest.ini`

## Typical Validation Commands

- `pytest`
- `ruff check .`
- `mypy .`

Use only commands that exist in the target repo or are explicitly configured in the project context.

## Documentation Conventions

- docstrings
- `README.md`
- `docs/`
- `mkdocs` or `sphinx` when present
- notebooks or examples directories when relevant

## Common Tooling

- `pytest`
- `ruff`
- `mypy`
- `uv`
- `pip`

## Builder Notes

- preserve package layout and import style
- update type hints when the repo uses them
- update tests with behavior changes
- avoid introducing formatting or lint drift

## Auditor Notes

- run configured test, lint, and typecheck commands
- run docs build when it is part of the request or clearly required by the repo
- treat failing CI-equivalent checks as blockers
