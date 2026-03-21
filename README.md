# StatsClaw

StatsClaw is a framework-only product for Claude Code that turns a plain repository into an Agent Teams workflow across multiple languages. It ships orchestration rules, agent definitions, project profiles, and runtime templates.

All runtime state lives inside the workspace repo under `.repos/workspace/<repo-name>/` and is git-ignored from StatsClaw.

---

## What You Install

- `CLAUDE.md` — orchestration policy (the authoritative reference)
- `agents/` — agent definitions (leader, planner, builder, tester, scriber, reviewer, shipper)
- `skills/` — shared protocol skills (credential-setup, isolation, handoff, mailbox, issue-patrol, profile-detection)
- `profiles/` — language-specific execution rules (R, Python, TypeScript, Stata, Go, Rust, C, C++)
- `templates/` — runtime artifact templates (context, status, credentials, mailbox, lock, log-entry, architecture)

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
                   scriber (recording)
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
| Recording | `scriber` | Both | Architecture, process-record log, documentation (mandatory) |
| Convergence | `reviewer` | Both | Cross-compares both pipelines; issues ship verdict |
| Ship | `shipper` | — | Commits, pushes, PRs, issue comments (conditional) |

**Key properties:**
- **Planner is always mandatory** — it bridges both pipelines
- **Builder handles code, scriber handles docs** — for docs-only requests, scriber replaces builder as implementer
- **Builder and tester run in parallel** (code workflows) — each with its own isolated spec
- **Pipeline isolation is enforced** — builder/scriber never sees test-spec.md, tester never sees spec.md
- **Adversarial verification** — if both pipelines converge independently, confidence is high

---

## Workflow

```text
Code:      leader → planner → [builder ∥ tester] → scriber → reviewer → shipper?
Docs-only: leader → planner → scriber → reviewer → shipper?
```

States: `CREDENTIALS_VERIFIED → NEW → PLANNED → SPEC_READY → PIPELINES_COMPLETE → DOCUMENTED → REVIEW_PASSED → READY_TO_SHIP → DONE`

Signals: `HOLD` (ambiguous, ask user), `BLOCK` (validation failed), `STOP` (unsafe to ship)

---

## Quick Start

1. Clone this repository.
2. Open it in Claude Code.
3. Tell Claude what you want and include the target project path.

StatsClaw acquires the workspace repo, creates the per-repo runtime directory, detects the project profile, verifies credentials, and runs the full workflow autonomously. Short prompts work:

```text
patrol fect issues on cfe
fix fect issue #42
Work on ~/GitHub/fect. Fix the failing tests.
ship it
```

---

## Runtime Layout

All runtime state lives inside the workspace repo, organized per target repository:

```text
.repos/
├── <target-repo>/                    # target repo checkout
└── workspace/                        # workspace repo (GitHub)
    └── <repo-name>/                  # per-target-repo runtime + logs
        ├── context.md                # active project context
        ├── CHANGELOG.md              # timeline index of all runs (pushed)
        ├── HANDOFF.md                # active handoff (pushed)
        ├── ref/                      # reference docs for future work (pushed)
        ├── runs/
        │   └── <request-id>/         # per-run artifacts
        │       ├── credentials.md    # push access verification
        │       ├── request.md        # scope and acceptance criteria
        │       ├── status.md         # state machine
        │       ├── impact.md         # affected files and risk areas
        │       ├── comprehension.md  # comprehension verification (from planner)
        │       ├── spec.md           # code pipeline input (from planner)
        │       ├── test-spec.md      # test pipeline input (from planner)
        │       ├── implementation.md # code pipeline output (from builder)
        │       ├── audit.md          # test pipeline output (from tester)
        │       ├── Architecture.md   # from scriber (primary copy in target repo root)
        │       ├── log-entry.md      # process record (from scriber; promoted to runs/<date>-<slug>.md)
        │       ├── docs.md           # documentation changes (from scriber)
        │       ├── review.md         # convergence verdict (from reviewer)
        │       ├── shipper.md        # ship actions (from shipper)
        │       ├── mailbox.md        # inter-teammate communication
        │       └── locks/            # write surface locks
        ├── logs/                     # diagnostic logs
        └── tmp/                      # transient data
```

---

## Repository Layout

```text
StatsClaw/
├── CLAUDE.md           # orchestration policy
├── README.md
├── agents/            # agent definitions
├── skills/             # shared protocol skills (9 skills)
├── profiles/           # language execution rules (8 languages)
├── templates/          # runtime artifact templates
└── .repos/             # target repo checkouts + workspace repo (runtime state, git-ignored; symlinks supported)
```

## Workspace Repository

Workflow logs, process records, and handoff documents are NOT stored in target repos. Instead, they are synced to a user-specified **workspace repository** on GitHub (e.g., `[username]/workspace`):

```text
workspace/
├── fect/
│   ├── CHANGELOG.md                # timeline index
│   ├── HANDOFF.md                  # active handoff
│   ├── ref/                        # reference docs for future work
│   │   └── cv-comparison-table.md
│   └── runs/                       # individual workflow logs
│       ├── 2026-03-16-cv-unification.md
│       └── 2026-03-17-convergence-conditioning.md
├── panelview/
│   ├── CHANGELOG.md
│   ├── HANDOFF.md
│   ├── ref/
│   └── runs/
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
- **Worktree isolation for writers.** Builder and scriber run in isolated git worktrees.
- **Surgical scope.** Each run modifies only what the request requires.
- **Explicit ship actions.** Nothing is pushed without user instruction or active patrol skill.
