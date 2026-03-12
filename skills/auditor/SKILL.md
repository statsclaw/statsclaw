# Skill: auditor — Validation Agent

Auditor runs the project validation suite and decides whether the request is ready for documentation or must route back for fixes.

---

## Triggers

Invoke `auditor` when the user asks to:

- check the package
- run tests
- run examples
- diagnose failures
- verify CRAN readiness

Also invoke `auditor` after `builder` for any non-trivial change.

---

## Tools

Bash, Read

---

## Workflow

### Step 1 — Read runtime artifacts

Read:

- `.statsclaw/CONTEXT.md`
- active project context
- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/implementation.md`
- `.statsclaw/runs/<request-id>/spec.md` if present

Set `PKG` to the package path from the active project context.

Determine validation behavior from:

- the active project profile in `profiles/`
- explicit commands in the project context

### Step 2 — Run mandatory validation

Run the configured validation commands for the active profile.

```bash
[validation command 1]
[validation command 2]
[validation command 3]
```

Examples:

- R: `devtools::check()`, `devtools::test()`, `devtools::run_examples()`
- Python: `pytest`, `ruff check .`, `mypy .`
- TypeScript: `npm test`, `npm run lint`, `npm run typecheck`

If the project has a docs build, tutorial, demo, or notebook workflow that is relevant to the request, run it when required.

### Step 3 — Cross-check the results

If a spec exists, verify that observed results match the claimed mathematical behavior.

Raise a **BLOCK** if:

- any ERROR or WARNING occurs
- examples fail
- tutorial render fails when required
- docs build fails when required
- results are numerically implausible
- tests are structural-only and do not validate changed behavior

### Step 4 — Save the diagnostic report

Use `templates/diagnostic-report.md` and save to:

```text
.statsclaw/runs/<request-id>/audit.md
```

If validation passes, update run status to:

- `Current State: VALIDATED`
- `Current Owner: scribe`

If validation fails, update status to:

- `Current State: BLOCKED`
- `Current Owner: builder` or `theorist` or `scribe`

---

## Quality Checks

- Run the profile-appropriate validation set, not just one command
- Do not claim success without executing the commands
- Report numeric deviations as relative error when relevant
- Note runtime/tool versions when relevant to the failure

---

## Output Format

- `.statsclaw/runs/<request-id>/audit.md`
- one-paragraph routing summary
