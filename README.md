# StatsClaw

StatsClaw is a framework-only product for Claude Code that turns a plain repository into an Agent Teams workflow across multiple languages. It ships orchestration rules, agent definitions, project profiles, and runtime templates.

All runtime state is local under `.statsclaw/` and ignored by git.

---

## What You Install

- `CLAUDE.md` — orchestration policy (the authoritative reference)
- `agents/` — agent definitions (leader, planner, builder, tester, recorder, reviewer, shipper)
- `skills/` — shared protocol skills (credential-setup, isolation, handoff, mailbox, issue-patrol, profile-detection)
- `profiles/` — language-specific execution rules (R, Python, TypeScript, Stata, Go, Rust)
- `templates/` — runtime artifact templates (context, package, status, credentials, mailbox, lock, log-entry, architecture)

Agent Teams is enabled at the project level through `.claude/settings.json`.

---

## Two-Pipeline Architecture

StatsClaw uses two fully isolated execution pipelines that converge at the reviewer:

```
                    planner (bridge)
                   /                \
        spec.md  /                    \  test-spec.md
               /                        \
          builder                      tester
      (code pipeline)            (test pipeline)
               \                        /
                \                      /
                   recorder (recording)
                       |
                   reviewer (convergence)
                       |
                     shipper
```

| Layer | Agent | Pipeline | Role |
| --- | --- | --- | --- |
| Control | `leader` | — | Plans work, dispatches teammates, manages state |
| Analysis | `planner` | Bridge | Produces `spec.md` AND `test-spec.md` from requirements |
| Code | `builder` | Code | Implements from `spec.md` only (never sees test-spec.md) |
| Test | `tester` | Test | Validates from `test-spec.md` only (never sees spec.md) |
| Recording | `recorder` | Both | Architecture, process-record log, documentation (mandatory) |
| Convergence | `reviewer` | Both | Cross-compares both pipelines; issues ship verdict |
| Ship | `shipper` | — | Commits, pushes, PRs, issue comments (conditional) |

**Key properties:**
- **Planner is always mandatory** — it bridges both pipelines
- **Builder handles code, recorder handles docs** — for docs-only requests, recorder replaces builder as implementer
- **Builder and tester run in parallel** (code workflows) — each with its own isolated spec
- **Pipeline isolation is enforced** — builder/recorder never sees test-spec.md, tester never sees spec.md
- **Adversarial verification** — if both pipelines converge independently, confidence is high

---

## Workflow

```text
Code:      leader → planner → [builder ∥ tester] → recorder → reviewer → shipper?
Docs-only: leader → planner → recorder → reviewer → shipper?
```

States: `CREDENTIALS_VERIFIED → NEW → PLANNED → SPEC_READY → PIPELINES_COMPLETE → DOCUMENTED → REVIEW_PASSED → READY_TO_SHIP → DONE`

Signals: `HOLD` (ambiguous, ask user), `BLOCK` (validation failed), `STOP` (unsafe to ship)

---

## Quick Start

1. Clone this repository.
2. Open it in Claude Code.
3. Tell Claude what you want and include the target project path.

StatsClaw auto-creates `.statsclaw/`, detects the project profile, verifies credentials, and runs the full workflow autonomously. Short prompts work:

```text
patrol fect issues on cfe
fix fect issue #42
Work on ~/GitHub/fect. Fix the failing tests.
ship it
```

---

## Runtime Layout

```text
.statsclaw/
├── CONTEXT.md              # active project context
├── packages/<name>.md      # per-package metadata
├── runs/<request-id>/
│   ├── credentials.md      # push access verification
│   ├── request.md          # scope and acceptance criteria
│   ├── status.md           # state machine
│   ├── impact.md           # affected files and risk areas
│   ├── comprehension.md    # comprehension verification (from planner, mandatory)
│   ├── spec.md             # code pipeline input (from planner)
│   ├── test-spec.md        # test pipeline input (from planner)
│   ├── implementation.md   # code pipeline output (from builder)
│   ├── audit.md            # test pipeline output (from tester)
│   ├── Architecture.md     # system architecture diagram (from recorder; synced to workspace repo)
│   ├── log-entry.md        # process record (from recorder; synced to workspace repo)
│   ├── docs.md             # documentation changes (from recorder)
│   ├── review.md           # convergence verdict (from reviewer)
│   ├── shipper.md           # ship actions (from shipper)
│   ├── mailbox.md          # inter-teammate communication
│   └── locks/              # write surface locks
├── logs/
└── tmp/
```

---

## Repository Layout

```text
StatsClaw/
├── CLAUDE.md           # orchestration policy
├── README.md
├── agents/            # agent definitions
├── skills/             # shared protocol skills (9 skills)
├── profiles/           # language execution rules (6 languages)
├── templates/          # runtime artifact templates
├── .repos/             # target repo checkouts + workspace repo (git-ignored; symlinks supported)
└── .statsclaw/         # local runtime state (git-ignored)
```

## Workspace Repository

Workflow logs, process records, and architecture diagrams are NOT stored in target repos. Instead, they are synced to a user-specified **workspace repository** on GitHub (e.g., `[username]/workspace`):

```text
workspace/
├── fect/
│   ├── Architecture.md     # latest architecture diagram
│   └── log/
│       └── 2026-03-15-fix-tests.md
├── panelview/
│   ├── Architecture.md
│   └── log/
│       └── 2026-03-17-add-feature.md
└── README.md
```

This keeps target repos clean (code + essential docs only) while preserving full traceability in one place.

---

## Design Principles

- **Credentials first, work second.** Verify push access before creating a run.
- **Team Leader dispatches, never does.** Leader plans and coordinates; teammates do the work.
- **Two pipelines, fully isolated.** Code pipeline and test pipeline never see each other's specs.
- **Planner first, always.** Every non-trivial request starts with dual-spec production.
- **Adversarial verification by design.** Independent convergence proves correctness.
- **Hard gates, not soft advice.** State transitions have preconditions; artifacts are verified.
- **Worktree isolation for writers.** Builder and recorder run in isolated git worktrees.
- **Surgical scope.** Each run modifies only what the request requires.
- **Explicit ship actions.** Nothing is pushed without user instruction or active patrol skill.
