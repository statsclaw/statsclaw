# StatsClaw Guide

StatsClaw is a framework-only product for Claude Code. It provides an Agent Teams-first workflow for code work across multiple languages without storing user runtime state in the repository.

## What This Repository Contains

- `CLAUDE.md` — the layered orchestration policy
- `.agents/` — isolated internal agent definitions
- `skills/` — shared protocol skills
- `profiles/` — language and project-type execution rules
- `templates/` — per-agent input/output templates plus shared runtime contracts

StatsClaw ships the framework only. User runtime state lives under `.statsclaw/` locally and is ignored by git.

The repository also enables Claude Code Agent Teams experimentally at the project level through `.claude/settings.json`.

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

For non-trivial requests, StatsClaw is expected to persist workflow state under `.statsclaw/runs/<request-id>/`, including `request.md`, `status.md`, `impact.md`, and stage artifacts as the work progresses.

## Product Model

StatsClaw separates framework files from runtime files.

Framework files stay in git:

- `CLAUDE.md`
- `README.md`
- `docs/README.md`
- `.agents/`
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

## Layered Workflow

Default flow:

```text
lead → theorist? → builder → auditor → scribe? → skeptic → github?
```

Issue-driven flow can begin with:

```text
github → lead → ...
```

The workflow is language-agnostic. Execution details come from the active project profile and optional project-context overrides.

Users do not need to explicitly name agents or write rigid trigger phrases. StatsClaw is intended to infer intent from natural language and route the work automatically.

Profiles currently supported:

- `r-package`
- `python-package`
- `typescript-package`
- `stata-project`

Meaning:

- `lead` owns both the request contract and the impact map
- `theorist` runs only when the request changes mathematical or algorithmic logic
- `scribe` runs only when docs, examples, or tutorials are actually affected
- `auditor` produces validation evidence
- `skeptic` reviews that evidence and issues the final ship gate
- `github` handles issues, PRs, checks, queue-driven intake, and ship-facing GitHub actions

For non-trivial requests, StatsClaw should continue through the selected workflow automatically. It should not pause between stages just to ask for "go on" or "continue" unless a real blocking condition exists.

Targeted variants:

- GitHub issue intake: `github → lead → ...`
- planning only: `lead`
- validation only: `lead → auditor`
- docs only: `lead → scribe → skeptic`
- ship only: `lead → skeptic → github`

## Agent Teams-First Execution

When Claude Code Agent Teams is available, StatsClaw should prefer:

- one Team Lead: `lead`
- three to five active teammates for broad interdependent work
- a shared task list under `.statsclaw/runs/<request-id>/tasks/`
- a shared message log under `.statsclaw/runs/<request-id>/mailbox.md`

The mailbox exists so teammates can announce interface changes, blockers, and handoff notes without forcing everyone to rediscover the same context.

For stronger isolation, writing teammates should either:

- operate in separate worktrees, or
- hold exclusive locks for their assigned write surfaces under `.statsclaw/runs/<request-id>/locks/`

In both modes:

- only `lead` updates `status.md` and lock ownership
- teammates write only their own stage artifact plus append-only mailbox messages

StatsClaw separates:

- `.agents/` for fixed agent identity, authority, and I/O boundaries
- `skills/` for shared protocols such as mailbox use, lock discipline, and handoff rules
- `templates/` for per-agent input/output contracts plus a small set of shared runtime contracts

The output templates name the runtime artifacts each agent must leave behind. The shared runtime templates define the canonical shapes for the local files that keep the workflow connected across stages.

## Layer Responsibilities

### `Control`

#### `lead`

- creates or resumes the active run
- owns routing, retries, ownership changes, and the state machine
- writes the canonical request contract and impact map once
- creates and maintains the shared task list and mailbox

Produces:

- `.statsclaw/runs/<request-id>/status.md`
- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md`
- `.statsclaw/runs/<request-id>/tasks/*.md`
- `.statsclaw/runs/<request-id>/mailbox.md`
- `.statsclaw/runs/<request-id>/locks/*.md`

### `Planning`

#### `theorist`

- converts mathematical intent into an implementation-ready specification
- blocks hidden invention

Produces:

- `.statsclaw/runs/<request-id>/spec.md`

### `Production`

#### `builder`

- implements the scoped code change
- preserves profile-specific conventions
- updates tests when behavior changes

Produces:

- target project code changes
- `.statsclaw/runs/<request-id>/implementation.md`

#### `scribe`

- updates profile-appropriate docs, examples, and tutorials
- aligns docs with the validated implementation and lead-owned docs surface

Produces:

- target project documentation updates
- `.statsclaw/runs/<request-id>/docs.md`

### `Assurance`

#### `auditor`

- runs profile-aware checks, tests, examples, docs builds, and tutorial renders
- records evidence and diagnoses failures

Produces:

- `.statsclaw/runs/<request-id>/audit.md`

#### `skeptic`

- reviews the full finished change set
- challenges test depth, validation completeness, and documentation freshness
- decides whether the change is safe to externalize

Produces:

- `.statsclaw/runs/<request-id>/review.md`

### `Externalization`

#### `github`

- inspects issues, PRs, review comments, labels, and checks
- normalizes actionable GitHub items into StatsClaw inputs
- handles commit, push, PR creation, versioning, and issue follow-up when shipping is requested

Produces:

- `.statsclaw/runs/<request-id>/github.md`

## State Model

Each request should move through explicit states:

- `NEW`
- `PLANNED`
- `SPEC_READY`
- `IMPLEMENTED`
- `VALIDATED`
- `DOCUMENTED`
- `REVIEW_PASSED`
- `READY_TO_SHIP`
- `DONE`

Blocking states:

- `HOLD`
- `BLOCKED`
- `STOPPED`

Suggested run layout:

```text
.statsclaw/runs/<request-id>/
├── request.md
├── status.md
├── impact.md
├── github.md
├── spec.md
├── implementation.md
├── audit.md
├── docs.md
├── review.md
├── mailbox.md
├── locks/
└── tasks/
```

## Workflow Signals

### `HOLD`

Raised when the request is ambiguous or would require invention.

Typical owners:

- `lead`
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
- `.agents/` — isolated agent definitions
- `skills/` — shared protocol skills
- `profiles/` — language and project-type rules
- `templates/` — workflow contracts
- `.statsclaw/` — local runtime state, auto-created at runtime

## First Prompt Suggestions

```text
Work on ~/GitHub/fect and have the Team Lead plan this request once before implementation.

Inspect open GitHub issues for the active project, build an actionable queue, and route the top issue into the workflow.

For /Users/tianzhuqin/GitHub/fect, every day at 00:00 America/Los_Angeles, scan open GitHub issues, pick the top actionable one, and activate the full StatsClaw workflow to solve it.

处理 /Users/tianzhuqin/GitHub/fect。每天 0 点 PT 扫描 open issues，只看 bug label，并自动激活整个 workflow 去解决。

Work on ~/GitHub/fect and have the Team Lead map the project once, then implement this estimator change.

Work on ~/GitHub/fect and implement this method, validate it, document it, review it, and prepare a ship handoff.

Work on ~/project/my_python_lib and adapt the workflow automatically for this repository.

Work on ~/GitHub/fect, read ~/papers/method.pdf, formalize the estimator, and implement it in the project.
```
