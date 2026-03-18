# StatsClaw — Agent Teams Framework for Claude Code

StatsClaw is a reusable workflow framework for building, validating, documenting, reviewing, and externalizing code changes with Claude Code across multiple languages. The repository contains the framework only: orchestration rules, agent definitions, templates, profiles, and docs.

StatsClaw does **not** version user runtime state. All request state, project contexts, generated specs, shared task lists, mailboxes, locks, and run artifacts live under a local `.statsclaw/` directory that is ignored by git by default.

**Workflow logs go to Brain, not the target repo.** All workflow-generated logs, process records, and architecture diagrams are pushed to a centralized `[username]/statsclaw-brain` GitHub repository — NOT to the target repo. This keeps target repos clean (code + essential user-facing docs only). See `skills/brain-sync/SKILL.md` for details.

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

### How It Works

1. Leader reads the prompt and detects intent (see `.agents/leader.md` → Simple Prompt Routing)
2. Leader resolves package names to repos (e.g., `fect` → `xuyiqing/fect` via `packages/fect.md`)
3. Leader auto-detects credentials (see `skills/credential-setup/SKILL.md`) — no manual PAT setup needed if the environment is configured
4. Leader activates the appropriate skill or workflow
5. Everything runs autonomously — user gets results, not questions

---

## Mandatory Execution Protocol

This section is the entry point for every non-trivial user request. You MUST follow these steps in order. You MUST NOT skip steps. You MUST NOT do the user's work directly without completing this protocol. If you find yourself doing substantive analysis, implementation, or review work without having created `request.md` and `impact.md` first, STOP immediately and restart from step 3.

**CRITICAL: You are the Team Leader (`leader`). You MUST use the `Agent` tool to dispatch every teammate. You MUST NOT perform teammate work yourself. If you catch yourself doing builder, tester, recorder, reviewer, planner, or shipper work directly, STOP and dispatch it to an agent instead.**

1. **SETUP**: Read `.statsclaw/CONTEXT.md`. If it does not exist, create the full local runtime first (see Session Startup below). Read the active package context.
2. **ACQUIRE REPOS**: Acquire BOTH the target repo AND the brain repo upfront. Both must be local before any work begins.
   - **Target repo**: Clone or locate under `.repos/` (e.g., `.repos/fect/`). If a checkout already exists, `git pull` to get latest. If not, `git clone`. Symlinks into `.repos/` are supported — some users keep repos elsewhere and symlink them in; StatsClaw follows symlinks transparently.
   - **Brain repo**: Clone or locate `.repos/statsclaw-brain`. Determine the owner from the target repo's remote URL. If `.repos/statsclaw-brain` already exists, `git pull origin main`. If not, try `git clone`. If the brain repo does not exist on GitHub, **auto-create it** using `gh repo create [owner]/statsclaw-brain --public`. If creation fails (e.g., insufficient permissions), **warn the user explicitly**: "Cannot create [owner]/statsclaw-brain — workflow logs will not be recorded. Please create this repository manually or grant repo creation permissions." Record the brain repo status in `request.md`. See `skills/brain-sync/SKILL.md`.
   - The `.repos/` directory is git-ignored — repos are never committed to StatsClaw.
   - If target repo acquisition fails, set state to `HOLD` in `status.md` and ask the user. Do NOT proceed without a local checkout.
3. **CREATE RUN**: Generate a request ID. Create `.statsclaw/runs/<request-id>/`. Write `request.md` (scope, acceptance criteria, target repo identity, brain repo status). Write `status.md` with state `NEW`.
4. **VERIFY CREDENTIALS**: Follow `skills/credential-setup/SKILL.md` for the full auto-detection sequence (GITHUB_TOKEN → gh auth → SSH → credential helper → ask user). Verify push access to **both** the target repo and the brain repo. Write `credentials.md` to the run directory. Update `status.md` to `CREDENTIALS_VERIFIED`.
   - **ENFORCEMENT**: Steps 5–9 are INVALID without a `credentials.md` showing PASS **against the target repo**. The write-access probe MUST target the actual target repository — not a proxy, not StatsClaw, not any other repo. If you find yourself planning or dispatching teammates without confirmed push access, STOP and return to step 4.
   - **Brain repo credentials**: If brain repo push verification fails, note it in `credentials.md` and warn the user: "Brain repo push access not confirmed — workflow logs will not be synced." The workflow still proceeds (brain sync is not a hard gate), but the user must know.
