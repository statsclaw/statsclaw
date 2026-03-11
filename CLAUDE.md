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

RClaw operates through six specialists. Each has a `skills/<name>/SKILL.md` that describes their triggers, tools, workflow, and output format.

| Name | Role |
| --- | --- |
| **scout** | Maps the package: structure, exports, dependencies, affected files |
| **theorist** | Formalizes mathematical or algorithmic specifications |
| **builder** | Implements and modifies R functions from specs |
| **auditor** | Runs `devtools::check()`, tests, and examples; diagnoses failures |
| **scribe** | Updates `.Rd` documentation, vignettes, and tutorials |
| **skeptic** | Adversarial quality gate: challenges tests, refactors, and artifacts before any commit; issues STOP or PASS |

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
| "stop", "wait", "hold on", "are we sure", "is this right", "before we commit", "review this" | skeptic |

For a **full method request** (adding a new method end-to-end), invoke all six in sequence:

```text
scout → theorist → builder → auditor → skeptic → scribe
```

---

## Safety Protocol

Any skill may raise a **HOLD** or a **BLOCK** at any point in the pipeline.

**HOLD** — raised by theorist or builder before proceeding:

- The pipeline pauses immediately.
- The skill states the concern in one or two sentences.
- Present the concern to the user and wait for explicit instruction. Do not resolve it by making a "best guess."

**BLOCK** — raised by auditor:

- The pipeline stops. Scribe does not run.
- The block persists until the underlying issue is resolved and auditor re-runs cleanly.

**Conditions that require a HOLD:**

| Raised by | Condition |
| --- | --- |
| theorist | Math is ambiguous or underspecified — interpretation would require invention |
| theorist | Source material does not support an identification assumption that the request implies |
| theorist | Notation conflicts or symbols are overloaded in ways that affect computation |
| builder | Spec conflicts with existing package API or calling conventions |
| builder | Implementation requires an undocumented judgment call that would affect results |
| builder | Requested change would silently break a downstream function |

**Conditions that require a BLOCK:**

| Raised by | Condition |
| --- | --- |
| auditor | Any ERROR in `devtools::check()` or `devtools::test()` |
| auditor | Numerical results are implausible given the method (even if tests formally pass) |
| auditor | Test suite passes trivially — structure-only checks with no correctness assertions |

**Conditions that require a STOP (skeptic):**

| Condition |
| --- |
| A changed code path has no test coverage |
| Tests are structural-only with no correctness assertions, and the risk is non-trivial |
| `devtools::check(args = '--as-cran')` was not run after a structural refactor |
| Tutorial was not re-rendered after any code change |
| Memory or skill files contain inaccuracies or contradict the actual repo state |
| Commit message omits a meaningful change |

A HOLD, BLOCK, or STOP is not a failure. It is the skill doing its job correctly.

---

## Pipeline

For any non-trivial code change:

1. **scout** — identify affected files and existing related functions
2. **theorist** — formalize the spec; raise HOLD if underspecified; sign off explicitly when complete
3. **builder** — challenge the spec before implementing; raise HOLD if conflicts exist; implement
4. **auditor** — run checks, tests, and numerical diagnostics (cross-referencing the spec); raise BLOCK on any failure or implausible result; route math inconsistencies back to theorist
5. **skeptic** — review the diff adversarially before any commit; challenge test coverage, refactor correctness, documentation freshness, and artifact accuracy; issue STOP or PASS
6. **scribe** — update documentation; flag any contradiction between docs and spec

If **auditor** raises a BLOCK:

- Code bug → route back to **builder**
- Math inconsistency → route back to **theorist**
- Documentation example fails → route to **scribe**

If **skeptic** raises a STOP:

- Missing tests → route back to **builder**
- Auditor checks incomplete → route back to **auditor**
- Docs stale → route to **scribe**
- Memory or skills inaccurate → fix in place before committing the RClaw repo

Repeat until auditor passes cleanly and skeptic issues a PASS.

---

## Principles

- Mathematical intent must be separated from software implementation. Any code update affecting a statistical method should begin with a theorist spec.
- Numerical reliability matters. builder must handle NA, Inf, and edge cases as specified by theorist.
- Documentation is not optional. scribe always runs after a successful auditor pass.
- Do not modify unrelated functions. Changes should be surgical.
- Templates live in `templates/`. Use them.
- Skills have independent judgment. A skill that raises a HOLD or BLOCK is not blocking progress — it is preventing a worse outcome.

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
│   ├── scribe/SKILL.md
│   └── skeptic/SKILL.md
├── templates/
│   ├── algorithm-spec.md
│   ├── diagnostic-report.md
│   └── tutorial-template.md
├── specs/                 — algorithm specs produced by theorist
└── reports/               — diagnostic reports produced by auditor
```
