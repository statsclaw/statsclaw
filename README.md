# StatsClaw

StatsClaw is a framework-only product for Claude Code that turns a plain repository into an Agent Teams-first delivery workflow across multiple languages. It ships the orchestration rules, agent definitions, project profiles, templates, and docs needed to take a request from planning to production, assurance, and externalization.

StatsClaw does **not** track a user's project history by default. All runtime state is local under `.statsclaw/` and ignored by git.

---

## What You Install

This repository contains the reusable framework:

- `CLAUDE.md` — layered orchestration policy
- `.agents/` — isolated internal agent definitions
- `skills/` — shared protocol skills used across agents
- `profiles/` — language and project-type execution rules
- `templates/` — per-agent input/output templates plus shared runtime templates
- `docs/` — single product and workflow guide

This repository also enables Claude Code Agent Teams experimentally at the project level through `.claude/settings.json`.

This repository does **not** contain user-specific runtime artifacts after installation:

- project contexts in active use
- generated request runs
- diagnostic reports
- algorithm specs
- task ledgers or event logs
- local logs or temporary files

---

## Layered Agents

StatsClaw coordinates five layers:

| Layer | Agents | Role |
| --- | --- | --- |
| `Control` | `lead` | Acts as Team Lead and owns run lifecycle, routing, retries, and the shared task list |
| `Planning` | `lead`, `theorist` | Owns the request contract, impact map, and any formal mathematical specification |
| `Production` | `builder`, `scribe` | Owns code, tests, docs, examples, and tutorial updates |
| `Assurance` | `auditor`, `skeptic` | Owns validation evidence and the final ship gate |
| `Externalization` | `github` | Owns issue intake, PR interactions, checks, and explicit ship-facing actions |

The key design choice is **single ownership per decision**:

- `lead` owns the request contract and repo-wide impact map
- `auditor` produces validation evidence
- `skeptic` challenges that evidence instead of duplicating it
- `github` normalizes external signals but does not own the internal request contract

---

## Closed-Loop Workflow

For a full feature or method request, the standard path is:

```text
lead → theorist? → builder → auditor → scribe? → skeptic → github?
```

For issue-driven work, the path can begin with:

```text
github → lead → ...
```

Meaning:

- `lead` combines Team Lead coordination with one-time planning
- `theorist` runs only when the request changes mathematical logic
- `scribe` runs only when public-facing docs or examples are in scope
- `auditor` and `skeptic` are intentionally separate: evidence first, gate second
- `github` owns external actions such as issue follow-up, commit, push, and PR creation

StatsClaw is designed to map cleanly onto Claude Code Agent Teams: one Team Lead, a shared task list, teammate coordination through a mailbox, and limited parallelism for interdependent work.

For stronger isolation, StatsClaw expects either:

- one worktree per active writing teammate, or
- lock-based write ownership under `.statsclaw/runs/<request-id>/locks/`

Shared behaviors such as mailbox usage, lock discipline, and handoff rules live in `skills/`; fixed identities and boundaries live in `.agents/`.
Per-agent I/O contracts live in `templates/`, while shared runtime contracts remain there as a small common core. In practice, the agent output templates describe which runtime artifacts must exist, and the shared templates define the shapes of the long-lived local files that keep handoffs consistent.

StatsClaw keeps one workflow and switches execution rules by project profile. Profiles currently cover:

- `r-package`
- `python-package`
- `typescript-package`
- `stata-project`

---

## Shared Runtime

The workflow is stateful. Each active request gets a local run folder under `.statsclaw/runs/<request-id>/`.

Typical contents:

```text
.statsclaw/runs/<request-id>/
├── request.md
├── status.md
├── impact.md
├── spec.md
├── implementation.md
├── audit.md
├── docs.md
├── review.md
├── github.md
├── mailbox.md
├── locks/
└── tasks/
```

Agents cooperate through these artifacts instead of relying on shared hidden context.

---

## Quick Start

1. Clone this repository.
2. Open it in Claude Code.
3. Tell Claude what you want and include the target project path.

StatsClaw will automatically:

- create `.statsclaw/` if it is missing
- create the active project context
- detect the project profile
- create the active request run
- route work through the Team Lead and teammates model

If `StatsClaw` is the repository currently open in Claude Code, non-trivial requests should enter the StatsClaw workflow by default. The user does not need to say "use StatsClaw" or "start with lead"; a target path plus the task is enough.

Example prompts:

```text
Work on ~/GitHub/fect.
Check all plot-related content.

~/GitHub/fect
Fix the failing tests and update docs.

Work on ~/GitHub/fect.
Inspect open GitHub issues, build an actionable queue, and route the top issue into the workflow.

Work on ~/GitHub/fect.
Every day at 00:00 America/Los_Angeles, scan the repo's open GitHub issues, pick the top actionable one, and run the full StatsClaw workflow to solve it.

处理 /Users/tianzhuqin/GitHub/fect。
每天 0 点 PT 扫描 open issues，只看 bug label，并自动激活整个 workflow 去解决。

Work on ~/GitHub/fect.
Map the project once, identify the affected surfaces, and implement the change without duplicate discovery work.

Work on ~/GitHub/fect.
Read ~/papers/method.pdf, formalize the estimator, implement it, validate it, update docs, and prepare a ship handoff.

Work on ~/project/my_python_lib.
Fix [bug], run validation, update docs, and prepare a PR summary.
```

---

## Repository Layout

```text
StatsClaw/
├── CLAUDE.md
├── README.md
├── .agents/
├── skills/
├── profiles/
├── docs/
├── templates/
└── .statsclaw/           # local only, auto-created at runtime, ignored by git
```

See `docs/README.md` for the full guide.

---

## Design Principles

- **Framework repo, local runtime.** Product code is versioned; user runtime artifacts are local.
- **Team Lead first.** Non-trivial work begins under `lead`, not ad hoc role switching.
- **Plan once.** `lead` owns both the request contract and the impact map so downstream agents do not repeat discovery work.
- **Agent Teams first.** Prefer a Team Lead with a small teammate set for interdependent work.
- **Hard isolation first.** Writing teammates should use isolated worktrees or explicit locks.
- **Shared methods, isolated authority.** Shared protocol skills are reusable; scope, locks, and ownership remain agent-specific.
- **Math before code.** New statistical or algorithmic logic starts with `theorist`.
- **Evidence before gate.** `auditor` proves what happened; `skeptic` decides whether that proof is good enough.
- **Docs follow validated implementation.** Public docs are updated from the final understood change, not guessed early.
- **Explicit ship actions.** No commit, push, PR, issue comment, or version bump without user instruction unless the active GitHub policy explicitly requires the follow-up.