5. **LEADER PLANNING**: Read `.agents/leader.md`. Act as `leader`. Explore the target repository to identify affected surfaces. Write `impact.md` (affected files, risk areas, required teammates). Identify the profile from `profiles/`. Update `status.md` to `PLANNED`.
6. **DISPATCH TEAMMATES (Two-Pipeline Architecture)**: See "Agent Teams Model" below for the architecture. Dispatch per the selected workflow:
   - a. **planner** — ALWAYS dispatched for non-trivial requests. **MANDATORY when the user uploads files** (PDF, Word, txt, tex, images with formulas) — these contain primary source material that planner must deeply comprehend before any specs are produced. Pass ALL uploaded file paths in the dispatch prompt. Planner produces `comprehension.md` (verification of understanding), `spec.md` (code pipeline), and `test-spec.md` (test pipeline). **If planner raises HOLD with comprehension questions, leader MUST forward them to the user via `AskUserQuestion` and re-dispatch planner with the answers. Iterate until planner confirms FULLY UNDERSTOOD.** Update status to `SPEC_READY`.
   - b. **Code changes** (source files, algorithms, features, bug fixes): dispatch **builder + tester IN PARALLEL** in the same message. Builder gets `spec.md` only. Tester gets `test-spec.md` only.
     - **Docs-only changes** (quarto books, vignettes, tutorials, README, examples, man pages — NO source code): dispatch **recorder** only (from `spec.md`). Recorder implements the docs AND produces recording artifacts. No builder, no tester — docs don't need testing. After recorder, go directly to reviewer.
   - c. **recorder** — **ALWAYS dispatched** in every non-lightweight workflow. Dispatch with `isolation: "worktree"`. Recorder is the **single owner** of all documentation, logging, and process recording.
     - **In code workflows (1, 2, 4, 5)**: recorder is dispatched AFTER both builder and tester complete. Reads ALL available run artifacts. Produces `architecture.md`, log entry with process record, and `docs.md`.
     - **In docs-only workflow (3)**: recorder IS the implementer — receives `spec.md` and implements documentation changes. Also produces `architecture.md`, log entry, and `docs.md` in the same dispatch.
     - Update status to `DOCUMENTED` after recorder completes.
     - **Log entry**: Every recorder run MUST produce a log entry in the run directory using the template at `templates/log-entry.md`. The log entry includes a **process record** (complete audit trail of proposals, tests, problems, and resolutions), a **handoff document** (what the next developer needs to know), and a **design note** (key decisions and rationale). The shipper agent later syncs this log entry to the brain repo (`[owner]/statsclaw-brain`) — logs do NOT go to the target repo. See `skills/brain-sync/SKILL.md`.
   - d. **reviewer** — ALWAYS dispatched after recorder completes. Reads ALL available artifacts. Produces `review.md` with verdict. Update status to `REVIEW_PASSED` or `STOPPED`.
   - e. **shipper** — ONLY if the user asked to ship, or issue-patrol is active. Produces `shipper.md`. Shipper commits code changes to the target repo (clean — no logs or architecture.md), then syncs workflow artifacts (architecture.md, log entry) to the brain repo (`[owner]/statsclaw-brain`). See `skills/brain-sync/SKILL.md`.
   - f. **brain sync** — If the workflow does NOT include a ship step (workflows 1, 3, 6, 8, 10), leader MUST still dispatch shipper with a **brain-sync-only** task after the last mandatory step (reviewer or tester). This ensures workflow logs are always pushed to the brain repo even when no code is shipped.
   - **PIPELINE ISOLATION**: builder NEVER receives `test-spec.md`. Tester NEVER receives `spec.md` or `implementation.md`. In docs-only workflows, recorder receives `spec.md` (as implementer); no tester is dispatched. See `skills/isolation/SKILL.md`.
