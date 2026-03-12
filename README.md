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

StatsClaw coordinates eight specialists:

| Agent | Role |
| --- | --- |
| `triage` | Turns a natural-language request into a structured task contract |
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

