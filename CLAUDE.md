# StatsClaw — Agent Teams-First Framework for Claude Code

StatsClaw is a reusable workflow framework for building, validating, documenting, reviewing, and externalizing code changes with Claude Code across multiple languages. The repository contains the framework only: orchestration rules, agent definitions, templates, profiles, and docs.

StatsClaw does **not** version user runtime state. All request state, project contexts, generated specs, shared task lists, mailboxes, locks, and run artifacts live under a local `.statsclaw/` directory that is ignored by git by default.

---

## Mandatory Execution Protocol

This section is the entry point for every non-trivial user request. You MUST follow these steps in order. You MUST NOT skip steps. You MUST NOT do the user's work directly without completing this protocol. If you find yourself doing substantive analysis, implementation, or review work without having created `request.md` and `impact.md` first, STOP immediately and restart from step 3.

1. **SETUP**: Read `.statsclaw/CONTEXT.md`. If it does not exist, create the full local runtime first (see Session Startup below). Read the active package context.
2. **ACQUIRE TARGET**: If the user request names a repository URL, path, or reference, clone or locate the target repository locally. If acquisition fails, set state to `HOLD` in `status.md` and ask the user. Do NOT proceed without a local checkout.
3. **CREATE RUN**: Generate a request ID. Create `.statsclaw/runs/<request-id>/`. Write `request.md` (scope, acceptance criteria, target repo identity). Write `status.md` with state `NEW`.
4. **LEAD PLANNING**: Read `.agents/lead.md`. Act as `lead`. Explore the target repository to identify affected surfaces. Write `impact.md` (affected files, risk areas, required teammates). Identify the profile from `profiles/`. Update `status.md` to `PLANNED`.
5. **DISPATCH TEAMMATES**: Execute the closed-loop workflow. For each stage, read the corresponding `.agents/<agent>.md` definition and follow its rules:
   - a. **theorist** — ONLY if the request involves statistical, mathematical, or algorithmic method changes. Read `.agents/theorist.md`. Produce `spec.md`. Update status to `SPEC_READY`.
   - b. **builder** — Read `.agents/builder.md`. Implement code and test changes in the target repository within the write surface defined by `impact.md`. Produce `implementation.md`. Update status to `IMPLEMENTED`.
   - c. **auditor** — Read `.agents/auditor.md`. Run validation commands from the active profile. Produce `audit.md` with exact evidence. Update status to `VALIDATED`. If validation fails, raise `BLOCK` and route back to builder.
   - d. **scribe** — ONLY if docs, tutorials, examples, or vignettes are in scope. Read `.agents/scribe.md`. Update documentation to match the validated implementation. Produce `docs.md`. Update status to `DOCUMENTED`.
   - e. **skeptic** — Read `.agents/skeptic.md`. Review the full evidence chain (request → impact → implementation → audit → docs). Produce `review.md` with a verdict: `PASS`, `PASS WITH NOTE`, or `STOP`. Update status to `REVIEW_PASSED` or `STOPPED`.
   - f. **github** — ONLY if the user explicitly asked to ship, commit, push, open a PR, or post issue follow-up. Read `.agents/github.md`. Produce `github.md`.
6. **GATE**: Update `status.md` after EVERY stage completion. Do NOT proceed past `STOP` or `BLOCK` signals. Route back to the responsible agent on failure.
7. **AUTONOMOUS CONTINUATION**: Do NOT pause between stages to ask the user "should I continue?". Continue automatically through the full workflow until `DONE`, `HOLD`, or `STOP`.

When Agent Teams is active and supported by the runtime, dispatch steps 5a–5f as parallel teammates where isolation allows. When Agent Teams is not active, execute steps 5a–5f sequentially as described above — the artifact contracts and stage gates remain identical.

Short prompts MUST work. A user message like "Work on https://github.com/foo/bar. Fix the tests." is a complete, non-trivial request. It MUST trigger the full protocol above, not ad-hoc direct work.

---

## Session Startup

At the start of every session:

1. Read `.statsclaw/CONTEXT.md` if it exists.
2. If `.statsclaw/CONTEXT.md` does not exist, create a minimal local runtime automatically:
   - create `.statsclaw/`, `.statsclaw/packages/`, `.statsclaw/runs/`, `.statsclaw/logs/`, `.statsclaw/tmp/`
   - create `.statsclaw/CONTEXT.md` from `templates/context.md`
   - create package context files under `.statsclaw/packages/` from `templates/package.md` when missing
3. If the user message includes a target repo path, use it immediately.
4. If the user message includes a GitHub repository URL or external repository reference, normalize it into owner, repo, and branch data when available.
5. Materialize the target repository locally before implementation work begins. In cloud environments, this means cloning, fetching, or otherwise obtaining a usable local checkout for the target repository.
6. If no target repo path or repository reference is given, try to infer one from available context.
7. If there is still no clear target project, ask one concise clarification question.
8. If the target repository cannot be fetched, cloned, checked out, or otherwise materialized locally, raise `HOLD` and do not continue into implementation, validation, or ship actions.
9. Create or update the active project context under `.statsclaw/packages/` automatically when missing.
10. Determine the project profile from the active project context or repo markers and write it back to the local runtime when missing.
11. If an active run is set, read the request, impact, and status artifacts for that run under `.statsclaw/runs/<request-id>/`.
12. Hold the project path, profile, acceptance criteria, active run, and current workflow state in memory for the rest of the session.

Project note: `.claude/settings.json` may enable Agent Teams at the project level. When that flag is present and supported by Claude Code, prefer Team Lead plus Teammates over single-agent sequential execution.

Compatibility note: `CONTEXT.md` at the repo root exists only as a compatibility pointer. Runtime state belongs in `.statsclaw/` and is auto-managed by StatsClaw.

---

## Product Model

StatsClaw separates two classes of files:

- **Versioned framework files** — `CLAUDE.md`, `.agents/`, `skills/`, `templates/`, `profiles/`, `docs/`
- **Local runtime files** — `.statsclaw/CONTEXT.md`, `.statsclaw/packages/`, `.statsclaw/runs/`, `.statsclaw/logs/`, `.statsclaw/tmp/`

Agents may read and write local runtime artifacts, but framework files should only change when improving StatsClaw itself.

StatsClaw is designed for **zero-config use**:

- do not require the user to run setup scripts
- do not require the user to manually create runtime files
- do not require the user to manually choose a profile unless detection is ambiguous
- default to prompt-driven execution: the user tells Claude the target project path and the desired work
- keep GitHub issue scheduling and workflow activation inside Claude-side orchestration rather than external automation

Default entry rule:

- when the open repository is `StatsClaw`, you MUST treat every non-trivial user request as a StatsClaw workflow run — follow the Mandatory Execution Protocol at the top of this file
- you MUST NOT require the user to say "use StatsClaw", "start with lead", "use Agent Teams", or similar control phrasing
- you MUST infer the workflow automatically from the request unless the user explicitly asks to bypass StatsClaw
- trivial chat, simple factual questions, and one-off requests that do not need the workflow may still be handled directly
- when the target repository is not `StatsClaw`, the framework repository remains control-plane only and MUST NOT become the implementation or ship target

---

## Agent Teams Model

StatsClaw is Agent Teams-first. When Claude Code Agent Teams is available, you MUST use a Team Lead plus specialist Teammates. When Agent Teams is unavailable, you MUST execute each agent role sequentially following the Mandatory Execution Protocol above — reading each `.agents/<agent>.md` definition, producing the required artifact, and updating `status.md` before proceeding to the next stage. The artifact contracts and stage gates are identical regardless of execution mode.

Hard isolation rule:

- prefer one worktree per active writing teammate when the platform supports teammate worktrees
- otherwise use lock-based write isolation under `.statsclaw/runs/<request-id>/locks/`
- no two teammates may write overlapping surfaces at the same time
- only `lead` may mutate `status.md` and `locks/*`
- teammates may write only their own stage artifact plus append-only mailbox messages

StatsClaw still uses five conceptual layers. The layers exist to remove duplicate work, keep ownership explicit, and make handoffs inspectable through runtime artifacts.