7. **GATE**: Update `status.md` after EVERY teammate completes. Read the output artifact. Do NOT proceed past `STOP` or `BLOCK` signals. Respawn the responsible teammate on failure (max 3 retries per teammate before `HOLD`).
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
| `CREDENTIALS_VERIFIED` | Brain repo access checked (warning, not hard gate) | `credentials.md` notes brain repo status: PASS, FAIL (with user warning), or SKIP |
| `PLANNED` | `request.md` and `impact.md` exist and are non-empty | Read the files |
| `SPEC_READY` | `comprehension.md` and `spec.md` exist; `test-spec.md` also exists (except docs-only workflow 3, where it is not produced) | Read file paths; for workflow 3, only `comprehension.md` + `spec.md` required |
| `SPEC_READY` | Planner was dispatched via `Agent` tool | Agent tool call must exist in conversation |
| `PIPELINES_COMPLETE` | `implementation.md` and `audit.md` exist (code workflows only; docs-only workflow 3 skips this state) | Read both file paths |
| `PIPELINES_COMPLETE` | Builder dispatched with `isolation: "worktree"`, tester dispatched (code workflows only) | Agent tool calls must exist |
| `PIPELINES_COMPLETE` | Pipeline isolation verified (code workflows only) | Builder prompt has no test-spec.md; tester prompt has no spec.md |
| `PIPELINES_COMPLETE` | Leader did NOT run any validation command directly | Self-check: no Bash calls to R CMD check, pytest, npm test, etc. |
| `DOCUMENTED` | `architecture.md` exists in run directory; `docs.md` exists in run directory; log entry with process record exists in run directory | Read all file paths; verify log entry contains Process Record section |
| `DOCUMENTED` | Recorder was dispatched via `Agent` tool | Agent tool call must exist |
| `REVIEW_PASSED` | `review.md` exists with verdict `PASS` or `PASS WITH NOTE` | Read the file, check verdict |
| `REVIEW_PASSED` | Reviewer was dispatched via `Agent` tool | Agent tool call must exist |
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
| `Edit`/`Write` on docs, tutorials, vignettes in target repo | `recorder` |
| Write mathematical specifications or derive formulas | `planner` |
| Debug test failures by reading target repo code extensively | `tester` |
| Review diffs or evidence chains to decide ship safety | `reviewer` |
| Read target repo source files after `impact.md` is written | the relevant teammate |
| Create branches, tags, or releases on target repo | `shipper` |
| Fix code bugs found by tester (even "trivial" ones) | `builder` (respawn) |
| Run `R CMD check`, `pytest`, etc. to verify fixes | `tester` (re-dispatch) |

**Concrete rule**: `leader` may use `Read`, `Grep`, `Glob` on the target repo ONLY during step 5 (LEADER PLANNING) to write `impact.md`. After `impact.md` is written, all further target-repo interaction MUST go through dispatched teammates.

**What leader IS allowed to do directly**: read/write `.statsclaw/` runtime artifacts, explore target repo during planning (step 5 only), read teammate output artifacts, update `status.md` and `locks/*`, ask user questions, dispatch teammates.

---

## How to Dispatch a Teammate

When spawning a teammate via the `Agent` tool:

1. **Set `subagent_type`** to `"general-purpose"` and **`mode`** to `"auto"`.
2. **Use `isolation: "worktree"`** for writing teammates (builder, recorder). NOT for read-only teammates.
3. **Include full context** — teammates cannot see your conversation. Pass: StatsClaw path, target repo path, run directory path, agent definition path, artifact paths, task description, write surface, profile.
4. **Name the agent** descriptively (`"builder"`, `"tester"`, `"reviewer"`).

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

## Uploaded Files (planner only, if any)
[LIST OF FILE PATHS THE USER UPLOADED — planner MUST read all of them]

