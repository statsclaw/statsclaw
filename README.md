# StatsClaw

**A workflow framework for statistical package development.**

**An open-source tool that helps researchers build, test, and document statistical software packages with AI agent teams.**

[Website](https://statsclaw.ai) · [Roadmap](ROADMAP.md) · [Contributing](CONTRIBUTING.md) · [Discussions](https://github.com/statsclaw/statsclaw/discussions)

---

## What is StatsClaw?

StatsClaw is a framework for [Claude Code](https://claude.ai/code) that uses **AI agent teams** to assist with statistical package development. You describe what you need — a bug fix, a new feature, a cross-language translation — and StatsClaw coordinates multiple AI agents to help you build, test, and document the result. It works best when a domain expert stays in the loop to guide decisions.

---

## How It Works

StatsClaw orchestrates a team of **9 specialized AI agents**, each operating under strict information isolation:

| Agent | Role |
|:------|:-----|
| **Leader** | Orchestrates the workflow, dispatches agents, enforces isolation |
| **Planner** | Reads your paper/formulas, executes deep comprehension protocol, produces specifications |
| **Builder** | Writes source code from `spec.md` (never sees the test spec) |
| **Tester** | Validates independently from `test-spec.md` (never sees the code spec) |
| **Simulator** | Runs Monte Carlo studies from `sim-spec.md` (never sees either spec) |
| **Scriber** | Documents architecture, generates tutorials, maintains audit trail |
| **Distiller** | Extracts reusable knowledge for the shared brain (brain mode only) |
| **Reviewer** | Cross-checks all pipelines, audits tolerance integrity, issues ship/no-ship verdict |
| **Shipper** | Commits, pushes, opens PRs, handles package distribution |

The **code**, **test**, and **simulation** pipelines are fully isolated — they never see each other's specs. If all pipelines converge independently, confidence in correctness is high. This is **adversarial verification by design**.

---

## Multi-Pipeline Architecture

```
                    planner (bridge)
                   /    |          \
        spec.md   /     |           \  sim-spec.md
                 /      |            \
            builder  test-spec.md   simulator
       (code pipeline)  |      (simulation pipeline)
                 \      |            /
                  \     v           /
                   \  tester      /
                    \   |        /
                     \  |       /
                      scriber (recording)
                          |
                      distiller (brain mode only)
                          |
                      reviewer (convergence)
                          |
                        shipper
```

**Key properties:**

- **Planner is always mandatory** — it bridges all pipelines
- **Builder handles code, scriber handles docs, simulator handles Monte Carlo studies** — for docs-only requests, scriber replaces builder as implementer
- **Builder and simulator run in parallel** (simulation workflows), then **tester validates the merged result** — each pipeline has its own isolated spec
- **Pipeline isolation is enforced** — each pipeline never sees another's spec
- **Adversarial verification** — if all pipelines converge independently, confidence is high

---

## Supported Languages

| R | Python | Stata | TypeScript | Go | Rust | C | C++ |
|:-:|:------:|:-----:|:----------:|:--:|:----:|:-:|:---:|

More languages coming — [Julia is next](https://github.com/statsclaw/statsclaw/issues/3)! Want another? [Let us know](https://github.com/statsclaw/statsclaw/issues/new?template=feature-request.yml).

---

## Quick Start

### Prerequisites

1. **Claude Code** — [Install Claude Code](https://claude.ai/code)
2. **GitHub access** — Push access to your target repository
3. **Workspace repo** — A GitHub repo for storing workflow artifacts (auto-created if needed)

### Your First Task

Just tell StatsClaw what you want. It auto-detects the language, selects the right workflow, and starts working:

```
work on https://github.com/your-org/your-package resolve the issues
```

StatsClaw will auto-detect the language, select a workflow, and start working. It will ask you clarification questions when it encounters ambiguity — your domain expertise guides the process. Results vary depending on task complexity; expect to iterate.

---

## Workflow

```text
Code:            leader → planner → builder → tester → scriber → [distiller]? → reviewer → shipper?
Docs-only:       leader → planner → scriber → reviewer → shipper?
Simulation+Code: leader → planner → [builder ∥ simulator] → tester → scriber → [distiller]? → reviewer → shipper?
Simulation-only: leader → planner → simulator → tester → scriber → [distiller]? → reviewer → shipper?
```

States: `CREDENTIALS_VERIFIED → NEW → PLANNED → SPEC_READY → PIPELINES_COMPLETE → DOCUMENTED → [KNOWLEDGE_EXTRACTED]? → REVIEW_PASSED → READY_TO_SHIP → DONE`

Signals: `HOLD` (ambiguous, ask user), `BLOCK` (validation failed), `STOP` (unsafe to ship)

---

## What Can StatsClaw Help With?

| Task | How it helps | Limitations |
|:-----|:-------------|:------------|
| **Implementing methods** | Assists with translating specs into code | Requires researcher to validate mathematical correctness |
| **Cross-language translation** | Handles R/Python idiom differences | May miss subtle numerical edge cases without careful review |
| **Testing & validation** | Independent test pipeline catches bugs tests miss | Empirical verification, not formal proofs |
| **Monte Carlo studies** | Automates simulation harness and reporting | Researcher must design meaningful DGPs and metrics |
| **Paper-driven features** | Reads methodology papers to design new functionality | Extracts concepts, not full estimator implementations |
| **Bug fixing** | Adversarial architecture helps find hidden bugs | Complex domain bugs still need human insight |
| **Documentation** | Generates Quarto books, API docs | Needs researcher review for accuracy |

---

## Example Prompts

```
# Fix a specific issue
fix issue #42 in my-package

# Build from scratch
build a Python package from this R code

# Cross-language migration
rewrite the Python backends in pure R and ship it

# Simulation study
run a Monte Carlo study comparing these three estimators

# Paper to package
build the R works from this PDF

# Paper-driven feature
read Correia (2016) and add network visualization to panelView

# Documentation
update the documentation for v2.0
```

---

## Learn by Example

We provide examples from our own usage. Each is a real repository you can inspect and learn from. Your mileage may vary — these represent what worked for us with active researcher involvement.

| Example | Repo | What it demonstrates |
|:--------|:-----|:---------------------|
| Iterative refactoring (1 to 2) | [`statsclaw/example-fect`](https://github.com/statsclaw/example-fect) | Multi-day, researcher-guided refactoring of an R package |
| Python from R source (0 to 1) | [`statsclaw/example-R2PY`](https://github.com/statsclaw/example-R2PY) | Building a Python package from an R reference |
| Paper to package + Monte Carlo | [`statsclaw/example-probit`](https://github.com/statsclaw/example-probit) | PDF manuscript to R/C++ package + simulation |
| Paper-driven feature addition | [`statsclaw/example-panelView`](https://github.com/statsclaw/example-panelView) | Reading a methodology paper to design a new feature |

See the [workspace example](https://github.com/statsclaw/example-workspace) for the actual workflow artifacts produced during these examples.

---

## What You Install

- `CLAUDE.md` — orchestration policy (the authoritative reference)
- `agents/` — agent definitions (leader, planner, builder, tester, simulator, scriber, distiller, reviewer, shipper)
- `skills/` — shared protocol skills (credential-setup, isolation, handoff, mailbox, issue-patrol, profile-detection, brain-sync, privacy-scrub)
- `profiles/` — language-specific execution rules (R, Python, TypeScript, Stata, Go, Rust, C, C++)
- `templates/` — runtime artifact templates and repo scaffolding (brain-repo, brain-seedbank-repo)

Agent Teams is enabled at the project level through `.claude/settings.json`.

---

## Runtime Layout

All runtime state lives inside the workspace repo, organized per target repository:

```text
.repos/
├── <target-repo>/                    # target repo checkout
├── brain/                            # statsclaw/brain clone (brain mode only)
├── brain-seedbank/                   # statsclaw/brain-seedbank clone (brain mode only)
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
        │       ├── sim-spec.md       # simulation pipeline input (from planner, workflows 11/12)
        │       ├── implementation.md # code pipeline output (from builder)
        │       ├── simulation.md     # simulation pipeline output (from simulator, workflows 11/12)
        │       ├── audit.md          # test pipeline output (from tester)
        │       ├── ARCHITECTURE.md   # from scriber (primary copy in target repo root)
        │       ├── log-entry.md      # process record (from scriber; promoted to runs/<date>-<slug>.md)
        │       ├── docs.md           # documentation changes (from scriber)
        │       ├── brain-contributions.md  # knowledge entries (from distiller, brain mode only)
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
├── agents/             # agent definitions (9 agents including distiller)
├── skills/             # shared protocol skills (13 skills including brain-sync, privacy-scrub)
├── profiles/           # language execution rules (8 languages)
├── templates/          # runtime artifact templates + repo scaffolding (brain-repo, brain-seedbank-repo)
└── .repos/             # target repo checkouts + workspace + brain repos (runtime state, git-ignored)
```

---

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

## Shared Brain

StatsClaw has a shared knowledge system where techniques discovered during workflows — mathematical methods, coding patterns, validation strategies, simulation designs — are extracted, privacy-scrubbed, and contributed to a collective knowledge base. When you enable Brain mode, your agents get smarter by reading knowledge contributed by all users.

**How it works:**

1. **Read** — Your agents automatically access relevant knowledge entries from [`statsclaw/brain`](https://github.com/statsclaw/brain)
2. **Contribute** — After noteworthy workflows, the distiller agent extracts reusable knowledge. You review everything and approve or decline — nothing is shared without your explicit consent
3. **Earn badges** — Accepted contributions earn virtual badges on the [Contributors leaderboard](https://github.com/statsclaw/brain/blob/main/CONTRIBUTORS.md)

**Privacy guarantee:** All contributions are automatically scrubbed of repo names, file paths, usernames, proprietary code, and any identifying information. Only generic, reusable knowledge is shared.

| Repo | Purpose |
|:-----|:--------|
| [`statsclaw/brain`](https://github.com/statsclaw/brain) | Curated knowledge — agents read from here |
| [`statsclaw/brain-seedbank`](https://github.com/statsclaw/brain-seedbank) | Contribution staging — users submit PRs here |

Brain mode is optional — you choose at session start. See [Brain System Documentation](.github/BRAIN.md) for full details.

---

## Design Principles

- **Credentials first, work second.** Verify push access before creating a run.
- **Team Leader dispatches, never does.** Leader plans and coordinates; teammates do the work.
- **Multi-pipeline, fully isolated.** Code, test, and simulation pipelines never see each other's specs.
- **Planner first, always.** Every non-trivial request starts with dual-spec production.
- **Adversarial verification by design.** Independent convergence proves correctness.
- **Hard gates, not soft advice.** State transitions have preconditions; artifacts are verified.
- **Worktree isolation for writers.** Builder, simulator, and scriber run in isolated git worktrees.
- **Surgical scope.** Each run modifies only what the request requires.
- **Explicit ship actions.** Nothing is pushed without user instruction or active patrol skill.
- **Collective knowledge, individual consent.** Brain mode lets agents learn from all users, but nothing is shared without explicit per-workflow approval.

---

## Get Involved

We are building StatsClaw in the open. Everyone is welcome.

- **Share an idea** — [Discussions](https://github.com/statsclaw/statsclaw/discussions/categories/ideas)
- **Report a bug** — [Bug report](https://github.com/statsclaw/statsclaw/issues/new?template=bug-report.yml)
- **Contribute code** — [Contributing guide](CONTRIBUTING.md)
- **Contribute knowledge** — Enable Brain mode and your discoveries help everyone. [Learn more](.github/BRAIN.md)
- **See what is planned** — [Roadmap](ROADMAP.md)

---

**[statsclaw.ai](https://statsclaw.ai)**

*A tool for statisticians and econometricians. Works best with an expert in the loop.*