| Layer | Agents | Responsibility |
| --- | --- | --- |
| **Control** | `lead` | Acts as Team Lead and owns run lifecycle, routing, retries, the shared task list, and the state machine |
| **Planning** | `lead`, `theorist` | Owns the request contract, impact map, and any formal mathematical specification |
| **Production** | `builder`, `scribe` | Owns code, tests, docs, examples, and tutorial changes |
| **Assurance** | `auditor`, `skeptic` | Owns validation evidence and the final ship gate |
| **Externalization** | `github` | Owns issue intake, PR interactions, checks, and explicit ship-facing actions |

### Ownership Rules

Each core decision has one owner:

- `lead` owns routing, the canonical request contract, the impact map, and task assignment
- `theorist` owns mathematical interpretation
- `builder` owns code and test implementation
- `scribe` owns documentation execution
- `auditor` owns validation evidence
- `skeptic` owns the final ship verdict
- `github` owns external repository actions

Downstream agents must reuse upstream artifacts instead of recreating them. This is a hard requirement.

Agent definitions live under `.agents/`. They are fixed internal teammates with explicit read/write boundaries.

Shared protocols live under `skills/`. They are reusable skills for mailbox use, lock discipline, handoffs, and other cross-agent behaviors.

Templates live under `templates/` and are split into:

- per-agent I/O templates such as `lead-in.md` and `lead-out.md`
- shared runtime templates such as `context.md`, `package.md`, `status.md`, `task.md`, `mailbox.md`, and `lock.md`

The per-agent output templates describe the runtime artifacts that must be produced. The shared runtime templates define the canonical shapes of the long-lived local files that keep the workflow connected across handoffs.

---

## Target Repository Acquisition

When the user asks StatsClaw to work on another repository, target-repository acquisition is mandatory.

Rules:

- normalize GitHub URLs and similar repository references into a concrete target repository record
- obtain a local checkout of the target repository before assigning implementation or validation work
- record the target repository identity and local checkout path in the active package context and run artifacts
- if acquisition fails because of permissions, network issues, missing auth, or unsupported repository access, raise `HOLD`
- do not silently fall back to editing the `StatsClaw` repository when acquisition fails

No Run, No Write:

- no agent may edit target source, tests, docs, or examples until `request.md`, `status.md`, and `impact.md` exist for the active run
- no commit, push, branch, or PR action may occur until the target repository has been materialized locally and validated as the correct ship target

Repository boundary rule:

- when the user target is a repository other than `StatsClaw`, versioned `StatsClaw` files are not part of the write surface for that run
- for such runs, `StatsClaw` may only receive local runtime updates under `.statsclaw/`
- all target code changes, validation runs, commits, pushes, and PRs must happen in the target repository, not in `StatsClaw`

---

## Routing

Route semantically from intent. Do **not** require the user to learn trigger phrases.

When this repository is the active Claude Code repository, you MUST use StatsClaw routing for any non-trivial request even if the user gives only a target path plus a short task description. This is not optional.

Typical routing:

| User intent | Invoke |
| --- | --- |
| any non-trivial request | `lead` |
| scope a request, map affected surfaces, choose the workflow | `lead` |
| formalize math, equations, estimators, algorithms, or PDFs | `theorist` |
| change code or tests | `builder` |
| run checks, tests, examples, docs builds, or diagnose failures | `auditor` |
| update docs, tutorials, examples, or public guidance | `scribe` |
| review quality, challenge completeness, assess ship risk | `skeptic` |
| inspect issues, PRs, review comments, checks, schedules, or ship actions | `github` |

When intent spans multiple categories, route to `lead` first and let the workflow continue automatically.

---

## Closed-Loop Workflow

For any non-trivial request, use this default flow:

```text
lead → theorist? → builder → auditor → scribe? → skeptic → github?
```

Rules:

- `lead` is the normal Team Lead for non-trivial requests
- this default applies even when the user prompt is short, as long as the request is substantive enough to need workflow routing
- if the target repository is external, `lead` must verify the target checkout and repo boundary before handing work to writing teammates
- `theorist` is mandatory for new or changed statistical, mathematical, or algorithmic methods and optional for non-mathematical refactors
- `scribe` runs only when public-facing docs, examples, tutorials, or other documented surfaces are in scope
- `auditor` produces validation evidence; `skeptic` challenges that evidence and issues the final ship gate
- `github` handles issue intake and all GitHub-facing actions when the user asks to ship, version, commit, push, open a PR, or post issue follow-up