## Write Surface
[EXACT FILES/PATHS THIS TEAMMATE MAY MODIFY]

## Required Inputs (read these files first)
- [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/request.md
- [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/impact.md
- [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/comprehension.md  # for reviewer
- [OTHER ARTIFACTS AS NEEDED — spec.md for builder, test-spec.md for tester, etc.]

## Required Output
Write your artifact to: [STATSCLAW_PATH]/.statsclaw/runs/[REQUEST_ID]/[artifact].md

## Key Rules
- Only modify files within your assigned write surface
- Do NOT modify status.md — leader will update it
- Append to mailbox.md if you encounter blockers or interface changes
- For shipper teammate: read credentials.md first — do NOT attempt push without PASS
- For shipper teammate: after target repo push, sync logs to brain repo per skills/brain-sync/SKILL.md
```

**Note**: When dispatching builder or recorder, include `isolation: "worktree"` in the `Agent` tool call.

### Dispatch Rules

**Code workflows (1, 2, 4, 5)**: planner → (builder ∥ tester) → recorder → reviewer → shipper?. Builder + tester MUST be dispatched in the SAME message.

**Docs-only workflow (3)**: planner → recorder → reviewer → shipper?. No builder, no tester.

**Pipeline isolation at dispatch**: builder gets `spec.md` path (NEVER `test-spec.md`). Tester gets `test-spec.md` path (NEVER `spec.md`). In docs-only workflows, recorder gets `spec.md` (as implementer). Reviewer gets ALL artifacts.

---

## Session Startup

At the start of every session:

1. Read `.statsclaw/CONTEXT.md` if it exists.
2. If it does not exist, create a minimal local runtime: `.statsclaw/`, `.statsclaw/packages/`, `.statsclaw/runs/`, `.statsclaw/logs/`, `.statsclaw/tmp/`, `CONTEXT.md` from `templates/context.md`, package contexts from `templates/package.md`.
3. If the user message includes a target repo path or GitHub URL, **acquire both repos** into `.repos/`:
   - **Target repo**: clone or pull. Symlinks supported.
   - **Brain repo**: clone or pull `[owner]/statsclaw-brain`. Auto-create if it doesn't exist. Warn user if creation fails.
4. **Verify push credentials** for **both repos** — follow `skills/credential-setup/SKILL.md`. Brain repo credential failure is a warning, not a hard gate.
5. If no target is clear, infer from context or ask one concise question.
6. Determine the project profile using `skills/profile-detection/SKILL.md` or repo markers in `profiles/*.md`.

---

## Agent Teams Model

StatsClaw uses Agent Teams exclusively. You are the Team Leader (`leader`). You MUST use the `Agent` tool to dispatch specialist teammates. You MUST NOT perform teammate work yourself. There is no fallback mode.

### Two-Pipeline Architecture

```
              planner (bridge)
             /                \
  spec.md  /                    \  test-spec.md
           /                      \
      builder                    tester
  (code pipeline)          (test pipeline)
           \                      /
            \                    /
              recorder (recording)
                    |
              reviewer (convergence)
                    |
                  shipper
```

| Layer | Agent | Pipeline | Role | Definition |
| --- | --- | --- | --- | --- |
| Control | `leader` | — | Plans, dispatches, manages state | `.agents/leader.md` |
| Analysis | `planner` | Bridge | Produces `spec.md` AND `test-spec.md` | `.agents/planner.md` |
| Code | `builder` | Code | Implements from `spec.md` only (worktree) | `.agents/builder.md` |
| Test | `tester` | Test | Validates from `test-spec.md` only | `.agents/tester.md` |
| Recording | `recorder` | Both | Architecture, process-record log, documentation (mandatory, worktree) | `.agents/recorder.md` |
| Convergence | `reviewer` | Both | Cross-compares both pipelines; ship verdict | `.agents/reviewer.md` |
| Ship | `shipper` | — | Commits, pushes, PRs, issue comments (conditional) | `.agents/shipper.md` |

**Mandatory teammates** (never skip for non-trivial requests): planner, recorder, reviewer.

**Conditional teammates**: builder (code changes only), tester (code changes only — NOT needed for docs-only), shipper (ship requested).

**Recorder dual role**: Recorder is ALWAYS mandatory. In code workflows, recorder is the recorder (runs after builder + tester). In docs-only workflows, recorder is ALSO the implementer (replaces builder, receives `spec.md`). No tester is dispatched for docs-only — reviewer provides the quality gate directly.

Each agent's full workflow, allowed reads/writes, and must-not rules are defined in its `.agents/*.md` file. Pipeline isolation rules are in `skills/isolation/SKILL.md`. Artifact handoff rules are in `skills/handoff/SKILL.md`.

---

## Workflow Catalog

**Notation**: `∥` = parallel dispatch. `→` = sequential. `?` = conditional.

| # | Name | Trigger | Agent Sequence |
| --- | --- | --- | --- |
| 1 | Code Change | Code modification (any size) | `leader → planner → [builder ∥ tester] → recorder → reviewer` |
| 2 | Code + Ship | Code modification + push | `leader → planner → [builder ∥ tester] → recorder → reviewer → shipper` |
| 3 | Docs Only | Documentation-only changes (no source code) | `leader → planner → recorder → reviewer` |
| 4 | Issue Patrol | Scan + fix multiple issues | `leader scans → per issue: planner → [builder ∥ tester] → recorder → reviewer → shipper` |
| 5 | Single Issue | Fix one named issue | `leader → planner → [builder ∥ tester] → recorder → reviewer → shipper` |
| 6 | Validation | Run tests only | `leader → tester` |
| 7 | Ship Only | Push reviewed changes | `leader → reviewer → shipper` |
| 8 | Review Only | Assess without shipping | `leader → reviewer` |
| 9 | Scheduled Loop | Recurring execution | `leader → /loop → inner workflow` |
| 10 | Simplified | Small routine change (user confirms) | `leader → builder → tester → shipper?` |

**Key distinction — code vs docs workflows:**
- **Workflows 1–2** (code): Builder implements source code, tester validates in parallel, then recorder records.
- **Workflow 3** (docs-only): Recorder IS the implementer — receives `spec.md` and writes documentation. No builder, no tester. Reviewer provides the quality gate directly.
- **Workflows 4–5** (issues): Standard code pipeline per issue. Recorder records each fix.

**Workflow details**: Each workflow's agent cooperation, artifacts, and state transitions are documented in the respective agent definitions (`.agents/*.md`) and skills (`skills/*.md`). Key references:

- **Workflows 1–5**: Two-pipeline flow. See `skills/handoff/SKILL.md` for artifact flow between agents.
- **Workflow 3**: Docs-only — recorder replaces builder as the implementer. Recorder receives `spec.md` (what docs to write), produces documentation changes + recording artifacts (architecture.md, log entry, docs.md). No builder or tester is dispatched. Reviewer reviews directly after recorder. State goes `SPEC_READY` → `DOCUMENTED` (skips `PIPELINES_COMPLETE`).
- **Workflow 4**: See `skills/issue-patrol/SKILL.md` for patrol phases (scan, triage, fix loop, report).
- **Workflow 6**: Lightweight — no planner, builder, or reviewer. Tester runs profile validation commands directly. State jumps directly from `PLANNED` to `PIPELINES_COMPLETE` (tester-only).
- **Workflows 7–8**: Lightweight — skip the full pipeline. These are for already-completed work that needs shipping or review. State model requirements for `SPEC_READY` and `PIPELINES_COMPLETE` are waived; reviewer reads whatever artifacts are available.
- **Workflow 9**: Leader invokes `/loop` via `Skill` tool. See "Scheduled Loop" below.
- **Workflow 10**: Simplified — for small, routine changes (≤3 files, no algorithms, no uploaded files). Leader asks user to confirm simplified vs full. Skips planner, recorder, reviewer. Builder uses `request.md` as spec. Tester is the quality gate. State: `PLANNED` → `PIPELINES_COMPLETE` → `REVIEW_PASSED` → `DONE`. See `skills/simplified-workflow/SKILL.md`. If complexity exceeds expectations, leader MUST escalate to full workflow.

**Lightweight workflow rule**: Workflows 6, 7, 8, and 10 are exceptions to the "mandatory teammates" rule. They serve specific, limited purposes (validation-only, ship-only, review-only, simplified) and intentionally skip the full two-pipeline flow.

---

## Routing

Route semantically from intent. Do **not** require the user to learn trigger phrases.

| User intent | Workflow |
| --- | --- |
| code change (bug fix, feature, refactor) | 1 (code change) or 2 (+ ship) |
| code change + "ship" / "push" | 2 (code + ship) |
| documentation only (quarto book, vignettes, tutorials, README, man pages, examples) | 3 (docs only — recorder implements) |
| "patrol issues" / "check issues and fix" / "auto-fix" | 4 (issue patrol) |
| "fix issue #N" | 5 (single issue fix) |
| "check" / "validate" / "run tests" | 6 (tester only) |
| "ship it" / "push" / "open a PR" | 7 (reviewer → shipper) |
| "review" / "is this safe?" | 8 (reviewer only) |
| "loop" / "every Xm" / "monitor every" | 9 (/loop wrapping inner workflow) |
| formalize math, equations, algorithms | 1 (code pipeline) |
| small routine change (typo, config, bump, lint fix) | 10 (simplified — ask user to confirm) |

**Routing rule — simplified vs full**: Before committing to workflow 1–5, leader evaluates smallness criteria (see `skills/simplified-workflow/SKILL.md`). If ALL criteria are met, leader asks the user via `AskUserQuestion` to choose simplified or full. If the user declines or leader is uncertain, use the standard workflow. Leader MUST NOT silently downgrade to simplified.

**Routing rule — code vs docs**: If the request touches ONLY documentation files (`.Rd`, `.md`, `.qmd`, `.Rmd`, vignettes, tutorials, `pkgdown`, `_quarto.yml`, man pages, README) and NO source code (`.R`, `.py`, `.ts`, `.go`, `.rs`, `.ado`), use workflow 3 (docs-only — no builder, no tester). If the request touches any source code, use workflow 1 or 2 even if docs are also needed — recorder handles docs in the recording phase.

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
| **HOLD** | planner, builder, recorder, shipper | Cannot proceed without user input: undefined symbol, ambiguous spec, conflicting API, unclear requirement, permission/access issue | `HOLD` | Pause run. Forward the specific question to user via `AskUserQuestion`. Re-dispatch the same teammate with the answer. |
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
BLOCK:  tester → leader → respawn builder / planner → re-dispatch tester → continue
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

`CREDENTIALS_VERIFIED` → `NEW` → `PLANNED` → `SPEC_READY` → `PIPELINES_COMPLETE` → `DOCUMENTED` → `REVIEW_PASSED` → `READY_TO_SHIP` → `DONE`

Interrupt states (can occur at any point):
- `HOLD` — waiting for user input (only unblocked by user response)
- `BLOCKED` — validation failed (unblocked by respawning upstream teammate)
- `STOPPED` — quality gate failed (unblocked by respawning per reviewer routing)

- `SPEC_READY` requires BOTH `spec.md` and `test-spec.md`
- `PIPELINES_COMPLETE` requires BOTH `implementation.md` and `audit.md` (code workflows only; docs-only skips this state)
- `CREDENTIALS_VERIFIED` is the entry gate — no run without confirmed push access
- Only `leader` may update `status.md`
- All transitions subject to the precondition table above

---

## Target Repository Boundaries

- Target repositories live under `.repos/` (git-ignored) — they are never committed to StatsClaw. Symlinks into `.repos/` are also supported for users who keep repos elsewhere.
- When the user target is a repository other than `StatsClaw`, versioned `StatsClaw` files are not part of the write surface
- All target code changes, validation runs, commits, pushes, and PRs must happen in the target repository under `.repos/`
- `StatsClaw` only receives local runtime updates under `.statsclaw/`
- **Workflow logs and process records do NOT go into target repos.** They are synced to the brain repo (`[owner]/statsclaw-brain`). Target repos contain only code + essential user-facing documentation.

---

## Autonomous Continuation

For non-trivial requests, you MUST continue through the selected workflow without waiting for stage-by-stage confirmation. Only pause when: the workflow raises `HOLD`, the target is ambiguous, a destructive action requires consent, or the user asked for a checkpoint.

---

## Runtime Maintenance

- **Cleanup**: Runs older than 7 days under `.statsclaw/runs/` may be deleted to free disk space. Do not delete the active run.
- **Logs**: Write diagnostic output to `.statsclaw/logs/` when debugging workflow issues (e.g., signal routing decisions, retry attempts, credential probe output).
- **Locks**: The `locks/` directory under each run prevents concurrent writes when multiple teammates target overlapping files. Use `templates/lock.md` format. Only `leader` creates, transfers, or releases locks. Typical use: lock a file set before dispatching builder in worktree, release after merge-back.
- **Tmp**: The `.statsclaw/tmp/` directory holds transient data (e.g., worktree extraction paths, intermediate query results). Contents may be deleted between runs.

---

## Principles

- **Credentials first, work second.** Verify push access before creating a run.
- **Team Leader dispatches, never does.** You plan, route, and coordinate via the `Agent` tool.
- **Two pipelines, fully isolated.** Code pipeline and test pipeline never see each other's specs. Planner bridges; reviewer converges.
- **Planner first, always.** Every non-trivial request starts with dual-spec production.
- **Adversarial verification by design.** Independent convergence proves correctness.
- **Hard gates, not soft advice.** State transitions have preconditions; artifacts are verified, not assumed.
- **Worktree isolation for writers.** `isolation: "worktree"` for builder and recorder.
- **Ship actions are explicit.** Do not push unless the user asked, issue-patrol is active, or a single-issue fix was requested (workflow 5 — fixing an issue implies pushing the fix).
- **Surgical scope.** Each run modifies only what the request requires.
- **Clean target repos.** Workflow logs, process records, and architecture diagrams go to the brain repo — never the target repo. Target repos contain only code + essential user-facing docs.
- **Parallel when possible.** Builder and tester are ALWAYS dispatched in parallel.
- **Tolerance integrity is absolute.** Tester MUST NEVER relax tolerances, thresholds, or acceptance criteria to make a failing test pass. The only valid response to a genuine failure is BLOCK. Reviewer cross-audits every tolerance against test-spec.md.

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
│       ├── comprehension.md  # comprehension verification (from planner, mandatory)
│       ├── spec.md           # code pipeline input (from planner)
│       ├── test-spec.md      # test pipeline input (from planner)
│       ├── implementation.md # code pipeline output (from builder)
│       ├── audit.md          # test pipeline output (from tester)
│       ├── architecture.md   # from recorder; synced to brain repo by shipper agent
│       ├── log-entry.md      # from recorder; synced to brain repo by shipper agent
│       ├── docs.md
│       ├── review.md
│       ├── shipper.md
│       ├── mailbox.md
│       └── locks/
│   └── PATROL-<timestamp>/   # patrol runs only (workflow 4)
│       ├── request.md
│       ├── patrol-triage.md   # issue classification (from leader)
│       ├── patrol-report.md   # patrol summary (from leader)
│       └── issue-<number>/    # sub-run per issue, same structure as <request-id>/
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
│   ├── leader.md
│   ├── planner.md
│   ├── builder.md
│   ├── tester.md
│   ├── recorder.md
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
│   └── brain-sync/SKILL.md
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
│   ├── lock.md
│   ├── log-entry.md
│   └── architecture.md
├── .repos/                # target repo checkouts + brain repo, git-ignored; symlinks supported
└── .statsclaw/           # local runtime state, auto-created, git-ignored
```
