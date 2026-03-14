# StatsClaw

StatsClaw is a framework-only product for Claude Code that turns a plain repository into an Agent Teams workflow across multiple languages. It ships orchestration rules, agent definitions, project profiles, and runtime templates.

All runtime state is local under `.statsclaw/` and ignored by git.

---

## What You Install

- `CLAUDE.md` — orchestration policy (the authoritative reference)
- `.agents/` — agent definitions (lead, theorist, builder, auditor, scribe, skeptic, github)
- `skills/` — shared protocol skills (credential-setup, isolation, handoff, mailbox, issue-patrol, profile-detection)
- `profiles/` — language-specific execution rules (R, Python, TypeScript, Stata, Go, Rust)
- `templates/` — runtime artifact templates (context, package, status, credentials, mailbox, lock)

Agent Teams is enabled at the project level through `.claude/settings.json`.

---

## Two-Pipeline Architecture

StatsClaw uses two fully isolated execution pipelines that converge at the skeptic:

```
                    theorist (bridge)
                   /                \
        spec.md  /                    \  test-spec.md
               /                        \
          builder                      auditor
      (code pipeline)            (test pipeline)
               \                        /
                \                      /
                   skeptic (convergence)
                       |
                     github
```

| Layer | Agent | Pipeline | Role |
| --- | --- | --- | --- |
| Control | `lead` | — | Plans work, dispatches teammates, manages state |
| Analysis | `theorist` | Bridge | Produces `spec.md` AND `test-spec.md` from requirements |
| Code | `builder` | Code | Implements from `spec.md` only (never sees test-spec.md) |
| Test | `auditor` | Test | Validates from `test-spec.md` only (never sees spec.md) |
| Docs | `scribe` | Code | Updates documentation (conditional) |
| Convergence | `skeptic` | Both | Cross-compares both pipelines; issues ship verdict |
| Ship | `github` | — | Commits, pushes, PRs, issue comments (conditional) |

**Key properties:**
- **Theorist is always mandatory** — it bridges both pipelines
- **Builder and auditor run in parallel** — each with its own isolated spec
- **Pipeline isolation is enforced** — builder never sees test-spec.md, auditor never sees spec.md
- **Adversarial verification** — if both pipelines converge independently, confidence is high

---

## Workflow

```text
lead plans → theorist → [builder ∥ auditor] → scribe? → skeptic → github?
```

States: `CREDENTIALS_VERIFIED → NEW → PLANNED → SPEC_READY → PIPELINES_COMPLETE → DOCUMENTED? → REVIEW_PASSED → READY_TO_SHIP → DONE`

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
│   ├── spec.md             # code pipeline input (from theorist)
│   ├── test-spec.md        # test pipeline input (from theorist)
│   ├── implementation.md   # code pipeline output (from builder)
│   ├── audit.md            # test pipeline output (from auditor)
│   ├── architecture.md     # system architecture diagram (from scribe, mandatory)
│   ├── docs.md             # documentation changes (from scribe)
│   ├── review.md           # convergence verdict (from skeptic)
│   ├── github.md           # ship actions (from github)
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
├── .agents/            # agent definitions
├── skills/             # shared protocol skills (6 skills)
├── profiles/           # language execution rules (6 languages)
├── templates/          # runtime artifact templates
└── .statsclaw/         # local only, auto-created, git-ignored
```

---

## Design Principles

- **Credentials first, work second.** Verify push access before creating a run.
- **Team Lead dispatches, never does.** Lead plans and coordinates; teammates do the work.
- **Two pipelines, fully isolated.** Code pipeline and test pipeline never see each other's specs.
- **Theorist first, always.** Every non-trivial request starts with dual-spec production.
- **Adversarial verification by design.** Independent convergence proves correctness.
- **Hard gates, not soft advice.** State transitions have preconditions; artifacts are verified.
- **Worktree isolation for writers.** Builder and scribe run in isolated git worktrees.
- **Surgical scope.** Each run modifies only what the request requires.
- **Explicit ship actions.** Nothing is pushed without user instruction or active patrol skill.
