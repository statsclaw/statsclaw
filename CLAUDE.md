# StatsClaw — Agent Teams Framework for Claude Code

StatsClaw is a reusable workflow framework for building, validating, documenting, reviewing, and externalizing code changes with Claude Code across multiple languages. The repository contains the framework only: orchestration rules, agent definitions, templates, profiles, and docs.

StatsClaw does **not** version user runtime state. All request state, project contexts, generated specs, shared task lists, mailboxes, locks, and run artifacts live under a local `.statsclaw/` directory that is ignored by git by default.

---

## Simple Prompt Interface

**Users should never need to learn StatsClaw terminology.** A simple sentence is enough to trigger the full workflow. Lead parses natural language (any language) and routes to the correct skill or workflow automatically.

### Example Prompts That Just Work

| User types | What happens |
| --- | --- |
| `"patrol fect issues on cfe"` | Scans open issues in xuyiqing/fect, fixes bugs on `cfe` branch, pushes PRs, replies to issues |
| `"fix fect issue #42"` | Runs full workflow to fix issue #42 in fect, pushes fix, comments on the issue |
| `"check fect issues and auto-fix"` | Same as patrol — scans, triages, fixes, pushes, replies |
| `"monitor fect issues every 30min"` | Recurring patrol with 30-minute interval |
| `"fix the failing tests in fect"` | Standard fix workflow on fect repo |
| `"ship it"` | Push current changes and create PR |

### How It Works

1. Lead reads the prompt and detects intent (see `.agents/lead.md` → Simple Prompt Routing)
2. Lead resolves package names to repos (e.g., `fect` → `xuyiqing/fect` via `packages/fect.md`)
3. Lead auto-detects credentials (see `skills/credential-setup/SKILL.md`) — no manual PAT setup needed if the environment is configured
4. Lead activates the appropriate skill or workflow
5. Everything runs autonomously — user gets results, not questions

---

## Mandatory Execution Protocol

This section is the entry point for every non-trivial user request. You MUST follow these steps in order. You MUST NOT skip steps. You MUST NOT do the user's work directly without completing this protocol. If you find yourself doing substantive analysis, implementation, or review work without having created `request.md` and `impact.md` first, STOP immediately and restart from step 3.

**CRITICAL: You are the Team Lead (`lead`). You MUST use the `Agent` tool to dispatch every teammate. You MUST NOT perform teammate work yourself. If you catch yourself doing builder, auditor, scribe, skeptic, theorist, or github work directly, STOP and dispatch it to an agent instead.**

1. **SETUP**: Read `.statsclaw/CONTEXT.md`. If it does not exist, create the full local runtime first (see Session Startup below). Read the active package context.
2. **ACQUIRE TARGET**: If the user request names a repository URL, path, or reference, clone or locate the target repository locally. If acquisition fails, set state to `HOLD` in `status.md` and ask the user. Do NOT proceed without a local checkout.
3. **VERIFY CREDENTIALS**: This is the FIRST hard gate — it runs BEFORE the run is created. Follow `skills/credential-setup/SKILL.md` for the auto-detection sequence.
   - a. **Auto-detect** credentials: check `GITHUB_TOKEN` env → `gh auth status` → SSH → git credential helper (in order).
   - b. If any method succeeds, configure it and test with `git ls-remote <remote-url>`.
   - c. **Only if ALL auto-detection fails**, use `AskUserQuestion` to ask the user for a GitHub Personal Access Token (PAT) or SSH key.
   - d. Once credentials work, write `credentials.md` to the run directory recording: remote URL tested, method used (PAT/SSH/gh-cli/env-token), timestamp, and result (PASS/FAIL).
   - e. Record the credential status in the package context under `.statsclaw/packages/`.
   - **ENFORCEMENT**: Steps 4–8 are INVALID without a `credentials.md` showing PASS. If you find yourself planning or dispatching teammates without confirmed push access, STOP and return to step 3.
