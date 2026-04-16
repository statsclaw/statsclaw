---
name: statsclaw-protocol
description: "Orchestrates multi-agent workflows (plan → build → test → document → review → ship) for code changes, simulation studies, and documentation across any language. Manages credential verification, pipeline isolation, state transitions, and signal handling (HOLD/BLOCK/STOP) with hard-gated preconditions. Use when the leader agent needs to execute the mandatory execution protocol for any non-trivial user request."
user-invocable: false
disable-model-invocation: true
---

# StatsClaw — Agent Teams Framework for Claude Code

Orchestrates multi-agent workflows for building, validating, documenting, reviewing, and shipping code changes with Claude Code across multiple languages. The leader agent dispatches specialist teammates (planner, builder, tester, simulator, scriber, distiller, reviewer, shipper) through isolated pipelines with hard-gated state transitions. The repository contains the framework only: orchestration rules, agent definitions, templates, profiles, and docs.

StatsClaw does **not** version user runtime state. All request state, project contexts, generated specs, shared task lists, mailboxes, locks, and run artifacts live inside the **workspace repository** under `.repos/workspace/<repo-name>/`. The workspace repo is a user-specified GitHub repository (e.g., `[username]/workspace`) that serves as both the runtime state directory and the permanent log archive. There is no separate `.statsclaw/` directory.

This keeps target repos clean (code + `ARCHITECTURE.md` + essential user-facing docs only). **Exception**: `ARCHITECTURE.md` is written to the target repo root so users and contributors can see the system architecture directly. See `skills/workspace-sync/SKILL.md` for details.

---

## Simple Prompt Interface

**Users should never need to learn StatsClaw terminology.** A simple sentence is enough to trigger the full workflow. Leader parses natural language (any language) and routes to the correct skill or workflow automatically.

### Example Prompts That Just Work

| User types | What happens |
| --- | --- |
| `"patrol fect issues on cfe"` | Scans open issues in xuyiqing/fect, fixes bugs on `cfe` branch, pushes PRs, replies to issues |
| `"fix fect issue #42"` | Runs full workflow to fix issue #42 in fect, pushes fix, comments on the issue |
| `"check fect issues and auto-fix"` | Same as patrol — scans, triages, fixes, pushes, replies |
| `"monitor fect issues every 30min"` | Recurring patrol with 30-minute interval |
| `"fix the failing tests in fect"` | Standard fix workflow on fect repo |
| `"ship it"` | Push current changes and create PR |
| `"simulate the finite-sample properties"` | Runs Monte Carlo simulation study (workflow 11 or 12) |
| `"run Monte Carlo for the new estimator"` | Implements estimator + runs simulation (workflow 11) |
| `"enable brain"` | Enables Brain mode — agents read shared knowledge, noteworthy discoveries are offered for contribution |
| `"turn off brain"` | Disables Brain mode — isolated mode, no shared knowledge |
| `/contribute` | Summarizes lessons learned during the session, extracts reusable knowledge, and submits to the shared brain (with user consent) |

### How It Works

1. Leader reads the prompt and detects intent (see `agents/leader.md` → Simple Prompt Routing)
2. Leader resolves package names to repos (e.g., `fect` → `xuyiqing/fect` via `.repos/workspace/fect/context.md`)
3. Leader auto-detects credentials (see `skills/credential-setup/SKILL.md`) — no manual PAT setup needed if the environment is configured
4. Leader activates the appropriate skill or workflow
5. Everything runs autonomously — user gets results, not questions

---

## Mandatory Execution Protocol

This section is the entry point for every non-trivial user request. You MUST follow these steps in order. You MUST NOT skip steps. You MUST NOT do the user's work directly without completing this protocol. If you find yourself doing substantive analysis, implementation, or review work without having created `request.md` and `impact.md` first, STOP immediately and restart from step 3.

**CRITICAL: You are the Team Leader (`leader`). You MUST use the `Agent` tool to dispatch every teammate. You MUST NOT perform teammate work yourself. If you catch yourself doing builder, tester, scriber, reviewer, planner, simulator, or shipper work directly, STOP and dispatch it to an agent instead.**

1. **SETUP**: Acquire the workspace repo (see step 2). Read `.repos/workspace/<repo-name>/context.md`. If it does not exist, create the runtime structure first (see Session Startup below). Read the active package context.
2. **ACQUIRE REPOS**: Acquire BOTH the target repo AND the workspace repo upfront. Both must be local before any work begins.
   - **Target repo (plugin mode)**: The **current working directory IS the target repo**. Do NOT clone it. Work directly in the current directory.
   - **Target repo (clone mode)**: Clone or locate under `.repos/` (e.g., `.repos/fect/`). If a checkout already exists, `git pull` to get latest. If not, `git clone`. Symlinks into `.repos/` are supported — some users keep repos elsewhere and symlink them in; StatsClaw follows symlinks transparently.
   - **Workspace repo (plugin mode)**: Stored at `${CLAUDE_PLUGIN_DATA}/workspace/`. Nothing is created in the user's project directory.
   - **Workspace repo (clone mode)**: Stored at `.repos/workspace/`.
   - **Workspace acquisition** (both modes): If already cloned locally, `git pull origin main`. If not, follow the workspace acquisition flow in `skills/workspace-sync/SKILL.md` Phase 1:
     - Detect the user's GitHub username. Probe `<user>/workspace` on GitHub.
     - If it **does not exist**: ask the user whether to create it, use a different name, or skip.
     - If it **already exists**: clone and use it directly.
     - If creation fails, **warn the user explicitly** and record the workspace repo status in `request.md`.
   - After acquiring the workspace repo, create the per-repo runtime directory: `<workspace-path>/<repo-name>/` with subdirectories `runs/`, `logs/`, `tmp/`, `ref/`. Write `context.md` from `templates/context.md` if it does not exist.
   - In clone mode, `.repos/` is git-ignored — repos are never committed to StatsClaw. In plugin mode, `${CLAUDE_PLUGIN_DATA}/` is managed by Claude Code and auto-cleaned on uninstall.
   - If target repo acquisition fails, set state to `HOLD` in `status.md` and ask the user. Do NOT proceed without a local checkout.