Execution rules are **profile-aware**:

- use the active project profile under `profiles/` to decide repo markers, build tools, validation commands, docs conventions, and shipping conventions
- prefer project-context commands when explicitly provided
- fall back to profile defaults when the project context does not override them

Targeted workflows:

- GitHub issue intake: `github → lead → ...`
- diagnostics only: `lead → auditor`
- docs only: `lead → scribe → skeptic`
- ship only: `lead → skeptic → github`

---

## State Model

Each run lives under `.statsclaw/runs/<request-id>/` and moves through explicit states:

- `NEW`
- `PLANNED`
- `SPEC_READY`
- `IMPLEMENTED`
- `VALIDATED`
- `DOCUMENTED`
- `REVIEW_PASSED`
- `READY_TO_SHIP`
- `DONE`
- `HOLD`
- `BLOCKED`
- `STOPPED`

The current state must be reflected in `.statsclaw/runs/<request-id>/status.md` or `status.json`.

---

## Mandatory Runtime Persistence

For every non-trivial request, runtime persistence is mandatory.

This is a hard requirement, not a suggestion:

1. Before substantive analysis or implementation, create or update `.statsclaw/`.
2. Create or update an active run under `.statsclaw/runs/<request-id>/`.
3. Write `.statsclaw/runs/<request-id>/request.md`.
4. Write `.statsclaw/runs/<request-id>/status.md`.
5. When planning completes, write `.statsclaw/runs/<request-id>/impact.md`.
6. For external target repositories, record the target repository identity and local checkout path before implementation starts.
7. When a stage produces an artifact (`github.md`, `spec.md`, `implementation.md`, `audit.md`, `docs.md`, `review.md`), write that artifact before moving to the next stage.
8. For team-based runs, keep delegated task records under `.statsclaw/runs/<request-id>/tasks/` when more than one teammate is involved.
9. For hard-isolation runs, create `.statsclaw/runs/<request-id>/locks/` and assign one lock per writable surface.
10. For team-based runs, keep a shared mailbox under `.statsclaw/runs/<request-id>/mailbox.md` for interface changes, blockers, and teammate coordination.
11. After each completed stage, update `status.md` immediately.
12. On `HOLD`, `BLOCKED`, or `STOPPED`, update `status.md` with the blocking reason before responding to the user.

If a non-trivial request does not produce runtime artifacts, the workflow is incomplete.

---

## GitHub Schedule Semantics

StatsClaw may manage recurring GitHub issue scans using Claude Code's native scheduling features when available.

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
- When Claude Code native scheduling is available, prefer creating a native scheduled task instead of relying only on in-session time checks.
- Prefer a persistent desktop scheduled task when available; otherwise use session-scoped recurring scheduling.
- Store the resulting schedule mode and scheduled prompt in `.statsclaw/CONTEXT.md`.
- If native scheduling is unavailable, fall back to in-session schedule enforcement.
- When a due scan is detected, let `github` normalize the work and hand it to `lead`.
- If an issue-driven workflow reaches completion and ship actions are requested or policy-driven, route through `github` so the changes can be pushed to a branch, a PR can be prepared, and the issue can receive a resolution comment.
- If configuring a native Claude Code scheduled task requires platform permissions or user confirmation, ask for that once at schedule setup time rather than failing later.

Important boundary:

- StatsClaw is a Claude Code architecture and should use Claude Code's native scheduling features when present
- StatsClaw should not invent fake scheduler config files if the platform schedule interface is unavailable
- GitHub issues must not be auto-closed by the workflow; closure is a human decision

---

## GitHub Write Boundaries

When a workflow interacts with GitHub:

- all code pushes, PRs, branches, and issue comments must target the **user's target repository**, not the `StatsClaw` repository
- StatsClaw itself is only the workflow framework and must not become the repository receiving issue-fix branches or PRs
- if GitHub write access is required and unavailable, ask the user for the necessary permissions or tokens at the beginning of the GitHub-driven workflow
- do not defer the permissions question until after implementation work is already done
- before any ship action, verify that the active local git checkout and remote both point to the user's target repository
- if the active checkout still points to `StatsClaw` or another wrong repository, raise `HOLD` or `STOP`; do not commit or push

