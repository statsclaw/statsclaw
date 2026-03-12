# Skill: scout — Project Mapping Agent

Scout maps a project's structure, exported surface, dependencies, tooling, and likely blast radius for a request. It normally runs after `triage`.

---

## Triggers

Invoke `scout` when the user asks:

- "Map the package"
- "What files are affected?"
- "What does this package export?"
- "What is the dependency structure?"
- "What functions would this change touch?"

Also invoke `scout` at the start of any non-trivial workflow unless the relevant file map is already known and current.

---

## Tools

Bash, Read, Glob, Grep

---

## Workflow

### Step 1 — Read runtime context

Read:

- `.statsclaw/CONTEXT.md`
- active project context under `.statsclaw/packages/`
- active request under `.statsclaw/runs/<request-id>/request.md` if present

Determine the active project profile from the project context.

If the package path is missing, stop and ask the user.

### Step 2 — Read project metadata

From the target project root, read profile-specific repo markers.

Examples:

- R: `DESCRIPTION`, `NAMESPACE`
- Python: `pyproject.toml`, `setup.cfg`, `pytest.ini`
- TypeScript: `package.json`, `tsconfig.json`
- Stata: `.do`, `.ado`, `.mata`, `stata.toc`, `pkg.pkg`

Extract:

- project name and version if available
- package manager or tooling
- declared dependencies
- exported modules, commands, or public surface where applicable

### Step 3 — Build the file inventory

Inspect relevant source and support files:

- source directories (`R/`, `src/`, `app/`, `lib/`, `package/`, etc.)
- test directories
- docs directories
- tutorial, examples, notebook, or demo directories
- build and packaging files

### Step 4 — Build the impact map

Identify:

- exported functions, modules, endpoints, commands, or public APIs
- key internal helpers or components
- callers and callees of the target code path when applicable
- files likely affected by the request
- public surfaces at risk: docs, tests, examples, tutorials, demos, notebooks, types, schemas

### Step 5 — Save the impact report

Use `templates/stage-report.md` and save to:

```text
.statsclaw/runs/<request-id>/impact.md
```

Update run status to:

- `Current State: SCOPED`
- `Current Owner: theorist` or `builder`

Updating `.statsclaw/runs/<request-id>/status.md` is mandatory before handoff.

---

## Quality Checks

- Do not guess function locations; verify them
- Respect the active project profile when choosing what metadata to inspect
- Flag broken exports or undocumented public interfaces
- Flag profile-relevant docs or build surfaces where follow-up work is likely required

---

## Output Format

- `.statsclaw/runs/<request-id>/impact.md`
- concise summary of blast radius and the recommended next agent