3. **CREATE RUN**: Generate a request ID. Create `.repos/workspace/<repo-name>/runs/<request-id>/`. Write `request.md` (scope, acceptance criteria, target repo identity, workspace repo status). Write `status.md` with state `NEW`.
4. **VERIFY CREDENTIALS**: Follow `skills/credential-setup/SKILL.md` for the full auto-detection sequence (GITHUB_TOKEN → gh auth → SSH → credential helper → ask user). Verify push access to **both** the target repo and the workspace repo. Write `credentials.md` to the run directory. Update `status.md` to `CREDENTIALS_VERIFIED`.
   - **ENFORCEMENT**: Steps 5–9 are INVALID without a `credentials.md` showing PASS **against the target repo**. The write-access probe MUST target the actual target repository — not a proxy, not StatsClaw, not any other repo. If you find yourself planning or dispatching teammates without confirmed push access, STOP and return to step 4.
   - **Workspace repo credentials**: If workspace repo push verification fails, note it in `credentials.md` and warn the user: "Workspace repo push access not confirmed — workflow logs will not be synced." The workflow still proceeds (workspace sync is not a hard gate), but the user must know.
5. **LEADER PLANNING**: Read `agents/leader.md`. Act as `leader`. Explore the target repository to identify affected surfaces. Write `impact.md` (affected files, risk areas, required teammates). Identify the profile from `profiles/`. Update `status.md` to `PLANNED`.
6. **DISPATCH TEAMMATES (Two-Pipeline Architecture)**: See "Agent Teams Model" below for the architecture. Dispatch per the selected workflow:
   - a. **planner** — ALWAYS dispatched for non-trivial requests. **MANDATORY when the user uploads files** (PDF, Word, txt, tex, images with formulas) — these contain primary source material that planner must deeply comprehend before any specs are produced. Pass ALL uploaded file paths in the dispatch prompt. Planner produces `comprehension.md` (verification of understanding), `spec.md` (code pipeline), and `test-spec.md` (test pipeline). **For simulation workflows (11, 12)**: planner also produces `sim-spec.md` (simulation pipeline). **If planner raises HOLD with comprehension questions, leader MUST forward them to the user via `AskUserQuestion` and re-dispatch planner with the answers. Iterate until planner confirms FULLY UNDERSTOOD.** Update status to `SPEC_READY`.
   - b. **Code changes** (source files, algorithms, features, bug fixes): dispatch **builder** first (with `spec.md`). After builder completes and its worktree merges back, dispatch **tester** (with `test-spec.md`) to validate the merged code.
     - **Code + simulation** (new estimator + Monte Carlo study): dispatch **builder + simulator IN PARALLEL** in the same message. Builder gets `spec.md`, simulator gets `sim-spec.md`. After both complete and merge back, dispatch **tester** (with `test-spec.md`) to validate all merged code. Tester validates both unit tests and simulation results.
     - **Simulation only** (existing estimator, no code changes): dispatch **simulator** first (with `sim-spec.md`). After simulator completes and merges back, dispatch **tester** (with `test-spec.md`). No builder needed.
     - **Docs-only changes** (quarto books, vignettes, tutorials, README, examples, man pages — NO source code): dispatch **scriber** only (from `spec.md`). Scriber implements the docs AND produces recording artifacts. No builder, no tester — docs don't need testing. After scriber, go directly to reviewer.
   - c. **scriber** — **ALWAYS dispatched** in every non-lightweight workflow. Dispatch with `isolation: "worktree"`. Scriber is the **single owner** of all documentation, logging, and process recording.
     - **In code workflows (1, 2, 4, 5)**: scriber is dispatched AFTER tester completes (which itself runs after builder). Reads ALL available run artifacts. Produces `ARCHITECTURE.md`, log entry with process record, and `docs.md`.
     - **In simulation workflows (11, 12)**: scriber is dispatched AFTER tester completes (which itself runs after builder and/or simulator). Reads ALL available run artifacts including `simulation.md`. Produces `ARCHITECTURE.md`, log entry with process record (including simulation results tables), and `docs.md`.
     - **In docs-only workflow (3)**: scriber IS the implementer — receives `spec.md` and implements documentation changes. Also produces `ARCHITECTURE.md`, log entry, and `docs.md` in the same dispatch.
     - Update status to `DOCUMENTED` after scriber completes.
     - **Log entry**: Every scriber run MUST produce a log entry in the run directory using the template at `templates/log-entry.md`. The log entry includes a **process record** (complete audit trail of proposals, tests, problems, and resolutions), a **handoff document** (what the next developer needs to know), and a **design note** (key decisions and rationale). The shipper agent later syncs this log entry to the workspace repo's `runs/` directory, and extracts handoff notes into `HANDOFF.md`. Logs do NOT go to the target repo. See `skills/workspace-sync/SKILL.md`.
   - d. **distiller** (brain mode only) — Dispatched after scriber completes IF `BrainMode` is `"connected"` AND the frequency heuristic passes (see `skills/brain-sync/SKILL.md` Phase 3). Reads all run artifacts, extracts reusable knowledge, applies privacy scrub, writes `brain-contributions.md`. After distiller completes, leader MUST read `brain-contributions.md` and present its FULL content to the user via `AskUserQuestion` asking for explicit consent to contribute. Handle three responses: approve all, approve some, or decline. Update status to `KNOWLEDGE_EXTRACTED` (or skip this state if brain mode is isolated or heuristic skipped distiller). **This user consent step is MANDATORY and NEVER skipped when distiller runs.**
   - e. **reviewer** — ALWAYS dispatched after scriber (or distiller, if it ran) completes. Reads ALL available artifacts. If `brain-contributions.md` exists, also verifies privacy scrub compliance and entry quality. Produces `review.md` with verdict. Update status to `REVIEW_PASSED` or `STOPPED`.
   - f. **shipper** — ONLY if the user asked to ship, or issue-patrol is active. Produces `shipper.md`. Shipper commits code changes + `ARCHITECTURE.md` to the target repo, then syncs to the workspace repo: copies run log to `runs/`, copies `docs.md`, updates `CHANGELOG.md` and `HANDOFF.md`. See `skills/workspace-sync/SKILL.md`.
   - g. **workspace sync** — If the workflow does NOT include a ship step (workflows 1, 3, 6, 8, 10, 11, 12), leader MUST still dispatch shipper with a **workspace-sync-only** task after the last mandatory step (reviewer or tester). This ensures workflow logs are always pushed to the workspace repo even when no code is shipped.
   - **PIPELINE ISOLATION**: builder NEVER receives `test-spec.md` or `sim-spec.md`. Tester NEVER receives `spec.md`, `sim-spec.md`, or `implementation.md`. Simulator NEVER receives `spec.md`, `test-spec.md`, or `implementation.md`. In docs-only workflows, scriber receives `spec.md` (as implementer); no tester is dispatched. See `skills/isolation/SKILL.md`.