4. **CREATE RUN**: Generate a request ID. Create `.statsclaw/runs/<request-id>/`. Write `request.md` (scope, acceptance criteria, target repo identity). Write `status.md` with state `NEW`.
5. **LEAD PLANNING**: Read `.agents/lead.md`. Act as `lead`. Explore the target repository to identify affected surfaces. Write `impact.md` (affected files, risk areas, required teammates). Identify the profile from `profiles/`. Update `status.md` to `PLANNED`.
6. **DISPATCH TEAMMATES (Two-Pipeline Architecture)**: See "Agent Teams Model" below for the architecture. Dispatch per the selected workflow:
   - a. **theorist** — ALWAYS dispatched for non-trivial requests. **MANDATORY when the user uploads files** (PDF, Word, txt, tex, images with formulas) — these contain primary source material that theorist must deeply comprehend before any specs are produced. Pass ALL uploaded file paths in the dispatch prompt. Theorist produces `comprehension.md` (verification of understanding), `spec.md` (code pipeline), and `test-spec.md` (test pipeline). **If theorist raises HOLD with comprehension questions, lead MUST forward them to the user via `AskUserQuestion` and re-dispatch theorist with the answers. Iterate until theorist confirms FULLY UNDERSTOOD.** Update status to `SPEC_READY`.
   - b. **builder + auditor IN PARALLEL** — After theorist completes, dispatch BOTH in the SAME message. Builder gets `spec.md` ONLY. Auditor gets `test-spec.md` ONLY. Update status to `PIPELINES_COMPLETE` after BOTH complete.
   - c. **scribe** — ONLY if docs are in scope. Dispatch with `isolation: "worktree"`. Produces `docs.md`. Update status to `DOCUMENTED`.
   - d. **skeptic** — ALWAYS dispatched after both pipelines complete. Reads ALL artifacts. Produces `review.md` with verdict. Update status to `REVIEW_PASSED` or `STOPPED`.
   - e. **github** — ONLY if the user asked to ship. Produces `github.md`.
   - **PIPELINE ISOLATION**: builder NEVER receives `test-spec.md`. Auditor NEVER receives `spec.md` or `implementation.md`. See `skills/isolation/SKILL.md`.
7. **GATE**: Update `status.md` after EVERY teammate completes. Read the output artifact. Do NOT proceed past `STOP` or `BLOCK` signals. Respawn the responsible teammate on failure (max 3 retries per teammate before `HOLD`).
8. **AUTONOMOUS CONTINUATION**: Do NOT pause between stages to ask the user "should I continue?". Continue automatically through the full workflow until `DONE`, `HOLD`, or `STOP`.

Short prompts MUST work. A user message like "Work on https://github.com/foo/bar. Fix the tests." is a complete, non-trivial request. It MUST trigger the full protocol above, not ad-hoc direct work.

---

## Hard Enforcement: State Transition Preconditions

**These are hard gates, not advisory. If a precondition is not met, the state transition is INVALID.**

| Target State | Precondition | Verification |
| --- | --- | --- |
| `NEW` | `credentials.md` exists with result PASS | Read the file, confirm PASS is present |
| `NEW` | Push access to target repo confirmed | `git ls-remote` succeeded during step 3 |
| `PLANNED` | `request.md` and `impact.md` exist and are non-empty | Read the files |
| `SPEC_READY` | `comprehension.md`, `spec.md`, AND `test-spec.md` all exist | Read all three file paths |
| `SPEC_READY` | Theorist was dispatched via `Agent` tool | Agent tool call must exist in conversation |
| `PIPELINES_COMPLETE` | `implementation.md` and `audit.md` exist | Read both file paths |
| `PIPELINES_COMPLETE` | Builder dispatched with `isolation: "worktree"`, auditor dispatched | Agent tool calls must exist |
| `PIPELINES_COMPLETE` | Pipeline isolation verified | Builder prompt has no test-spec.md; auditor prompt has no spec.md |
| `PIPELINES_COMPLETE` | Lead did NOT run any validation command directly | Self-check: no Bash calls to R CMD check, pytest, npm test, etc. |
| `DOCUMENTED` | `architecture.md` and `docs.md` exist in run directory | Read both file paths |
| `REVIEW_PASSED` | `review.md` exists with verdict `PASS` or `PASS WITH NOTE` | Read the file, check verdict |
| `REVIEW_PASSED` | Skeptic was dispatched via `Agent` tool | Agent tool call must exist |
| `READY_TO_SHIP` | Status is `REVIEW_PASSED` | Read current status |
| `DONE` | Github teammate dispatched (if ship requested) | Agent tool call must exist |