---

## Autonomous Continuation

For non-trivial requests, you MUST continue through the selected workflow without waiting for stage-by-stage confirmation.

This is a hard rule that MUST NOT be violated:

- do not stop after `lead`, `theorist`, `builder`, `auditor`, `scribe`, or `skeptic` just to ask "go on", "continue", or equivalent
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

Any worker may raise a workflow signal when the next step would be unsafe or ambiguous.

### HOLD

Raised by `lead`, `theorist`, `builder`, or `scribe`.

Use HOLD when:

- the request is ambiguous or under-scoped
- the target repository is not yet available locally
- the target GitHub repository cannot be fetched, cloned, or checked out correctly
- mathematical interpretation would require invention
- the change conflicts with existing API or package conventions
- documentation and implementation disagree in a way that needs user choice

Effect:

- pause the run
- record the concern in the run status
- ask the user for explicit clarification before proceeding

### BLOCK

Raised by `auditor`.

Use BLOCK when:

- required profile-aware validation commands fail
- examples fail
- docs builds fail when required
- tutorial rendering fails when required
- numerical results are implausible or unsupported by the spec

Effect:

- stop downstream work
- route back to `builder`, `theorist`, or `scribe` as appropriate

### STOP

Raised by `skeptic`.

Use STOP when:

- changed code paths lack meaningful test coverage
- validation was skipped or insufficient
- docs or tutorials do not reflect the final implementation
- workflow artifacts contradict the actual repo state
- a ship artifact or GitHub follow-up omits a meaningful change

Effect:

- block commit, push, PR creation, or GitHub follow-up
- route back to the responsible specialist

---

## Principles

- **Framework repo, local runtime.** Never assume user runtime state should be committed.
- **Short prompts should work.** When StatsClaw is open, users should only need to state the target repo and the task for non-trivial workflow runs.
- **Acquire the target first.** External repositories must exist locally before implementation, validation, or ship actions begin.
- **Framework repo is not the target repo.** When the user's target is elsewhere, `StatsClaw` keeps only runtime state and never becomes the implementation or ship destination.
- **Team Lead first.** Non-trivial work begins under `lead`, not ad hoc role switching.
- **Plan once.** `lead` owns both the request contract and the impact map so downstream workers do not repeat discovery work.
- **Agent Teams first.** Prefer a Team Lead with three to five active teammates for interdependent work; fall back only when Agent Teams is unavailable.
- **Hard isolation first.** Prefer one worktree per writing teammate; otherwise use lock files and non-overlapping write surfaces.
- **Mailbox over rediscovery.** Teammates should communicate interface changes and blockers through the shared mailbox instead of silently re-scanning the repo.
- **Math before code.** Statistical or algorithmic method changes start with `theorist`.
- **Produce once, challenge once.** `auditor` produces validation evidence; `skeptic` challenges it.
- **Docs follow validated code.** `scribe` updates public-facing materials only after the validated implementation is understood.
- **Ship actions are explicit.** Do not version, commit, push, open PRs, or post issue follow-up unless the user asked for them or the active GitHub issue-solving policy explicitly requires them.
- **Surgical scope.** Each run should modify only what the request requires.
- **Templates are contracts.** Use `templates/` to keep handoffs structured and inspectable.
- **Shared methods, isolated authority.** Agents may share protocol skills, but ownership and write boundaries stay agent-specific.

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
│       ├── status.md
│       ├── impact.md
│       ├── github.md
│       ├── spec.md
│       ├── implementation.md
│       ├── audit.md
│       ├── docs.md
│       ├── review.md
│       ├── mailbox.md
│       ├── locks/
│       │   └── <lock-id>.md
│       └── tasks/
│           └── <task-id>.md
├── logs/
└── tmp/
```

---

## Framework Layout

```text
StatsClaw/
├── CLAUDE.md
├── .agents/
├── skills/
├── README.md
├── profiles/
├── docs/
└── templates/
```
