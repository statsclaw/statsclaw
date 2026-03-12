# StatsClaw Guide

StatsClaw is a framework-only product for Claude Code. It provides a closed-loop workflow for code work across multiple languages without storing user runtime state in the repository.

## What This Repository Contains

- `CLAUDE.md` — the orchestrator and workflow policy
- `skills/` — specialist agent definitions
- `profiles/` — language and project-type execution rules
- `templates/` — structured artifacts for requests, specs, audits, docs, reviews, and release handoffs

StatsClaw ships the framework only. User runtime state lives under `.statsclaw/` locally and is ignored by git.

## Zero-Config Use

1. Clone the repository.
2. Open it in Claude Code.
3. Tell Claude the target project path and the work you want done.

StatsClaw will auto-create the local runtime when needed:

- `.statsclaw/CONTEXT.md`
- `.statsclaw/packages/`
- `.statsclaw/runs/`
- `.statsclaw/logs/`
- `.statsclaw/tmp/`

The user does not need to run setup scripts or manually fill runtime files.

For non-trivial requests, StatsClaw is expected to persist workflow state under `.statsclaw/runs/<request-id>/`, including `request.md`, `status.md`, and stage artifacts as the work progresses.

## Product Model

StatsClaw separates framework files from runtime files.

Framework files stay in git:

- `CLAUDE.md`
- `README.md`
- `docs/README.md`
- `skills/`
- `profiles/`
- `templates/`

Runtime files stay local:

- `.statsclaw/CONTEXT.md`
- `.statsclaw/packages/*.md`
- `.statsclaw/runs/*`
- `.statsclaw/logs/*`
- `.statsclaw/tmp/*`

This keeps the product clean and avoids tracking user package paths, work history, generated specs, or diagnostic reports.

## Closed-Loop Workflow

Standard flow:

```text
triage → scout → theorist? → builder → auditor → scribe → skeptic → release?
```

Issue-driven flow can begin with:

```text
github → triage → scout → ...
```

The workflow is language-agnostic. Execution details come from the active project profile and optional project-context overrides.

Users do not need to explicitly name agents or write rigid trigger phrases. StatsClaw is intended to infer intent from natural language and route the work automatically.

Profiles currently supported:

- `r-package`
- `python-package`
- `typescript-package`
- `stata-project`

Meaning:

- `theorist` runs when the request changes mathematical or algorithmic logic
- `scribe` runs after validation so docs match the final implementation
- `skeptic` reviews the finished change set
- `release` runs only when the user explicitly asks to ship
- `github` handles issues, PRs, checks, and queue-driven intake when work begins from GitHub

For non-trivial requests, StatsClaw should continue through the selected workflow automatically. It should not pause between stages just to ask for "go on" or "continue" unless a real blocking condition exists.

Targeted variants:

- GitHub issue intake: `github → triage → scout → ...`
- mapping only: `triage → scout`
- validation only: `triage → auditor`
- docs only: `triage → scout → scribe → skeptic`
- release only: `triage → skeptic → release`

The GitHub agent can maintain a recurring scan schedule inside the Claude-side workflow layer. Example:

- every day at `00:00 America/Los_Angeles`
- scan the target repo's open issues
- build an actionable queue
- activate the full StatsClaw workflow for the top actionable issue
- after a successful solve, push the work to a branch and comment on the issue with the resolution summary

This schedule belongs to StatsClaw runtime state and is managed inside Claude-side orchestration rather than external GitHub Actions.

Users do not need to fill schedule fields manually. StatsClaw should parse natural-language instructions such as:

- "每天 0 点 PT 扫描"
- "每周一早上 9 点扫一次"
- "只看 bug label"
- "自动激活整个 workflow 去解决"

GitHub access preference:

- preferred: `gh` CLI if it is installed and authenticated
- fallback: GitHub REST API via `GH_TOKEN` or `GITHUB_TOKEN`
- if neither exists, the GitHub agent should pause with a clear HOLD instead of silently failing

Issue-resolution policy:

- after an issue-driven workflow succeeds, StatsClaw should push the resulting changes to the corresponding branch
- it should also comment on the GitHub issue with the branch and PR status plus a short resolution summary
- it must not auto-close the issue