**Before every `status.md` update**: read current status, verify ALL preconditions, read required artifacts, then write.

**Violation protocol**: revert `status.md`, dispatch the missing teammate, re-attempt only after precondition is satisfied.

---

## Lead Self-Check: Forbidden Direct Actions

Before EVERY tool call, `lead` MUST check whether the action belongs to a teammate.

| You are about to... | Dispatch to... |
| --- | --- |
| `Edit`/`Write` on target repo source files | `builder` |
| Run `R CMD check`, `pytest`, `npm test`, or any validation command | `auditor` |
| Run `git commit`, `git push`, `gh pr create` on target repo | `github` |
| `Edit`/`Write` on docs, tutorials, vignettes in target repo | `scribe` |
| Write mathematical specifications or derive formulas | `theorist` |
| Debug test failures by reading target repo code extensively | `auditor` |
| Review diffs or evidence chains to decide ship safety | `skeptic` |

**Concrete rule**: `lead` may use `Read`, `Grep`, `Glob` on the target repo ONLY during step 5 (LEAD PLANNING) to write `impact.md`. After `impact.md` is written, all further target-repo interaction MUST go through dispatched teammates.

**What lead IS allowed to do directly**: read/write `.statsclaw/` runtime artifacts, explore target repo during planning (step 5 only), read teammate output artifacts, update `status.md` and `locks/*`, ask user questions, dispatch teammates.

---

## How to Dispatch a Teammate

When spawning a teammate via the `Agent` tool:

1. **Set `subagent_type`** to `"general-purpose"` and **`mode`** to `"auto"`.
2. **Use `isolation: "worktree"`** for writing teammates (builder, scribe). NOT for read-only teammates.
3. **Include full context** — teammates cannot see your conversation. Pass: StatsClaw path, target repo path, run directory path, agent definition path, artifact paths, task description, write surface, profile.
4. **Name the agent** descriptively (`"builder"`, `"auditor"`, `"skeptic"`).

### Teammate Prompt Template

```
You are the [ROLE] teammate in a StatsClaw workflow.

Read your agent definition at [STATSCLAW_PATH]/.agents/[role].md and follow its rules exactly.

## Context
- StatsClaw repo: [STATSCLAW_PATH]
- Target repo: [TARGET_PATH]
- Run directory: [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/
- Profile: [PROFILE]

## Your Task
[SPECIFIC TASK DESCRIPTION]

## Write Surface
[EXACT FILES/PATHS THIS TEAMMATE MAY MODIFY]

## Required Inputs (read these files first)
- [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/request.md
- [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/impact.md
- [OTHER ARTIFACTS AS NEEDED]

## Required Output
Write your artifact to: [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/[artifact].md

## Key Rules
- Only modify files within your assigned write surface
- Do NOT modify status.md — lead will update it
- Append to mailbox.md if you encounter blockers or interface changes
- For github teammate: read credentials.md first — do NOT attempt push without PASS
```

### Dispatch Rules

**Mandatory parallel dispatch**: builder + auditor — MUST be dispatched in the SAME message after theorist completes.

**Additional parallel**: builder + scribe if non-overlapping write surfaces.

