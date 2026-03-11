# RClaw — R Package Development Workspace

RClaw is an agentic workspace for developing, maintaining, and documenting statistical R packages. It translates mathematical specifications into working code, validates implementations, and keeps documentation synchronized with the codebase.

---

## Session Startup

At the start of every session:

1. Read `CONTEXT.md` to find the `Active:` field, which points to a file under `packages/`.
2. Read that package file to load the package path, description, known issues, and current task.
3. If `CONTEXT.md` points to `_template.md` or the package file is unfilled, ask the user to set up their package context before proceeding.
4. Hold the package path and task in mind for all subsequent operations.

---

## Team

RClaw operates through five specialists. Each has a `skills/<name>/SKILL.md` that describes their triggers, tools, workflow, and output format.

| Name | Role |
| --- | --- |
| **scout** | Maps the package: structure, exports, dependencies, affected files |
| **theorist** | Formalizes mathematical or algorithmic specifications |
| **builder** | Implements and modifies R functions from specs |
| **auditor** | Runs `devtools::check()`, tests, and examples; diagnoses failures |
| **scribe** | Updates `.Rd` documentation, vignettes, and tutorials |

---

## Routing

Invoke skills based on the user's request. Use exact matches first; fall back to semantic judgment.

| Trigger words | Invoke |
| --- | --- |
| "map", "structure", "dependencies", "what files", "what functions", "exports" | scout |
| "formalize", "translate", "equation", "LaTeX", "algorithm spec", "identification" | theorist |
| "implement", "write", "modify", "refactor", "patch", "add function" | builder |
| "check", "test", "validate", "diagnose", "run examples", "does it pass" | auditor |
| "document", "vignette", "tutorial", "Rd", "examples", "usage" | scribe |

For a **full method request** (adding a new method end-to-end), invoke all five in sequence:

```text
scout → theorist → builder → auditor → scribe
```

---

## Standard Workflow

For any non-trivial code change:

1. **scout** — identify affected files and existing related functions
2. **theorist** — formalize the mathematical or algorithmic spec (skip if no math involved)
3. **builder** — implement the change
4. **auditor** — run checks and tests; diagnose failures
5. **scribe** — update documentation to reflect the change

If **auditor** finds failures:

- Code bug → route back to **builder**
- Math inconsistency → route back to **theorist**
- Documentation example fails → route to **scribe**

Repeat until the package passes `devtools::check()` cleanly.

---

## Principles

- Mathematical intent must be separated from software implementation. Any code update affecting a statistical method should begin with a theorist spec.
- Numerical reliability matters. builder must handle NA, Inf, and edge cases as specified by theorist.
- Documentation is not optional. scribe always runs after a successful auditor pass.
- Do not modify unrelated functions. Changes should be surgical.
- Templates live in `templates/`. Use them.

---

## File Layout

```text
RClaw/
├── CLAUDE.md              — this file
├── CONTEXT.md             — points to the active package file
├── packages/
│   ├── _template.md       — copy this to add a new package
│   ├── fect.md            — per-package context (path, tasks, issues)
│   └── ...
├── skills/
│   ├── scout/SKILL.md
│   ├── theorist/SKILL.md
│   ├── builder/SKILL.md
│   ├── auditor/SKILL.md
│   └── scribe/SKILL.md
├── templates/
│   ├── algorithm-spec.md
│   ├── diagnostic-report.md
│   └── tutorial-template.md
├── specs/                 — algorithm specs produced by theorist
└── reports/               — diagnostic reports produced by auditor
```