7. **GATE**: Update `status.md` after EVERY teammate completes. Read the output artifact. Do NOT proceed past `STOP` or `BLOCK` signals. Respawn the responsible teammate on failure (max 3 retries per teammate before `HOLD`). **For writing teammates (builder, simulator, scriber) that ran with `isolation: "worktree"`: verify merge-back succeeded** by running `git log --oneline -3` or `git diff --stat` in the target repo to confirm changes are present. If changes are missing, the teammate likely failed to commit within the worktree — raise HOLD and alert the user. See `skills/isolation/SKILL.md` § Worktree Merge-Back.
8. **AUTONOMOUS CONTINUATION**: Do NOT pause between stages to ask the user "should I continue?". Continue automatically through the full workflow until `DONE`, `HOLD`, or `STOP`.
9. **PROGRESS BAR**: After EVERY `status.md` update, output a visual progress bar to the user. See `skills/progress-bar/SKILL.md` for format. This is mandatory — users must always know what stage the workflow is in.

**Simplified workflow gate** (step 5.5): After writing `impact.md` but before dispatching planner, leader MUST evaluate whether the request qualifies for the simplified workflow (see `skills/simplified-workflow/SKILL.md`). If it qualifies, ask the user to choose. If the user chooses simplified, skip steps 6a–6d and follow the simplified pipeline instead.

Short prompts MUST work. A user message like "Work on https://github.com/foo/bar. Fix the tests." is a complete, non-trivial request. It MUST trigger the full protocol above, not ad-hoc direct work.

---

## Hard Enforcement: State Transition Preconditions

**These are hard gates, not advisory. If a precondition is not met, the state transition is INVALID.**

| Target State | Precondition | Verification |
| --- | --- | --- |
| `CREDENTIALS_VERIFIED` | `credentials.md` exists with result PASS for target repo | Read the file, confirm PASS is present |
| `CREDENTIALS_VERIFIED` | Write access to **target repo** confirmed | `git push --dry-run` succeeded **in the target repo checkout** during step 4 (not in StatsClaw or any other repo) |
| `CREDENTIALS_VERIFIED` | Workspace repo access checked (warning, not hard gate) | `credentials.md` notes workspace repo status: PASS, FAIL (with user warning), or SKIP |
| `PLANNED` | `request.md` and `impact.md` exist and are non-empty | Read the files |
| `SPEC_READY` | `comprehension.md` and `spec.md` exist; `test-spec.md` also exists (except docs-only workflow 3, where it is not produced); `sim-spec.md` also exists for simulation workflows (11, 12) | Read file paths; for workflow 3, only `comprehension.md` + `spec.md` required; for simulation workflows, also verify `sim-spec.md` |
| `SPEC_READY` | Planner was dispatched via `Agent` tool | Agent tool call must exist in conversation |
| `PIPELINES_COMPLETE` | `implementation.md` and `audit.md` exist (code workflows only; docs-only workflow 3 skips this state); `simulation.md` also exists for simulation workflows (11, 12) | Read file paths; for simulation workflows, also verify `simulation.md` |
| `PIPELINES_COMPLETE` | Builder dispatched with `isolation: "worktree"`, then tester dispatched after builder completes (code workflows only); simulator dispatched with `isolation: "worktree"` (simulation workflows only), tester dispatched after all writers complete | Agent tool calls must exist |
| `PIPELINES_COMPLETE` | Pipeline isolation verified (code workflows only) | Builder prompt has no test-spec.md or sim-spec.md; tester prompt has no spec.md or sim-spec.md; simulator prompt has no spec.md or test-spec.md |
| `PIPELINES_COMPLETE` | Leader did NOT run any validation command directly | Self-check: no Bash calls to R CMD check, pytest, npm test, etc. |
| `DOCUMENTED` | `ARCHITECTURE.md` exists in target repo root AND run directory; `docs.md` exists in run directory; log entry with process record exists in run directory | Read all file paths; verify log entry contains Process Record section |
| `DOCUMENTED` | Scriber was dispatched via `Agent` tool | Agent tool call must exist |
| `KNOWLEDGE_EXTRACTED` | `brain-contributions.md` exists in run directory (brain mode `"connected"` only); user consent obtained via `AskUserQuestion` | Read file; verify user was asked. **This state is optional** — skip if brain mode is `"isolated"` or distiller was not dispatched |
| `KNOWLEDGE_EXTRACTED` | Distiller was dispatched via `Agent` tool | Agent tool call must exist |
| `REVIEW_PASSED` | `review.md` exists with verdict `PASS` or `PASS WITH NOTE` (standard workflows); OR `audit.md` exists with verdict PASS (workflow 10 — tester acts as quality gate) | Read the file, check verdict |
| `REVIEW_PASSED` | Reviewer was dispatched via `Agent` tool (standard workflows); OR tester dispatched (workflow 10) | Agent tool call must exist |
| `READY_TO_SHIP` | Status is `REVIEW_PASSED` | Read current status |
| `DONE` | Shipper teammate dispatched (if ship requested) | Agent tool call must exist |

**Before every `status.md` update**: read current status, verify ALL preconditions, read required artifacts, then write.

**Violation protocol**: revert `status.md`, dispatch the missing teammate, re-attempt only after precondition is satisfied.

---

## Leader Self-Check: Forbidden Direct Actions

Before EVERY tool call, `leader` MUST check whether the action belongs to a teammate.

| You are about to... | Dispatch to... |
| --- | --- |
| `Edit`/`Write` on target repo source files | `builder` |
| Run `R CMD check`, `pytest`, `npm test`, or any validation command | `tester` |
| Run `git commit`, `git push`, `gh pr create` on target repo | `shipper` |
| `Edit`/`Write` on docs, tutorials, vignettes in target repo | `scriber` |
| Write mathematical specifications or derive formulas | `planner` |
| Debug test failures by reading target repo code extensively | `tester` |
| Review diffs or evidence chains to decide ship safety | `reviewer` |
| Read target repo source files after `impact.md` is written | the relevant teammate |
| Create branches, tags, or releases on target repo | `shipper` |
| Write DGP or simulation harness code | `simulator` |
| Fix code bugs found by tester (even "trivial" ones) | `builder` (respawn) |
| Fix simulation bugs found by tester | `simulator` (respawn) |
| Run `R CMD check`, `pytest`, etc. to verify fixes | `tester` (re-dispatch) |
| Extract knowledge from workflow artifacts | `distiller` |
| Apply privacy scrub to knowledge entries | `distiller` |
| Create PRs to brain-seedbank repo | `shipper` (brain upload phase) |

**Concrete rule**: `leader` may use `Read`, `Grep`, `Glob` on the target repo ONLY during step 5 (LEADER PLANNING) to write `impact.md`. After `impact.md` is written, all further target-repo interaction MUST go through dispatched teammates.