## Agent Roles

### `triage`

- structures the user request
- defines acceptance criteria
- selects the workflow path
- creates the local run contract

Produces:

- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/status.md`

### `github`

- inspects issues, PRs, review comments, labels, and checks
- converts actionable GitHub items into StatsClaw runs
- supports daily issue queue maintenance

Produces:

- `.statsclaw/runs/<request-id>/github.md`
- optionally `.statsclaw/runs/<request-id>/request.md`
- optionally `.statsclaw/runs/<request-id>/status.md`

### `scout`

- maps project structure
- identifies exports, internal helpers, dependencies, tooling, and affected files

Produces:

- `.statsclaw/runs/<request-id>/impact.md`

### `theorist`

- converts mathematical intent into an implementation-ready specification
- blocks hidden invention

Produces:

- `.statsclaw/runs/<request-id>/spec.md`

### `builder`

- implements the scoped code change
- preserves profile-specific conventions
- keeps scope surgical

Produces:

- target project code changes
- `.statsclaw/runs/<request-id>/implementation.md`

### `auditor`

- runs profile-aware checks, tests, examples, docs builds, and tutorial renders
- diagnoses failures and routes them back correctly

Produces:

- `.statsclaw/runs/<request-id>/audit.md`

### `scribe`

- updates profile-appropriate docs, examples, and tutorials
- aligns docs with the validated implementation

Produces:

- target project documentation updates
- `.statsclaw/runs/<request-id>/docs.md`

### `skeptic`

- reviews the full finished change set
- challenges test depth, validation completeness, and documentation freshness

Produces:

- `.statsclaw/runs/<request-id>/review.md`

### `release`

- prepares changelog, versioning, commit, PR, and handoff artifacts
- runs only when explicitly requested

Produces:

- `.statsclaw/runs/<request-id>/release.md`

## State Model

Each request should move through explicit states:

- `NEW`
- `TRIAGED`
- `SCOPED`
- `SPEC_READY`
- `IMPLEMENTED`
- `VALIDATED`
- `DOCUMENTED`
- `REVIEW_PASSED`
- `READY_TO_RELEASE`
- `DONE`

Blocking states:

- `HOLD`
- `BLOCKED`
- `STOPPED`

Suggested run layout:

```text
.statsclaw/runs/<request-id>/
├── request.md
├── github.md
├── impact.md
├── spec.md
├── implementation.md
├── audit.md
├── docs.md
├── review.md
├── release.md
└── status.md
```

## Workflow Signals

### `HOLD`

Raised when the request is ambiguous or would require invention.

Typical owners:

- `triage`
- `theorist`
- `builder`
- `scribe`

### `BLOCK`

Raised when validation fails.

Typical owner:

- `auditor`

### `STOP`

Raised when the change is not safe to ship even though implementation may be complete.

Typical owner:

- `skeptic`

## Repository Map

- `CLAUDE.md` — orchestration policy
- `README.md` — short product overview
- `docs/README.md` — single complete user guide
- `skills/` — agent definitions
- `profiles/` — language and project-type rules
- `templates/` — workflow contracts
- `.statsclaw/` — local runtime state, created after bootstrap

## First Prompt Suggestions

```text
Work on ~/GitHub/fect and triage this request.

Inspect open GitHub issues for the active project, build an actionable queue, and route the top issue into the workflow.

For /Users/tianzhuqin/GitHub/fect, every day at 00:00 America/Los_Angeles, scan open GitHub issues, pick the top actionable one, and activate the full StatsClaw workflow to solve it.

处理 /Users/tianzhuqin/GitHub/fect。每天 0 点 PT 扫描 open issues，只看 bug label，并自动激活整个 workflow 去解决。

Work on ~/GitHub/fect and map the project files affected by this estimator change.

Work on ~/GitHub/fect and implement this method, validate it, document it, review it, and prepare a release handoff.

Work on ~/project/my_python_lib and adapt the workflow automatically for this repository.

Work on ~/GitHub/fect, read ~/papers/method.pdf, extract the estimator, formalize it, and implement it in the project.
```
