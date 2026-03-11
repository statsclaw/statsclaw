# RClaw

An agentic workspace for developing, maintaining, and documenting statistical R packages. RClaw translates mathematical specifications into working code, validates implementations, and keeps documentation synchronized with the codebase.

RClaw is a domain-specific extension of [OpenClaw](https://github.com/xuyiqing/openclaw-brain), following the same Markdown-based, documentation-driven architecture.

---

## How It Works

RClaw operates through five specialists, each defined by a `SKILL.md` file. They are coordinated by `CLAUDE.md`, which routes user requests and enforces a standard workflow.

| Agent | Role |
| --- | --- |
| **scout** | Maps the package: structure, exports, function dependencies, affected files |
| **theorist** | Translates LaTeX equations or method descriptions into formal algorithm specs |
| **builder** | Implements and modifies R functions from algorithm specs |
| **auditor** | Runs `devtools::check()`, `testthat`, and examples; diagnoses failures |
| **scribe** | Writes and updates `.Rd` documentation, vignettes, and tutorials |

---

## Standard Workflow

For a new method, the full pipeline runs in sequence:

```
scout → theorist → builder → auditor → scribe
```

For targeted tasks (bug fix, doc update, validation run), only the relevant agent is invoked.

If **auditor** finds failures, they are routed back: code bugs go to **builder**, math inconsistencies go to **theorist**, broken examples go to **scribe**.

---

## Getting Started

1. Clone or open this repo as a Claude Code workspace.
2. Copy `packages/_template.md` to `packages/<your-package>.md` and fill it in.
3. Update `CONTEXT.md` to point to your package file:

   ```yaml
   Active: packages/<your-package>.md
   ```

4. Describe what you need. Examples:

```
"Map the fect package and show all exported functions."

"Implement the following panel data estimator: [paste LaTeX]"

"Run devtools::check() on the package and diagnose any failures."

"Write a vignette for the main estimation function."
```

---

## Repository Structure

```text
RClaw/
├── CLAUDE.md                   — orchestrator: session startup, routing, workflow rules
├── CONTEXT.md                  — points to the active package file
├── packages/
│   ├── _template.md            — copy this to add a new package
│   └── <package>.md            — per-package context: path, tasks, issues
├── skills/
│   ├── scout/SKILL.md          — repository mapping
│   ├── theorist/SKILL.md       — mathematical specification
│   ├── builder/SKILL.md        — code implementation
│   ├── auditor/SKILL.md        — validation and testing
│   └── scribe/SKILL.md         — documentation and tutorials
└── templates/
    ├── algorithm-spec.md       — structured template for method specs
    ├── diagnostic-report.md    — structured template for check output
    └── tutorial-template.md   — structured template for vignettes/tutorials
```

Runtime directories created on first use:

- `specs/` — algorithm specs produced by theorist
- `reports/` — diagnostic reports produced by auditor
- `tutorials/` — standalone tutorial files produced by scribe

---

## Design Principles

- **Math before code.** Any change to a statistical method begins with a theorist spec.
- **Numerical reliability.** builder follows the spec exactly and handles edge cases (NA, Inf, near-singular matrices) as specified.
- **Documentation is not optional.** scribe runs after every successful auditor pass.
- **Surgical changes.** builder does not touch functions outside the current task scope.
- **Templates enforce structure.** All output follows the templates in `templates/`.

---

## Phase 2 (Planned)

- `skills/triage/` — classifies GitHub issues and routes them to the right agent
- `skills/benchmarker/` — compares numerical results across package versions
