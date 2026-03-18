# Skill: Simplified Workflow (Workflow 10)

A lightweight workflow for small, well-understood changes where the full two-pipeline architecture adds overhead without proportional safety benefit.

---

## When to Offer

Lead MUST evaluate every incoming request against these **smallness criteria** before committing to a full workflow. If ALL of the following are true, lead SHOULD offer the simplified workflow:

| Criterion | Test |
| --- | --- |
| **Few files** | Change touches ≤3 files (estimated during planning) |
| **Low risk** | No algorithmic changes, no numerical methods, no public API changes |
| **Clear scope** | Request is unambiguous — no uploaded files, no papers, no formulas |
| **Well-understood** | The fix/change pattern is routine (typo, config tweak, simple bug fix, dependency bump, adding a parameter, formatting) |
| **No theoretical work** | No mathematical derivation, no statistical methodology, no specification needed |

### Examples of Small Requests

- Fix a typo in a function name or docstring
- Bump a version number in DESCRIPTION/package.json/Cargo.toml
- Add a missing `@export` tag
- Fix a linting error
- Add a simple parameter with a default value
- Update a URL in documentation
- Fix a broken import/require path
- Add `.Rbuildignore` entries

### Examples That Are NOT Small (use full workflow)

- Implement a new estimator or algorithm
- Fix a numerical bug that changes outputs
- Refactor a module's public API
- Any change where the user uploaded reference material (PDFs, papers)
- Changes that affect test outcomes or coverage

---

## How to Offer

When lead detects a small request, it MUST ask the user before proceeding:

```
Lead uses AskUserQuestion with:
  question: "This looks like a small change (≤3 files, routine pattern). Use simplified workflow?"
  options:
    - label: "Simplified (faster)"
      description: "Skip theorist/scribe. Direct: plan → build → validate → ship."
    - label: "Full workflow"
      description: "Run the complete two-pipeline architecture with all teammates."
```

If the user chooses "Full workflow" or provides a custom answer suggesting thoroughness, lead proceeds with the standard workflow (1–9).

If the user chooses "Simplified", lead uses Workflow 10.

**If lead is uncertain** whether the request is small, it MUST ask. The default is always to offer the choice — never silently downgrade to simplified.

---

## Workflow 10: Simplified Pipeline

### Agent Sequence

```
lead → builder → auditor → github?
```

No theorist, no scribe, no skeptic. Lead writes a lightweight spec directly in `request.md` (extended with acceptance criteria).

### State Model (Simplified)

```
CREDENTIALS_VERIFIED → PLANNED → PIPELINES_COMPLETE → REVIEW_PASSED → DONE
```

Skipped states: `SPEC_READY`, `DOCUMENTED`. No `comprehension.md`, `spec.md`, `test-spec.md`, `architecture.md`, `docs.md`, or `review.md` from skeptic.

### Steps

1. **CREDENTIALS** — Same as full workflow (step 4 in CLAUDE.md). Hard gate.
2. **PLAN** — Lead writes `request.md` with:
   - Clear description of the change
   - Acceptance criteria (what "done" looks like)
   - Affected files (the write surface)
   - Expected validation outcome
   Lead writes `impact.md` as in the full workflow. Status → `PLANNED`.
3. **BUILD** — Dispatch builder with `isolation: "worktree"`. Builder receives `request.md` as its spec (no separate `spec.md`). Builder implements and writes `implementation.md`. Status → `PIPELINES_COMPLETE`.
4. **VALIDATE** — Dispatch auditor. Auditor runs profile validation commands and verifies acceptance criteria from `request.md`. Auditor writes `audit.md`. If BLOCK → respawn builder (max 3). Auditor acts as the quality gate (replaces skeptic for simplified workflow).
   - For audit pass: status → `REVIEW_PASSED`.
5. **SHIP** (if requested) — Dispatch github. Status → `DONE`.

### Preconditions (Simplified)

| Target State | Precondition |
| --- | --- |
| `PLANNED` | `request.md` with acceptance criteria AND `impact.md` exist |
| `PIPELINES_COMPLETE` | `implementation.md` exists |
| `REVIEW_PASSED` | `audit.md` exists with verdict PASS |
| `DONE` | `github.md` exists (if ship requested) |

### What Is Skipped

| Component | Reason |
| --- | --- |
| theorist | No theoretical analysis needed for routine changes |
| scribe | No architecture/process-record needed for small changes |
| skeptic | Auditor provides sufficient quality gate |
| `spec.md` / `test-spec.md` | Builder uses `request.md` directly; auditor validates against acceptance criteria |
| `comprehension.md` | No uploaded material to comprehend |
| `architecture.md` | Small change doesn't warrant architecture documentation |
| Log entry | No process record for routine changes |

### Escalation

If at any point during the simplified workflow:
- Builder raises HOLD (spec ambiguity) more than once
- Auditor blocks more than once on the same issue
- The change turns out to affect more files than estimated

Lead MUST escalate to the full workflow. This means:
1. Dispatch theorist with all context accumulated so far
2. Continue from `SPEC_READY` onward using the full pipeline
3. Update `status.md` to reflect the escalation

---

## Progress Bar for Simplified Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress (simplified)                             [2/4] │
│                                                                     │
│  [✔] Plan ── [▶] Implement ── [ ] Validate ── [ ] Ship             │
│                                                                     │
│  ▶ Active: builder implementing changes...                          │
└─────────────────────────────────────────────────────────────────────┘
```

See `skills/progress-bar/SKILL.md` for full progress bar specification.
