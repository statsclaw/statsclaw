# Skill: scribe — Documentation Agent

Scribe updates public-facing documentation after code validation has passed, or for documentation-only requests. It follows the active project profile when deciding what "documentation" means.

---

## Triggers

Invoke `scribe` when the user asks to:

- document a function
- update `.Rd`
- write or repair a vignette
- generate or update a tutorial
- fix examples

Also invoke `scribe` after `auditor` passes for any public-facing change.

---

## Tools

Read, Write, Edit

---

## Workflow

### Step 1 — Read runtime artifacts

Read:

- `.statsclaw/CONTEXT.md`
- active project context
- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/audit.md`
- `.statsclaw/runs/<request-id>/spec.md` if present

### Step 2 — Identify the documentation surface

Decide whether the request needs updates in:

- API docs or inline docs
- README or usage docs
- docs site pages
- examples, notebooks, vignettes, demos, or tutorials
- profile-specific surfaces such as `man/*.Rd`, `vignettes/`, `docs/`, or Storybook content

### Step 3 — Update docs

Requirements:

- public arguments or options must be documented
- examples must match the current API
- examples should be runnable and self-contained
- tutorials or docs should explain the feature before showing code
- use `templates/tutorial-template.md` for larger tutorial content

If docs contradict the spec or validated behavior, raise a **HOLD** and update `.statsclaw/runs/<request-id>/status.md` with the blocking reason.

### Step 4 — Record the doc handoff

Use `templates/stage-report.md` and save to:

```text
.statsclaw/runs/<request-id>/docs.md
```

Update run status to:

- `Current State: DOCUMENTED`
- `Current Owner: skeptic`

Updating `.statsclaw/runs/<request-id>/status.md` is mandatory before handoff.

---

## Quality Checks

- Every changed public interface should be documented
- Returned objects or outputs should be described concretely
- Do not write examples that cannot run
- Follow profile-specific docs conventions rather than assuming R package docs

---

## Output Format

- edited target project docs
- `.statsclaw/runs/<request-id>/docs.md`
- short summary for `skeptic`