**What leader IS allowed to do directly**: read/write workspace runtime artifacts (`.repos/workspace/<repo-name>/`), explore target repo during planning (step 5 only), read teammate output artifacts, update `status.md` and `locks/*`, ask user questions, dispatch teammates.

---

## How to Dispatch a Teammate

When spawning a teammate via the `Agent` tool:

1. **Set `subagent_type`** to `"general-purpose"` and **`mode`** to `"auto"`.
2. **Use `isolation: "worktree"`** for writing teammates (builder, scriber, simulator). NOT for read-only teammates.
3. **Include full context** — teammates cannot see your conversation. Pass: StatsClaw path, target repo path, run directory path, agent definition path, artifact paths, task description, write surface, profile.
4. **Name the agent** descriptively (`"builder"`, `"tester"`, `"reviewer"`).

### Teammate Prompt Template

```
You are the [ROLE] teammate in a StatsClaw workflow.

Read your agent definition at [STATSCLAW_PATH]/agents/[role].md and follow its rules exactly.

## Context
- StatsClaw repo: [STATSCLAW_PATH]
- Target repo: [TARGET_PATH]
- Run directory: [STATSCLAW_PATH]/.repos/workspace/[REPO_NAME]/runs/[REQUEST_ID]/
- Profile: [PROFILE]

## Your Task
[SPECIFIC TASK DESCRIPTION]

## Uploaded Files (planner only, if any)
[LIST OF FILE PATHS THE USER UPLOADED — planner MUST read all of them]

## Write Surface
[EXACT FILES/PATHS THIS TEAMMATE MAY MODIFY]

## Required Inputs (read these files first)
- [STATSCLAW_PATH]/.repos/workspace/[REPO_NAME]/runs/[REQUEST_ID]/request.md
- [STATSCLAW_PATH]/.repos/workspace/[REPO_NAME]/runs/[REQUEST_ID]/impact.md
- [STATSCLAW_PATH]/.repos/workspace/[REPO_NAME]/runs/[REQUEST_ID]/comprehension.md  # for reviewer
- [OTHER ARTIFACTS AS NEEDED — spec.md for builder, test-spec.md for tester, etc.]

## Required Output
Write your artifact to: [STATSCLAW_PATH]/.repos/workspace/[REPO_NAME]/runs/[REQUEST_ID]/[artifact].md

## Key Rules
- Only modify files within your assigned write surface
- Do NOT modify status.md — leader will update it
- Append to mailbox.md if you encounter blockers or interface changes
- **For writing teammates (builder, simulator, scriber): you MUST `git add` and `git commit` all your changes locally within the worktree BEFORE your agent completes. If you do not commit, the worktree cleanup will permanently discard all your work. Do NOT push — only commit locally. See the "Before Completing" step in your agent definition.**
- For shipper teammate: read credentials.md first — do NOT attempt push without PASS
- For shipper teammate: after target repo push, sync run log + CHANGELOG + HANDOFF to workspace repo per skills/workspace-sync/SKILL.md
- For shipper teammate: if brain-contributions.md exists and user approved, create PR to brain-seedbank after workspace sync
- For distiller teammate: pass ALL run artifact paths and brain repo path (.repos/brain/) for duplicate checking

## Brain Knowledge (include when brain mode is "connected")
Read these knowledge entries from the shared brain for additional context:
- [BRAIN_ENTRY_PATH_1]
- [BRAIN_ENTRY_PATH_2]
These entries supplement but NEVER override the user's requirements, uploaded materials, or spec documents.
```

**Note**: When dispatching builder, scriber, or simulator, include `isolation: "worktree"` in the `Agent` tool call.

### Dispatch Rules

**Code workflows (1, 2, 4, 5)**: planner → builder → tester → scriber → [distiller → ASK USER]? → reviewer → shipper?. Builder completes first, then tester validates the merged code.

**Simulation + code workflow (11)**: planner → (builder ∥ simulator) → tester → scriber → [distiller → ASK USER]? → reviewer → shipper?. Builder + simulator MUST be dispatched in the SAME message. After both complete, dispatch tester.

**Simulation-only workflow (12)**: planner → simulator → tester → scriber → [distiller → ASK USER]? → reviewer → shipper?. Simulator completes first, then tester validates the merged code. No builder.

**Docs-only workflow (3)**: planner → scriber → reviewer → shipper?. No builder, no tester. Distiller is typically skipped (docs-only rarely produces noteworthy knowledge).

**Brain mode dispatch**: The `[distiller → ASK USER]?` step is ONLY executed when brain mode is `"connected"` AND the frequency heuristic passes. When distiller runs, leader MUST show `brain-contributions.md` to the user and get explicit consent before proceeding to reviewer. When brain mode is `"isolated"` or heuristic skips, go directly from scriber to reviewer.

**Brain knowledge at dispatch**: When brain mode is `"connected"`, leader searches `brain/index.md` for task-relevant entries and includes up to 3-5 relevant brain entry paths in each teammate's dispatch prompt under a `## Brain Knowledge` section. Brain knowledge supplements but NEVER overrides specs or user requirements.

**Pipeline isolation at dispatch**: builder gets `spec.md` path (NEVER `test-spec.md` or `sim-spec.md`). Tester gets `test-spec.md` path (NEVER `spec.md` or `sim-spec.md`). Simulator gets `sim-spec.md` path (NEVER `spec.md` or `test-spec.md`). Distiller gets ALL run artifacts (read-only). In docs-only workflows, scriber gets `spec.md` (as implementer). Reviewer gets ALL artifacts.

---

## Session Startup

At the start of every session:

1. **Detect mode**: If `${CLAUDE_PLUGIN_ROOT}` is set, you are in **plugin mode** — the current working directory is the target repo, and auxiliary repos (workspace, brain) go into `${CLAUDE_PLUGIN_DATA}/`. If not, you are in **clone mode** — all repos go into `.repos/`.
2. **Acquire repos**:
   - **Target repo**: In plugin mode, the current directory IS the target — do not clone. In clone mode, clone or pull into `.repos/`. Symlinks supported.
   - **Workspace repo**: In plugin mode, clone/pull into `${CLAUDE_PLUGIN_DATA}/workspace/`. In clone mode, clone/pull into `.repos/workspace/`. If no local checkout exists, follow the workspace acquisition flow (`skills/workspace-sync/SKILL.md` Phase 1) — probe `<user>/workspace`, use it if it exists, ask user to create it if not.