**Sequential**: theorist → (builder ∥ auditor) → skeptic → github.

**Pipeline isolation at dispatch**: builder gets `spec.md` path (NEVER `test-spec.md`). Auditor gets `test-spec.md` path (NEVER `spec.md`). Skeptic gets ALL artifacts.

---

## Session Startup

At the start of every session:

1. Read `.statsclaw/CONTEXT.md` if it exists.
2. If it does not exist, create a minimal local runtime: `.statsclaw/`, `.statsclaw/packages/`, `.statsclaw/runs/`, `.statsclaw/logs/`, `.statsclaw/tmp/`, `CONTEXT.md` from `templates/context.md`, package contexts from `templates/package.md`.
3. If the user message includes a target repo path or GitHub URL, acquire it.
4. **Verify push credentials** immediately after acquisition — follow `skills/credential-setup/SKILL.md`.
5. If no target is clear, infer from context or ask one concise question.
6. Determine the project profile using `skills/profile-detection/SKILL.md` or repo markers in `profiles/*.md`.

---

## Agent Teams Model

StatsClaw uses Agent Teams exclusively. You are the Team Lead (`lead`). You MUST use the `Agent` tool to dispatch specialist teammates. You MUST NOT perform teammate work yourself. There is no fallback mode.

### Two-Pipeline Architecture

```
              theorist (bridge)
             /                \
  spec.md  /                    \  test-spec.md
           /                      \
      builder                    auditor
  (code pipeline)          (test pipeline)
           \                      /
            \                    /
              skeptic (convergence)
                    |
                  github
```

| Layer | Agent | Pipeline | Role | Definition |
| --- | --- | --- | --- | --- |
| Control | `lead` | — | Plans, dispatches, manages state | `.agents/lead.md` |
| Analysis | `theorist` | Bridge | Produces `spec.md` AND `test-spec.md` | `.agents/theorist.md` |
| Code | `builder` | Code | Implements from `spec.md` only (worktree) | `.agents/builder.md` |
| Test | `auditor` | Test | Validates from `test-spec.md` only | `.agents/auditor.md` |
| Docs | `scribe` | Code | Updates documentation (conditional, worktree) | `.agents/scribe.md` |
| Convergence | `skeptic` | Both | Cross-compares both pipelines; ship verdict | `.agents/skeptic.md` |
| Ship | `github` | — | Commits, pushes, PRs, issue comments (conditional) | `.agents/github.md` |

**Mandatory teammates** (never skip for non-trivial requests): theorist, builder, auditor, skeptic.

**Conditional teammates**: scribe (docs in scope), github (ship requested).

Each agent's full workflow, allowed reads/writes, and must-not rules are defined in its `.agents/*.md` file. Pipeline isolation rules are in `skills/isolation/SKILL.md`. Artifact handoff rules are in `skills/handoff/SKILL.md`.

---

## Workflow Catalog

**Notation**: `∥` = parallel dispatch. `→` = sequential. `?` = conditional.

| # | Name | Trigger | Agent Sequence |
| --- | --- | --- | --- |
| 1 | Standard | Code change, no ship | `lead → theorist → [builder ∥ auditor] → skeptic` |
| 2 | With Docs | Code change + docs | `lead → theorist → [builder ∥ auditor ∥ scribe] → skeptic` |
| 3 | With Ship | Code change + ship | `lead → theorist → [builder ∥ auditor] → skeptic → github` |
| 4 | Issue Patrol | Scan + fix multiple issues | `lead scans → per issue: theorist → [builder ∥ auditor] → skeptic → github` |
| 5 | Single Issue | Fix one named issue | `lead → theorist → [builder ∥ auditor] → skeptic → github` |
| 6 | Validation | Run tests only | `lead → auditor` |
| 7 | Ship Only | Push reviewed changes | `lead → skeptic → github` |
| 8 | Review Only | Assess without shipping | `lead → skeptic` |
| 9 | Scheduled Loop | Recurring execution | `lead → /loop → inner workflow` |

