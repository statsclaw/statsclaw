# StatsClaw Framework Overview

StatsClaw is an Agent Teams framework for Claude Code. It orchestrates multi-agent workflows for building, validating, documenting, reviewing, and shipping code changes across repositories and languages.

## Agents

StatsClaw uses 7 agents organized into layers:

| Layer | Agent | Role |
| --- | --- | --- |
| Control | **lead** | Plans work, dispatches teammates, manages state |
| Planning | **theorist** | Formalizes mathematical and algorithmic specifications |
| Production | **builder** | Implements code and test changes |
| Production | **scribe** | Updates documentation, examples, and tutorials |
| Assurance | **auditor** | Runs validation commands and produces evidence |
| Assurance | **skeptic** | Reviews the full evidence chain and issues ship verdict |
| Externalization | **github** | Handles commits, pushes, PRs, and issue interactions |

Lead is the only agent that runs in the main conversation. All others are dispatched as sub-agents via the Agent tool.

## Closed-Loop Workflow

The default workflow for a non-trivial request:

```
lead plans → theorist? → builder → auditor → scribe? → skeptic → github?
```

Stages marked with `?` are conditional. Theorist runs only for math/algorithm changes. Scribe runs only when docs are in scope. Github runs only when the user asks to ship.

Lead mediates every handoff. Each teammate produces one output artifact. Downstream teammates read upstream artifacts rather than re-discovering.

## State Transitions

Each run moves through explicit states stored in `status.md`:

```
NEW → PLANNED → SPEC_READY? → IMPLEMENTED → VALIDATED → DOCUMENTED? → REVIEW_PASSED → READY_TO_SHIP → DONE
```

Failure states: `HOLD` (needs user input), `BLOCKED` (validation failed), `STOPPED` (skeptic rejected).

On `BLOCK`, lead respawns the responsible builder/theorist. On `STOP`, lead respawns the responsible teammate and re-validates. On `HOLD`, lead asks the user.

## Isolation

Writing teammates (builder, scribe) run with `isolation: "worktree"` so each gets its own copy of the repository. Read-only teammates (auditor, skeptic) operate on the main checkout.

No two writing teammates may modify overlapping files. Write surfaces are defined in `impact.md` and enforced by convention. Only lead may update `status.md` and lock files.

Communication between isolated teammates flows through a shared append-only mailbox at `.statsclaw/runs/<request-id>/mailbox.md`.

## Runtime Layout

All run state lives under `.statsclaw/` (git-ignored):

```
.statsclaw/
├── CONTEXT.md          # Active project context
├── packages/           # Per-package metadata
├── runs/<request-id>/  # Per-run artifacts (request, status, impact, etc.)
├── logs/
└── tmp/
```

## Profiles

Profiles under `profiles/` define language- and ecosystem-specific conventions: repo markers, build tools, validation commands, documentation formats, and shipping steps.

### Adding a New Profile

1. Create `profiles/<name>.md`.
2. Define: repo markers (files that identify this project type), build/install commands, test/check commands, documentation build commands, and shipping conventions.
3. StatsClaw auto-detects the profile from repo markers. If detection is ambiguous, it asks the user.

## Key Principles

- **Short prompts work.** A target repo path and a task description are enough to trigger the full workflow.
- **Acquire target first.** The target repository must exist locally before any work begins.
- **Plan once.** Lead writes `impact.md` so teammates do not repeat discovery.
- **Math before code.** Algorithm changes start with theorist.
- **Produce once, challenge once.** Auditor validates; skeptic challenges.
- **Ship actions are explicit.** Nothing is pushed or PR'd without the user asking.