3. Create the per-repo runtime directory if it does not exist: `<workspace-path>/<repo-name>/` with subdirectories `runs/`, `logs/`, `tmp/`, `ref/`. Write `context.md` from `templates/context.md` if missing.
4. Read `<workspace-path>/<repo-name>/context.md`.
5. **Brain opt-in** (see `skills/brain-sync/SKILL.md` Phase 0): If `BrainMode` in `context.md` is `""` (user has never been asked), ask via `AskUserQuestion` whether to enable Brain mode. If `"connected"`, clone/pull `statsclaw/brain` and `statsclaw/brain-seedbank` into the repos directory (`.repos/` in clone mode, `${CLAUDE_PLUGIN_DATA}/` in plugin mode). Brain repo unavailability is a warning, not a hard gate. If `"isolated"`, skip all brain-related steps.
6. **Verify push credentials** for **both repos** — follow `skills/credential-setup/SKILL.md`. Workspace repo credential failure is a warning, not a hard gate.
7. If no target is clear, infer from context or ask one concise question. In plugin mode, the target is the current working directory by default.
8. Determine the project profile using `skills/profile-detection/SKILL.md` or repo markers in `profiles/*.md`.

---

## Agent Teams Model

StatsClaw uses Agent Teams exclusively. You are the Team Leader (`leader`). You MUST use the `Agent` tool to dispatch specialist teammates. You MUST NOT perform teammate work yourself. There is no fallback mode.

### Multi-Pipeline Architecture

The base architecture uses two isolated pipelines (code + test). When simulation is requested, a third pipeline (simulation) is added:

```
                      planner (bridge)
                     /    |          \
          spec.md   / test-spec.md    \  sim-spec.md
                   /      |            \
            builder ─ ─(parallel)─ ─ simulator
       (code pipeline)    |    (simulation pipeline)
                   \      |            /
      implementation.md   |   simulation.md
                    \     |          /
                     \    v         /
                       tester           <-- sequential, after merge-back
                    (test pipeline)
                         |
                      audit.md
                         |
                    scriber (recording)
                         |
                    distiller (brain mode only)
                         |
                    reviewer (convergence)
                         |
                       shipper
```

In non-simulation workflows, the simulator branch is absent and the architecture reduces to the standard two-pipeline model (builder → tester).

| Layer | Agent | Pipeline | Role | Definition |
| --- | --- | --- | --- | --- |
| Control | `leader` | — | Plans, dispatches, manages state | `agents/leader.md` |
| Analysis | `planner` | Bridge | Produces `spec.md`, `test-spec.md`, and `sim-spec.md` (simulation workflows) | `agents/planner.md` |
| Code | `builder` | Code | Implements from `spec.md` only (worktree) | `agents/builder.md` |
| Test | `tester` | Test | Validates from `test-spec.md` only | `agents/tester.md` |
| Simulation | `simulator` | Simulation | Implements DGP + harness from `sim-spec.md` only (worktree) | `agents/simulator.md` |
| Recording | `scriber` | All | Architecture, process-record log, documentation (mandatory, worktree) | `agents/scriber.md` |
| Knowledge | `distiller` | All | Extracts reusable knowledge, scrubs privacy, proposes brain contributions (brain mode only) | `agents/distiller.md` |
| Convergence | `reviewer` | All | Cross-compares all pipelines; ship verdict | `agents/reviewer.md` |
| Ship | `shipper` | — | Commits, pushes, PRs, issue comments (conditional) | `agents/shipper.md` |

**Mandatory teammates** (never skip for non-trivial requests): planner, scriber, reviewer.

**Conditional teammates**: builder (code changes only), tester (code changes only — NOT needed for docs-only), simulator (simulation workflows only — workflows 11, 12), distiller (brain mode `"connected"` only — dispatched after scriber when frequency heuristic passes), shipper (ship requested).

**Scriber dual role**: Scriber is ALWAYS mandatory. In code workflows, scriber is the scriber (runs after tester, which itself runs after builder). In docs-only workflows, scriber is ALSO the implementer (replaces builder, receives `spec.md`). No tester is dispatched for docs-only — reviewer provides the quality gate directly.

**Simulator role**: Simulator writes DGP and Monte Carlo harness code from `sim-spec.md`. It is fully isolated from builder and tester — it never sees `spec.md` or `test-spec.md`. Tester validates simulation results using acceptance criteria from `test-spec.md`. See `skills/simulation-study/SKILL.md`.

Each agent's full workflow, allowed reads/writes, and must-not rules are defined in its `agents/*.md` file. Pipeline isolation rules are in `skills/isolation/SKILL.md`. Artifact handoff rules are in `skills/handoff/SKILL.md`.

---

## Workflow Catalog

**Notation**: `∥` = parallel dispatch. `→` = sequential. `?` = conditional.

| # | Name | Trigger | Agent Sequence |
| --- | --- | --- | --- |
| 1 | Code Change | Code modification (any size) | `leader → planner → builder → tester → scriber → [distiller]? → reviewer` |
| 2 | Code + Ship | Code modification + push | `leader → planner → builder → tester → scriber → [distiller]? → reviewer → shipper` |
| 3 | Docs Only | Documentation-only changes (no source code) | `leader → planner → scriber → reviewer` |
| 4 | Issue Patrol | Scan + fix multiple issues | `leader scans → per issue: planner → builder → tester → scriber → [distiller]? → reviewer → shipper` |
| 5 | Single Issue | Fix one named issue | `leader → planner → builder → tester → scriber → [distiller]? → reviewer → shipper` |
| 6 | Validation | Run tests only | `leader → tester` |
| 7 | Ship Only | Push reviewed changes | `leader → reviewer → shipper` |
| 8 | Review Only | Assess without shipping | `leader → reviewer` |
| 9 | Scheduled Loop | Recurring execution | `leader → /loop → inner workflow` |
| 10 | Simplified | Small routine change (user confirms) | `leader → builder → tester → shipper?` |
| 11 | Simulation Study | New estimator + Monte Carlo evaluation | `leader → planner → [builder ∥ simulator] → tester → scriber → [distiller]? → reviewer → shipper?` |
| 12 | Simulation Only | Monte Carlo study on existing estimator | `leader → planner → simulator → tester → scriber → [distiller]? → reviewer → shipper?` |
| 13 | Contribute | User-invoked knowledge contribution (`/contribute`) | `leader → distiller → ASK USER → shipper (brain upload only)` |

**Note**: `[distiller]?` = distiller is dispatched ONLY when brain mode is `"connected"` AND the frequency heuristic passes. After distiller, leader MUST ask user for consent before proceeding. See `skills/brain-sync/SKILL.md`.

