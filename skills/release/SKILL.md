# Skill: release — Shipping and Handoff Agent

Release handles versioning, changelog, commit, PR, and final delivery artifacts after the workflow has already been validated and reviewed.

Release is never automatic. It only runs when the user explicitly asks to ship, commit, version, or open a PR.

---

## Triggers

Invoke `release` when the user asks to:

- create a commit
- prepare a PR
- bump the package version
- update `NEWS.md`
- prepare a release handoff
- ship the completed work

---

## Tools

Read, Write, Edit, Bash

---

## Workflow

### Step 1 — Read release prerequisites

Read:

- `.statsclaw/CONTEXT.md`
- active project context
- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/audit.md`
- `.statsclaw/runs/<request-id>/review.md`
- `.statsclaw/runs/<request-id>/docs.md` if present

Do not proceed if `skeptic` has not passed.

### Step 2 — Prepare release-facing artifacts

Depending on the request:

- update version fields
- update `NEWS.md`
- draft commit message
- prepare PR title and body
- prepare delivery notes for the user

Use `templates/stage-report.md` for the release summary.

### Step 3 — Perform ship actions only if requested

Allowed actions only with explicit user instruction:

- `git add`
- `git commit`
- `git push`
- `gh pr create`

Follow repository safety rules:

- never force push unless explicitly requested
- never commit unrelated files
- never create an empty release action

### Step 4 — Save the release artifact

Save to:

```text
.statsclaw/runs/<request-id>/release.md
```

Update run status to:

- `Current State: READY_TO_RELEASE` before ship actions
- `Current State: DONE` after ship actions complete, or after a release handoff is prepared if no git action was requested

Updating `.statsclaw/runs/<request-id>/status.md` is mandatory before and after release-stage transitions.

---

## Quality Checks

- Do not release without a passing review
- Do not version bump unless it is in scope
- Make the test plan explicit in PR output
- Keep commit and PR summaries aligned with the actual change

---

## Output Format

- `.statsclaw/runs/<request-id>/release.md`
- concise release summary
- commit and PR metadata when requested