**Workflow details**: Each workflow's agent cooperation, artifacts, and state transitions are documented in the respective agent definitions (`.agents/*.md`) and skills (`skills/*.md`). Key references:

- **Workflows 1–5**: Standard two-pipeline flow. See `skills/handoff/SKILL.md` for artifact flow between agents.
- **Workflow 4**: See `skills/issue-patrol/SKILL.md` for patrol phases (scan, triage, fix loop, report).
- **Workflow 6**: No theorist, builder, or skeptic. Auditor runs profile validation commands directly.
- **Workflow 9**: Lead invokes `/loop` via `Skill` tool. See "Scheduled Loop" below.

---

## Routing

Route semantically from intent. Do **not** require the user to learn trigger phrases.

| User intent | Workflow |
| --- | --- |
| any non-trivial code request | 1–3 (full pipeline) |
| "patrol issues" / "check issues and fix" / "auto-fix" | 4 (issue patrol) |
| "fix issue #N" | 5 (single issue fix) |
| "check" / "validate" / "run tests" | 6 (auditor only) |
| "ship it" / "push" / "open a PR" | 7 (skeptic → github) |
| "review" / "is this safe?" | 8 (skeptic only) |
| "loop" / "every Xm" / "monitor every" | 9 (/loop wrapping inner workflow) |
| formalize math, equations, algorithms | 1 (theorist-first pipeline) |
| update docs, tutorials, examples | 2 (pipeline with scribe) |

Routing is semantic. Lead interprets intent from natural language in any language.

---

## Scheduled Loop (Recurring Tasks)

When the user's intent involves recurring or periodic execution, lead MUST activate the `/loop` skill via the `Skill` tool.

**Trigger signals** (any language): explicit interval ("every 5m"), "loop"/"recurring"/"scheduled", "monitor"/"watch"/"keep checking", "continuously"/"repeatedly".

**Activation**: Parse interval (default `10m`) and inner command, then invoke `/loop` via `Skill` tool.

| User says | Lead invokes |
| --- | --- |
| `"patrol fect issues every 30min"` | `/loop 30m patrol fect issues on cfe` |
| `"loop run tests every 10m"` | `/loop 10m run tests` |
| `"monitor fect every 5m"` | `/loop 5m check fect` |

**Rules**: Use `Skill` tool — do NOT implement polling with `sleep`. The `/loop` skill manages its own lifecycle.

---

## Signal Handling

| Signal | Raised by | Meaning | Lead response |
| --- | --- | --- | --- |
| **HOLD** | theorist, builder, scribe | Ambiguous requirement, need user input | Pause run. Ask user via `AskUserQuestion`. Resume after clarification. |
| **BLOCK** | auditor | Validation failed | Read `audit.md`. Respawn responsible teammate (usually builder). Re-dispatch auditor after fix. |
| **STOP** | skeptic | Change is unsafe to ship | Read `review.md`. Respawn responsible teammate per skeptic's routing. Re-run from appropriate pipeline stage. |

**Max retries**: A teammate may be respawned up to **3 times** for the same issue. After 3 failures, set status to `HOLD` and ask the user for guidance.

**Signal propagation**: HOLD → ask user → resume. BLOCK → respawn → re-validate → skeptic. STOP → respawn → re-run pipelines → skeptic.

---

## State Model

Each run moves through explicit states:

`CREDENTIALS_VERIFIED` → `NEW` → `PLANNED` → `SPEC_READY` → `PIPELINES_COMPLETE` → `DOCUMENTED`? → `REVIEW_PASSED` → `READY_TO_SHIP` → `DONE`

Also: `HOLD`, `BLOCKED`, `STOPPED`