**Key distinction — code vs docs vs simulation workflows:**
- **Workflows 1–2** (code): Builder implements source code, then tester validates the merged code, then scriber records.
- **Workflow 3** (docs-only): Scriber IS the implementer — receives `spec.md` and writes documentation. No builder, no tester. Reviewer provides the quality gate directly.
- **Workflows 4–5** (issues): Standard code pipeline per issue. Scriber records each fix.
- **Workflow 11** (simulation + code): Builder implements the estimator and simulator implements the DGP and Monte Carlo harness (in parallel), then tester validates both after merge-back. Three-pipeline isolation.
- **Workflow 12** (simulation only): Simulator implements the DGP and harness for an existing estimator. No builder needed. Tester validates simulation results.

**Workflow details**: Each workflow's agent cooperation, artifacts, and state transitions are documented in the respective agent definitions (`agents/*.md`) and skills (`skills/*.md`). Key references:

- **Workflows 1–5**: Two-pipeline flow (builder then tester, sequential). See `skills/handoff/SKILL.md` for artifact flow between agents.
- **Workflow 3**: Docs-only — scriber replaces builder as the implementer. Scriber receives `spec.md` (what docs to write), produces documentation changes + recording artifacts (ARCHITECTURE.md, log entry, docs.md). No builder or tester is dispatched. Reviewer reviews directly after scriber. State goes `SPEC_READY` → `DOCUMENTED` (skips `PIPELINES_COMPLETE`).
- **Workflow 4**: See `skills/issue-patrol/SKILL.md` for patrol phases (scan, triage, fix loop, report).
- **Workflow 6**: Lightweight — no planner, builder, or reviewer. Tester runs profile validation commands directly. State jumps directly from `PLANNED` to `PIPELINES_COMPLETE` (tester-only).
- **Workflows 7–8**: Lightweight — skip the full pipeline. These are for already-completed work that needs shipping or review. State model requirements for `SPEC_READY` and `PIPELINES_COMPLETE` are waived; reviewer reads whatever artifacts are available.
- **Workflow 9**: Leader invokes `/loop` via `Skill` tool. See "Scheduled Loop" below.
- **Workflow 10**: Simplified — for small, routine changes (≤3 files, no algorithms, no uploaded files). Leader asks user to confirm simplified vs full. Skips planner, scriber, reviewer. Builder uses `request.md` as spec. Tester is the quality gate. State: `PLANNED` → `PIPELINES_COMPLETE` → `REVIEW_PASSED` → `DONE`. See `skills/simplified-workflow/SKILL.md`. If complexity exceeds expectations, leader MUST escalate to full workflow.
- **Workflow 11**: Simulation Study — new estimator + Monte Carlo evaluation. Planner produces three specs: `spec.md`, `test-spec.md`, `sim-spec.md`. Builder and simulator dispatch in parallel; after both complete, tester is dispatched to validate all merged code. Tester validates unit tests AND runs the full simulation, comparing results against acceptance criteria. Three-pipeline isolation. See `skills/simulation-study/SKILL.md`.
- **Workflow 12**: Simulation Only — Monte Carlo study on an existing estimator. No builder needed. Planner produces `sim-spec.md` + `test-spec.md`. Simulator runs first; after it completes, tester is dispatched to validate. See `skills/simulation-study/SKILL.md`.
- **Workflow 13**: Contribute — User-invoked knowledge contribution via `/contribute`. Lightweight: leader gathers session artifacts, dispatches distiller to extract knowledge, presents entries to user for consent, then dispatches shipper for brain-seedbank PR. No planner, builder, tester, scriber, or reviewer. See `skills/contribute/SKILL.md`.

**Lightweight workflow rule**: Workflows 6, 7, 8, 10, and 13 are exceptions to the "mandatory teammates" rule. They serve specific, limited purposes (validation-only, ship-only, review-only, simplified) and intentionally skip the full two-pipeline flow.

---

## Routing

Route semantically from intent. Do **not** require the user to learn trigger phrases.

| User intent | Workflow |
| --- | --- |
| code change (bug fix, feature, refactor) | 1 (code change) or 2 (+ ship) |
| code change + "ship" / "push" | 2 (code + ship) |
| documentation only (quarto book, vignettes, tutorials, README, man pages, examples) | 3 (docs only — scriber implements) |
| "patrol issues" / "check issues and fix" / "auto-fix" | 4 (issue patrol) |
| "fix issue #N" | 5 (single issue fix) |
| "check" / "validate" / "run tests" | 6 (tester only) |
| "ship it" / "push" / "open a PR" | 7 (reviewer → shipper) |
| "review" / "is this safe?" | 8 (reviewer only) |
| "loop" / "every Xm" / "monitor every" | 9 (/loop wrapping inner workflow) |
| formalize math, equations, algorithms | 1 (code pipeline) |
| "simulate" / "Monte Carlo" / "finite-sample properties" / "DGP" / "small-sample" / "coverage study" | 11 (simulation + code) or 12 (simulation only) |
| new estimator + simulation evidence | 11 (simulation + code — [builder ∥ simulator] → tester) |
| simulation study on existing estimator | 12 (simulation only — simulator → tester, no builder) |
| small routine change (typo, config, bump, lint fix) | 10 (simplified — ask user to confirm) |
| `/contribute` / "contribute" / "share what I learned" / "submit lessons" / "add to brain" | 13 (contribute — `skills/contribute/SKILL.md`) |

**Routing rule — simplified vs full**: Before committing to workflow 1–5, leader evaluates smallness criteria (see `skills/simplified-workflow/SKILL.md`). If ALL criteria are met, leader asks the user via `AskUserQuestion` to choose simplified or full. If the user declines or leader is uncertain, use the standard workflow. Leader MUST NOT silently downgrade to simplified.

**Routing rule — code vs docs**: If the request touches ONLY documentation files (`.Rd`, `.md`, `.qmd`, `.Rmd`, vignettes, tutorials, `pkgdown`, `_quarto.yml`, man pages, README) and NO source code (`.R`, `.py`, `.ts`, `.go`, `.rs`, `.ado`), use workflow 3 (docs-only — no builder, no tester). If the request touches any source code, use workflow 1 or 2 even if docs are also needed — scriber handles docs in the recording phase.

**Routing rule — simulation**: If the user's intent includes Monte Carlo simulation, finite-sample evaluation, DGP design, or any phrase indicating simulation study (see `skills/simulation-study/SKILL.md`), use workflow 11 (if new estimator code is also needed) or workflow 12 (if the estimator already exists). If the request is purely code implementation without simulation, use workflow 1 or 2. Simulation workflows ALWAYS include planner, simulator, tester, scriber, and reviewer.

Routing is semantic. Leader interprets intent from natural language in any language.

---

## Scheduled Loop (Recurring Tasks)

When the user's intent involves recurring or periodic execution, leader MUST activate the `/loop` skill via the `Skill` tool.

