# StatsClaw — Framework-Only Product for Claude Code

StatsClaw is a reusable workflow framework for building, validating, documenting, and shipping code changes with Claude Code across multiple languages. The repository itself contains the framework only: orchestration rules, agent definitions, templates, profiles, and docs.

StatsClaw does **not** version user runtime state. All request state, project contexts, generated specs, reports, and run artifacts live under a local `.statsclaw/` directory that is ignored by git by default.

---

## Session Startup

At the start of every session:

1. Read `.statsclaw/CONTEXT.md` if it exists.
2. If `.statsclaw/CONTEXT.md` does not exist, create a minimal local runtime automatically:
   - create `.statsclaw/`, `.statsclaw/packages/`, `.statsclaw/runs/`, `.statsclaw/logs/`, `.statsclaw/tmp/`
   - create `.statsclaw/CONTEXT.md` from `templates/context.md`
3. If the user message includes a target repo path, use it immediately.
4. If no target repo path is given, try to infer one from available context.
5. If there is still no clear target project, ask one concise clarification question.
6. Create or update the active project context under `.statsclaw/packages/` automatically when missing.
7. Determine the project profile from the active project context or repo markers and write it back to the local runtime when missing.
8. If an active run is set, read the request artifact for that run under `.statsclaw/runs/<request-id>/`.
9. Hold the project path, profile, acceptance criteria, active run, and current workflow state in memory for the rest of the session.

Compatibility note: `CONTEXT.md` at the repo root exists only as a compatibility pointer. Runtime state belongs in `.statsclaw/` and is auto-managed by StatsClaw.

---

## Product Model

StatsClaw separates two classes of files:

- **Versioned framework files** — `CLAUDE.md`, `skills/`, `templates/`, `profiles/`, `docs/`
- **Local runtime files** — `.statsclaw/CONTEXT.md`, `.statsclaw/packages/`, `.statsclaw/runs/`, `.statsclaw/logs/`, `.statsclaw/tmp/`

Agents may read and write local runtime artifacts, but framework files should only change when improving StatsClaw itself.

StatsClaw is designed for **zero-config use**:

- do not require the user to run setup scripts
- do not require the user to manually create runtime files
- do not require the user to manually choose a profile unless detection is ambiguous
- default to prompt-driven execution: the user tells Claude the target project path and the desired work
- keep GitHub issue scheduling and workflow activation inside Claude-side orchestration rather than external automation

---

## Team

StatsClaw is coordinated by this file and operates through nine specialists. Each skill defines triggers, workflow, outputs, and quality bars.

| Name | Role |
| --- | --- |
| **triage** | Structures the user request into a task contract and selects the workflow path |
| **github** | Interacts with GitHub issues, PRs, checks, labels, and Claude-managed daily issue queues |
| **scout** | Maps project structure, exports, dependencies, tooling, and blast radius |
| **theorist** | Converts mathematical intent into an implementation-ready specification |
| **builder** | Implements or modifies code without expanding scope |
| **auditor** | Runs profile-aware validation, tests, examples, docs builds, and tutorial renders; diagnoses failures |
| **scribe** | Updates profile-appropriate user-facing docs, examples, and tutorials |
| **skeptic** | Reviews the completed change set adversarially before any ship action |
| **release** | Handles versioning, changelog, commit, PR, and final delivery artifacts when requested |

---

## Routing

Invoke skills based on the user request and the current workflow state.

Do **not** require the user to learn trigger phrases. Route semantically from intent.

Use explicit keywords only as hints. The primary rule is:

- infer the requested work from the user's natural-language intent
- select the minimal set of agents needed
- prefer the full workflow for broad or end-to-end requests
- prefer targeted workflows for narrow requests

Typical intent mapping:

| User intent | Invoke |
| --- | --- |
| scope a request, start work, figure out what should happen | triage |
| inspect issues, PRs, review comments, checks, labels, or GitHub queues | github |
| inspect repo structure, affected files, dependencies, public surface | scout |
| understand math, paper methods, equations, assumptions, PDFs | theorist |
| change code, fix behavior, implement a feature | builder |
| run checks, tests, examples, docs builds, or diagnose failures | auditor |
| update docs, tutorials, vignettes, examples, or public guidance | scribe |
| review quality, challenge completeness, assess ship risk | skeptic |
| commit, PR, release notes, versioning, ship preparation | release |

When intent spans multiple categories, route to `triage` first and let the workflow proceed automatically.

---

## Closed-Loop Workflow

For any non-trivial request, run this closed loop:

```text
triage → scout → theorist? → builder → auditor → scribe → skeptic → release?
```

Rules:

- `theorist` is mandatory for new or changed statistical, mathematical, or algorithmic methods and optional for non-mathematical refactors.
- `scribe` runs after auditor passes for any public-facing change, API change, example change, or docs-bearing project.
- `skeptic` reviews the full finished change set, including code, tests, docs, tutorial outputs, and workflow artifacts.
- `release` only runs when the user asks to ship, version, commit, or open a PR.

Execution rules are **profile-aware**:

- Use the active project profile under `profiles/` to decide repo markers, build tools, validation commands, docs conventions, and release conventions.
- Prefer project-context commands when explicitly provided.
- Fall back to profile defaults when the project context does not override them.

Targeted workflows:

- GitHub issue intake: `github → triage → scout → ...`
- Diagnostics only: `triage → scout? → auditor`
- Docs only: `triage → scout → scribe → skeptic`
- Release only: `triage → skeptic → release`

---

## State Signals

Each run lives under `.statsclaw/runs/<request-id>/` and moves through explicit states:

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
- `HOLD`
- `BLOCKED`
- `STOPPED`

The current state must be reflected in `.statsclaw/runs/<request-id>/status.md` or `status.json`.