- `SPEC_READY` requires BOTH `spec.md` and `test-spec.md`
- `PIPELINES_COMPLETE` requires BOTH `implementation.md` and `audit.md`
- `CREDENTIALS_VERIFIED` is the entry gate — no run without confirmed push access
- Only `lead` may update `status.md`
- All transitions subject to the precondition table above

---

## Target Repository Boundaries

- When the user target is a repository other than `StatsClaw`, versioned `StatsClaw` files are not part of the write surface
- All target code changes, validation runs, commits, pushes, and PRs must happen in the target repository
- `StatsClaw` only receives local runtime updates under `.statsclaw/`

---

## Autonomous Continuation

For non-trivial requests, you MUST continue through the selected workflow without waiting for stage-by-stage confirmation. Only pause when: the workflow raises `HOLD`, the target is ambiguous, a destructive action requires consent, or the user asked for a checkpoint.

---

## Runtime Maintenance

- **Cleanup**: Runs older than 7 days under `.statsclaw/runs/` may be deleted to free disk space. Do not delete the active run.
- **Logs**: Write diagnostic output to `.statsclaw/logs/` when debugging workflow issues.
- **Locks**: The `locks/` directory under each run can be used to prevent concurrent writes to the same file. Use `templates/lock.md` format. Only `lead` manages locks.

---

## Principles

- **Credentials first, work second.** Verify push access before creating a run.
- **Team Lead dispatches, never does.** You plan, route, and coordinate via the `Agent` tool.
- **Two pipelines, fully isolated.** Code pipeline and test pipeline never see each other's specs. Theorist bridges; skeptic converges.
- **Theorist first, always.** Every non-trivial request starts with dual-spec production.
- **Adversarial verification by design.** Independent convergence proves correctness.
- **Hard gates, not soft advice.** State transitions have preconditions; artifacts are verified, not assumed.
- **Worktree isolation for writers.** `isolation: "worktree"` for builder and scribe.
- **Ship actions are explicit.** Do not push unless the user asked or issue-patrol is active.
- **Surgical scope.** Each run modifies only what the request requires.
- **Parallel when possible.** Builder and auditor are ALWAYS dispatched in parallel.

---

## Runtime Layout

```text
.statsclaw/
├── CONTEXT.md
├── packages/
│   └── <package>.md
├── runs/
│   └── <request-id>/
│       ├── credentials.md
│       ├── request.md
│       ├── status.md
│       ├── impact.md
│       ├── comprehension.md  # comprehension verification (from theorist, mandatory)
│       ├── spec.md           # code pipeline input (from theorist)
│       ├── test-spec.md      # test pipeline input (from theorist)
│       ├── implementation.md # code pipeline output (from builder)
│       ├── audit.md          # test pipeline output (from auditor)
│       ├── architecture.md  # system architecture diagram (from scribe, mandatory)
│       ├── docs.md
│       ├── review.md
│       ├── github.md
│       ├── mailbox.md
│       ├── locks/
│       └── tasks/
├── logs/
└── tmp/
```

---

## Framework Layout

```text
StatsClaw/
├── CLAUDE.md
├── README.md
├── .agents/
│   ├── lead.md
│   ├── theorist.md
│   ├── builder.md
│   ├── auditor.md
│   ├── scribe.md
│   ├── skeptic.md
│   └── github.md
├── skills/
│   ├── isolation/SKILL.md
│   ├── mailbox/SKILL.md
│   ├── handoff/SKILL.md
│   ├── issue-patrol/SKILL.md
│   ├── credential-setup/SKILL.md
│   └── profile-detection/SKILL.md
├── profiles/
│   ├── r-package.md
│   ├── python-package.md
│   ├── typescript-package.md
│   ├── stata-project.md
│   ├── go-module.md
│   └── rust-crate.md
├── templates/
│   ├── context.md
│   ├── package.md
│   ├── status.md
│   ├── credentials.md
│   ├── mailbox.md
│   └── lock.md
└── .statsclaw/           # local only, auto-created, git-ignored
```