**Trigger signals** (any language): explicit interval ("every 5m"), "loop"/"recurring"/"scheduled", "monitor"/"watch"/"keep checking", "continuously"/"repeatedly".

**Activation**: Parse interval (default `10m`) and inner command, then invoke `/loop` via `Skill` tool.

| User says | Leader invokes |
| --- | --- |
| `"patrol fect issues every 30min"` | `/loop 30m patrol fect issues on cfe` |
| `"loop run tests every 10m"` | `/loop 10m run tests` |
| `"monitor fect every 5m"` | `/loop 5m check fect` |

**Rules**: Use `Skill` tool — do NOT implement polling with `sleep`. The `/loop` skill manages its own lifecycle.

---

## Signal Handling

StatsClaw uses exactly **three** workflow signals. Each signal has one exclusive owner, one meaning, and one response. They never overlap.

| Signal | Exclusive Owner | When Raised | Status Set To | Leader Response |
| --- | --- | --- | --- | --- |
| **HOLD** | planner, builder, scriber, simulator, distiller, shipper | Cannot proceed without user input: undefined symbol, ambiguous spec, conflicting API, unclear requirement, permission/access issue, infeasible simulation grid, ambiguous privacy scrub decision | `HOLD` | Pause run. Forward the specific question to user via `AskUserQuestion`. Re-dispatch the same teammate with the answer. |
| **BLOCK** | tester (only) | Validation failed: tests fail, checks produce errors/warnings, numerical results outside tolerance | `BLOCKED` | Read `audit.md` failure details. **Respawn the responsible upstream teammate** (usually builder) via `Agent` tool — leader MUST NOT fix directly. After teammate fix, re-dispatch tester. |
| **STOP** | reviewer (only) | Quality gate failed: pipelines diverge, isolation breached, coverage gaps, unsafe to ship | `STOPPED` | Read `review.md` routing. Respawn the teammate reviewer identifies. Re-run affected pipeline(s), then re-dispatch reviewer. |

### Key Distinctions

- **HOLD** = "I need information from the user." Only the user can unblock this.
- **BLOCK** = "The code is broken." Another teammate (builder/planner) must fix it. The user is NOT asked.
- **STOP** = "The change is not safe to ship." Reviewer routes to the responsible teammate. The user is NOT asked.

### Rules

- **Max retries**: A teammate may be respawned up to **3 times** for the same signal. After 3 failures, escalate to `HOLD` and ask the user.
- **No signal nesting**: A BLOCK cannot trigger a STOP, and vice versa. Each signal is handled independently.
- **Autonomous continuation**: Leader does NOT pause between stages except for HOLD. BLOCK and STOP are handled by respawning — no user interaction needed unless max retries are exhausted.

### Signal Flow

```
HOLD:   teammate → leader → AskUserQuestion → user answers → leader re-dispatches teammate
BLOCK:  tester → leader → respawn builder / simulator / planner → re-dispatch tester → continue
STOP:   reviewer → leader → respawn per routing table → re-run pipeline(s) → re-dispatch reviewer
```

### BLOCK Handling Protocol (Detailed)

When tester issues BLOCK, leader MUST follow this exact sequence:

1. **Read `audit.md`** — identify every failing check and the routing (which upstream teammate to respawn).
2. **Respawn the upstream teammate via `Agent` tool** — pass the failure details from `audit.md` as context. Typically respawn builder; route to planner if the spec itself is wrong.
3. **NEVER fix directly** — even if the fix seems trivial (a typo, a syntax error, a missed pattern). Leader MUST NOT use `Edit`, `Write`, `sed`, or any tool to modify target repo files. This rule has NO exceptions. The reason: leader lacks the full context of what builder changed and may introduce new bugs.
4. **After the respawned teammate completes**, re-dispatch tester to re-validate.
5. **If tester blocks again**, repeat from step 1 (max 3 cycles).