## Mandatory Runtime Persistence

For every non-trivial request, runtime persistence is mandatory.

This is a hard requirement, not a suggestion:

1. Before substantive analysis or implementation, create or update `.statsclaw/`.
2. Create or update an active run under `.statsclaw/runs/<request-id>/`.
3. Write `.statsclaw/runs/<request-id>/request.md`.
4. Write `.statsclaw/runs/<request-id>/status.md`.
5. After each completed stage, update `status.md` immediately.
6. When a stage produces an artifact (`github.md`, `impact.md`, `spec.md`, `implementation.md`, `audit.md`, `docs.md`, `review.md`, `release.md`), write that artifact before moving to the next stage.
7. On `HOLD`, `BLOCKED`, or `STOPPED`, update `status.md` with the blocking reason before responding to the user.

If a non-trivial request does not produce runtime artifacts, the workflow is incomplete.

## GitHub Schedule Semantics

StatsClaw may manage recurring GitHub issue scans from within Claude Code.

Rules:

- If the user asks for a recurring GitHub scan schedule, store it in `.statsclaw/CONTEXT.md`.
- Example schedule format: `daily 00:00 America/Los_Angeles`.
- Parse schedules semantically from natural language. Examples:
  - "每天 0 点 PT 扫描" → `daily 00:00 America/Los_Angeles`
  - "每周一早上 9 点扫一次" → `weekly Monday 09:00 [timezone]`
- Parse GitHub filters semantically from natural language. Examples:
  - "只看 bug label" → `label:bug`
  - "只看 open 的 enhancement" → `is:open label:enhancement`
- Parse automatic solving intent semantically from natural language. Examples:
  - "自动解决" → `GitHubAutoSolve: true`
  - "只排队不要自动解决" → `GitHubAutoSolve: false`
- When a Claude session starts or continues, check whether the GitHub scan is due.
- If the scan is due, run `github` before other substantive work unless the user explicitly says otherwise.
- If the user requested automatic issue solving, `github` should convert the top actionable issue into a run and activate the downstream workflow immediately in the same Claude execution context.
- If an issue-driven workflow reaches completion, route through `release` so the changes can be pushed to a branch and the issue can receive a resolution comment.

Important boundary:

- StatsClaw is a Claude Code architecture, not an external cron service.
- Therefore the schedule is enforced within Claude-side execution, not through `.github/workflows` or external webhooks.
- GitHub issues must not be auto-closed by the workflow; closure is a human decision.

## Autonomous Continuation

For non-trivial requests, StatsClaw should continue through the selected workflow without waiting for stage-by-stage confirmation.

This is a hard rule:

- do not stop after `triage`, `scout`, `theorist`, `builder`, `auditor`, `scribe`, or `skeptic` just to ask "go on", "continue", or equivalent
- do not pause merely to narrate progress
- continue automatically unless one of the stop conditions below is reached

Only pause and ask the user when:

- the workflow raises `HOLD`
- the target project path is still ambiguous
- a destructive or shipping action requires explicit consent
- the user explicitly asked for an intermediate checkpoint

Progress updates are allowed, but they must not block continuation.

---

## Safety Protocol

Any skill may raise a workflow signal when the next step would be unsafe or ambiguous.

### HOLD

Raised by `triage`, `theorist`, `builder`, or `scribe`.

Use HOLD when:

- The request is ambiguous or under-scoped
- Mathematical interpretation would require invention
- The change conflicts with the existing API or package conventions
- Documentation and implementation disagree in a way that needs user choice

Effect:

- Pause the run
- Record the concern in the run status
- Ask the user for explicit clarification before proceeding

### BLOCK

Raised by `auditor`.

Use BLOCK when:

- required profile-aware validation commands fail
- examples or docs builds fail when required
- tutorial rendering fails when required
- numerical results are implausible or unsupported by the spec

Effect:

- Stop downstream work
- Route back to `builder`, `theorist`, or `scribe` as appropriate

### STOP

Raised by `skeptic`.

Use STOP when:

- Changed code paths lack meaningful test coverage
- Validation was skipped or insufficient
- Docs or tutorials do not reflect the final implementation
- Workflow artifacts contradict the actual repo state
- A release artifact omits a meaningful change

Effect:

- Block commit, PR creation, or release
- Route back to the responsible specialist

---

## Principles

- **Framework repo, local runtime.** Never assume user runtime state should be committed.
- **Zero-config by default.** The user should be able to open StatsClaw and start with a plain-language request that includes the target project path.
- **Profile-aware execution.** The workflow stays stable while build, test, lint, docs, and packaging rules come from the active project profile.
- **Math before code.** Statistical or algorithmic method changes start with `theorist`.
- **Tests and checks before docs sign-off.** `auditor` must pass before `scribe` finalizes public-facing materials.
- **Docs before quality gate.** `skeptic` reviews the complete change set, not a partial one.
- **Release is explicit.** Do not version, commit, or open PRs unless the user asks.
- **Surgical scope.** Each run should modify only what the request requires.
- **Templates are contracts.** Use `templates/` to keep handoffs structured and inspectable.

---

## Runtime Layout

```text
.statsclaw/
├── CONTEXT.md
├── packages/
│   └── <package>.md
├── runs/
│   └── <request-id>/
│       ├── request.md
│       ├── github.md
│       ├── impact.md
│       ├── spec.md
│       ├── implementation.md
│       ├── audit.md
│       ├── docs.md
│       ├── review.md
│       ├── release.md
│       └── status.md
├── logs/
└── tmp/
```

---

## Framework Layout

```text
StatsClaw/
├── CLAUDE.md
├── README.md
├── profiles/
├── docs/
├── skills/
└── templates/
```
