# StatsClaw

StatsClaw is a framework-only product for Claude Code that turns a plain repository into a structured delivery workflow across multiple languages. It ships the orchestration rules, agent definitions, project profiles, templates, and docs needed to take a request from intake to implementation, validation, documentation, review, and release.

StatsClaw does **not** track a user's project history by default. All runtime state is local under `.statsclaw/` and ignored by git.

---

## What You Install

This repository contains the reusable framework:

- `CLAUDE.md` — workflow orchestrator
- `skills/` — agent definitions
- `profiles/` — language and project-type execution rules
- `templates/` — structured artifacts for requests, specs, audits, reviews, and docs
- `docs/` — single product and workflow guide

This repository does **not** contain user-specific runtime artifacts after installation:

- project contexts in active use
- generated request runs
- diagnostic reports
- algorithm specs
- local logs or temporary files

---

## Agent Team

StatsClaw coordinates nine specialists:

| Agent | Role |
| --- | --- |
| `triage` | Turns a natural-language request into a structured task contract |
| `github` | Handles issues, PRs, checks, labels, and daily issue queue interactions |
| `scout` | Maps project structure, exports, dependencies, tooling, and blast radius |
| `theorist` | Converts mathematical intent into a formal implementation spec |
| `builder` | Implements the requested change in the target project |
| `auditor` | Runs profile-aware checks, tests, examples, and docs or tutorial builds |
| `scribe` | Updates profile-appropriate docs, examples, tutorials, and public guidance |
| `skeptic` | Reviews the full finished change set before shipping |
| `release` | Handles changelog, versioning, commit, PR, and delivery artifacts |

---

## Closed-Loop Workflow

For a full feature or method request, the standard path is:

```text
triage → scout → theorist? → builder → auditor → scribe → skeptic → release?
```

For issue-driven work, the path can begin with:

```text
github → triage → scout → ...
```

Meaning:

- `theorist` is required when the request changes mathematical logic
- `scribe` runs after validation so docs match the final code
- `skeptic` reviews the complete finished artifact set
- `release` only runs when the user explicitly asks to ship

StatsClaw keeps one workflow and switches execution rules by project profile. Profiles currently cover:

- `r-package`
- `python-package`
- `typescript-package`
- `stata-project`

StatsClaw can also operate in GitHub-driven mode:

- inspect issues and PRs
- summarize CI/check failures
- create issue-driven run artifacts
- maintain a daily actionable issue queue

The GitHub agent can also manage a recurring scan schedule inside the Claude-side workflow layer, for example:

- scan the target repo's open issues every day at `00:00 America/Los_Angeles`
- build an actionable queue
- activate the full StatsClaw workflow for the top actionable issue
- after solving, push the changes to the corresponding branch and reply on the issue with the resolution summary

This schedule belongs to the StatsClaw runtime and is handled by Claude-side orchestration rather than external GitHub Actions.

You do not need to fill schedule fields manually. You can just say things like:

- "每天 0 点 PT 扫描"
- "每周一早上 9 点扫一次"
- "只看 bug label"
- "自动激活整个 workflow 去解决"

GitHub access preference:

- preferred: `gh` CLI if it is installed and authenticated
- fallback: GitHub REST API via `GH_TOKEN` or `GITHUB_TOKEN`
- if neither exists, the GitHub agent should pause with a clear HOLD instead of silently failing

Issue-resolution policy:

- after an issue-driven workflow succeeds, StatsClaw should push the changes to the corresponding branch
- it should also post an issue comment summarizing what was solved and where the branch/PR lives
- it must not auto-close the issue

The workflow is stateful. Each active request gets a local run folder under `.statsclaw/runs/<request-id>/`.

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

Example prompts:

```text
Work on ~/GitHub/fect.
Inspect open GitHub issues, build an actionable queue, and route the top issue into the workflow.

Work on ~/GitHub/fect.
Every day at 00:00 America/Los_Angeles, scan the repo's open GitHub issues, pick the top actionable one, and run the full StatsClaw workflow to solve it.

处理 /Users/tianzhuqin/GitHub/fect。
每天 0 点 PT 扫描 open issues，只看 bug label，并自动激活整个 workflow 去解决。

Work on ~/GitHub/fect.
Map the project and identify the files affected by a new ATT estimator.

Work on ~/GitHub/fect.
Formalize the following estimator from the paper and implement it.

Work on ~/GitHub/fect.
Read ~/papers/method.pdf, extract the estimator, formalize it, and implement it in the project.

Work on ~/GitHub/fect.
Run the full validation workflow and tell me what is blocking release.

Work on ~/GitHub/fect.
Prepare docs, review the change, and create a release-ready handoff.

Work on ~/project/my_python_lib.
Fix [bug], run validation, update docs, and prepare a PR summary.
```

---

## Repository Layout

```text
StatsClaw/
├── CLAUDE.md
├── README.md
├── profiles/
├── docs/
├── skills/
├── templates/
└── .statsclaw/           # local only, created by bootstrap, ignored by git
```

See `docs/README.md` for the full guide.

---

## Design Principles

- **Framework repo, local runtime.** Product code is versioned; user runtime artifacts are local.
- **Profile-aware execution.** The workflow stays stable while validation, docs, and packaging rules come from the active project profile.
- **Math before code.** New statistical or algorithmic logic starts with a formal spec.
- **Validation before documentation sign-off.** Docs follow passing checks.
- **Review before release.** Shipping happens only after a skeptical review.
- **Explicit release actions.** No commit, PR, or version bump without user instruction.
- **GitHub-aware intake.** Issue-driven work can enter the workflow through the GitHub agent, including Claude-managed recurring scans.