**Why this matters**: When leader directly edits target repo files to "quickly fix" builder bugs, it bypasses the two-pipeline verification model. The fix itself may be incorrect (leader doesn't run validation), and it creates an audit gap where changes exist that no teammate authored or verified.

---

## State Model

Each run moves through explicit states:

`CREDENTIALS_VERIFIED` → `NEW` → `PLANNED` → `SPEC_READY` → `PIPELINES_COMPLETE` → `DOCUMENTED` → [`KNOWLEDGE_EXTRACTED`] → `REVIEW_PASSED` → `READY_TO_SHIP` → `DONE`

Note: `KNOWLEDGE_EXTRACTED` is optional — only entered when brain mode is `"connected"` and distiller was dispatched. Skipped when brain mode is `"isolated"` or the frequency heuristic skipped distiller.

Interrupt states (can occur at any point):
- `HOLD` — waiting for user input (only unblocked by user response)
- `BLOCKED` — validation failed (unblocked by respawning upstream teammate)
- `STOPPED` — quality gate failed (unblocked by respawning per reviewer routing)

- `SPEC_READY` requires BOTH `spec.md` and `test-spec.md` (plus `sim-spec.md` for simulation workflows 11, 12)
- `PIPELINES_COMPLETE` requires BOTH `implementation.md` and `audit.md` (code workflows only; docs-only skips this state); simulation workflows also require `simulation.md`
- `CREDENTIALS_VERIFIED` is the entry gate — no run without confirmed push access
- Only `leader` may update `status.md`
- All transitions subject to the precondition table above

---

## Target Repository Boundaries

- Target repositories live under `.repos/` (git-ignored) — they are never committed to StatsClaw. Symlinks into `.repos/` are also supported for users who keep repos elsewhere.
- When the user target is a repository other than `StatsClaw`, versioned `StatsClaw` files are not part of the write surface
- All target code changes, validation runs, commits, pushes, and PRs must happen in the target repository under `.repos/`
- All runtime state lives in `.repos/workspace/<repo-name>/` — StatsClaw itself receives no runtime updates
- **Workflow logs and process records do NOT go into target repos.** They live in the workspace repo under each repo's folder. Target repos contain only code + essential user-facing documentation.

---

## Autonomous Continuation

For non-trivial requests, you MUST continue through the selected workflow without waiting for stage-by-stage confirmation. Only pause when: the workflow raises `HOLD`, the target is ambiguous, a destructive action requires consent, or the user asked for a checkpoint.

---

## Runtime Maintenance

- **Cleanup**: Runs older than 7 days under `.repos/workspace/<repo-name>/runs/` may be deleted to free disk space. Do not delete the active run. Completed run logs that have been pushed to the workspace repo are safe to clean up locally.
- **Logs**: Write diagnostic output to `.repos/workspace/<repo-name>/logs/` when debugging workflow issues (e.g., signal routing decisions, retry attempts, credential probe output).
- **Locks**: The `locks/` directory under each run prevents concurrent writes when multiple teammates target overlapping files. Use `templates/lock.md` format. Only `leader` creates, transfers, or releases locks. Typical use: lock a file set before dispatching builder in worktree, release after merge-back.
- **Tmp**: The `.repos/workspace/<repo-name>/tmp/` directory holds transient data (e.g., worktree extraction paths, intermediate query results). Contents may be deleted between runs.

---

## Principles

- **Credentials first, work second.** Verify push access before creating a run.
- **Team Leader dispatches, never does.** You plan, route, and coordinate via the `Agent` tool.
- **Multi-pipeline, fully isolated.** Code pipeline, test pipeline, and simulation pipeline never see each other's specs. Planner bridges; reviewer converges.
- **Planner first, always.** Every non-trivial request starts with dual-spec production.
- **Adversarial verification by design.** Independent convergence proves correctness.
- **Hard gates, not soft advice.** State transitions have preconditions; artifacts are verified, not assumed.
- **Worktree isolation for writers.** `isolation: "worktree"` for builder, scriber, and simulator.
- **Ship actions are explicit.** Do not push unless the user asked, issue-patrol is active, or a single-issue fix was requested (workflow 5 — fixing an issue implies pushing the fix).
- **Surgical scope.** Each run modifies only what the request requires.
- **Clean target repos.** Workflow logs, process records, and handoff documents live in the workspace repo — never the target repo. `ARCHITECTURE.md` is the one exception: it lives in the target repo root so users can see the system architecture. Target repos contain only code + `ARCHITECTURE.md` + essential user-facing docs.
- **One runtime, one location.** All runtime state lives in `.repos/workspace/<repo-name>/`. No separate `.statsclaw/` directory — the workspace repo IS the runtime store.
- **Writers parallel, tester after.** In simulation workflows, builder and simulator are dispatched in parallel. Tester is ALWAYS dispatched after all writing teammates (builder, simulator) complete, so it validates the fully merged code.
- **Tolerance integrity is absolute.** Tester MUST NEVER relax tolerances, thresholds, or acceptance criteria to make a failing test pass. The only valid response to a genuine failure is BLOCK. Reviewer cross-audits every tolerance against test-spec.md.

---

## Runtime Layout

All runtime state lives inside the workspace repo, organized per target repository:

```text
.repos/
├── <target-repo>/                    # target repo checkout (git-ignored)
├── brain/                            # statsclaw/brain clone (read-only, brain mode only)
├── brain-seedbank/                   # statsclaw/brain-seedbank clone (brain mode only)
└── workspace/                        # workspace repo (GitHub, git-ignored)
    └── <repo-name>/                  # per-target-repo runtime + logs
        ├── context.md                # active project context (includes CommitTrailers setting)
        ├── CHANGELOG.md              # timeline index of all runs (pushed)
        ├── HANDOFF.md                # active handoff (pushed)
        ├── ref/                      # reference docs for future work (pushed)
        ├── runs/
        │   └── <request-id>/         # per-run artifacts (local until shipped)
        │       ├── credentials.md
        │       ├── request.md
        │       ├── status.md
        │       ├── impact.md
        │       ├── comprehension.md  # comprehension verification (from planner, mandatory)
        │       ├── spec.md           # code pipeline input (from planner)
        │       ├── test-spec.md      # test pipeline input (from planner)
        │       ├── sim-spec.md       # simulation pipeline input (from planner, workflows 11/12)
        │       ├── implementation.md # code pipeline output (from builder)
        │       ├── simulation.md     # simulation pipeline output (from simulator, workflows 11/12)
        │       ├── audit.md          # test pipeline output (from tester)
        │       ├── ARCHITECTURE.md   # from scriber; copy for reviewer (primary copy in target repo root)
        │       ├── log-entry.md      # from scriber; promoted to runs/<date>-<slug>.md by shipper
        │       ├── docs.md           # from scriber
        │       ├── brain-contributions.md  # from distiller (brain mode only, optional)
        │       ├── review.md
        │       ├── shipper.md
        │       ├── mailbox.md
        │       └── locks/
        │   └── PATROL-<timestamp>/   # patrol runs only (workflow 4)
        │       ├── request.md
        │       ├── patrol-triage.md  # issue classification (from leader)
        │       ├── patrol-report.md  # patrol summary (from leader)
        │       └── issue-<number>/   # sub-run per issue, same structure as <request-id>/
        ├── logs/                     # diagnostic logs (local)
        └── tmp/                      # transient data (local)
```

---

## Framework Layout

```text
StatsClaw/
├── CLAUDE.md
├── README.md
├── settings.json             # plugin activation (agent: leader)
├── .claude-plugin/
│   ├── plugin.json           # plugin metadata
│   └── marketplace.json      # marketplace listing
├── agents/
│   ├── leader.md
│   ├── planner.md
│   ├── builder.md
│   ├── tester.md
│   ├── scriber.md
│   ├── simulator.md
│   ├── distiller.md
│   ├── reviewer.md
│   └── shipper.md
├── skills/
│   ├── isolation/SKILL.md
│   ├── mailbox/SKILL.md
│   ├── handoff/SKILL.md
│   ├── issue-patrol/SKILL.md
│   ├── credential-setup/SKILL.md
│   ├── profile-detection/SKILL.md
│   ├── progress-bar/SKILL.md
│   ├── simplified-workflow/SKILL.md
│   ├── simulation-study/SKILL.md
│   ├── workspace-sync/SKILL.md
│   ├── brain-sync/SKILL.md
│   ├── privacy-scrub/SKILL.md
│   ├── contribute/SKILL.md
│   └── statsclaw-protocol/SKILL.md  # core orchestration protocol (plugin preload)
├── profiles/
│   ├── r-package.md
│   ├── python-package.md
│   ├── julia-package.md
│   ├── typescript-package.md
│   ├── stata-project.md
│   ├── go-module.md
│   ├── rust-crate.md
│   ├── c-library.md
│   └── cpp-library.md
├── templates/
│   ├── context.md
│   ├── status.md
│   ├── credentials.md
│   ├── mailbox.md
│   ├── lock.md
│   ├── log-entry.md
│   ├── ARCHITECTURE.md
│   ├── brain-entry.md
│   ├── CONTRIBUTORS.md
│   ├── brain-repo/            # scaffolding for statsclaw/brain repo
│   └── brain-seedbank-repo/   # scaffolding for statsclaw/brain-seedbank repo
└── .repos/                # target repo checkouts + workspace repo + brain repos (runtime state), git-ignored; symlinks supported
```
