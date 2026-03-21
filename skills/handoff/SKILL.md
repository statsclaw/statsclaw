# Shared Skill: Handoff Protocol (Two-Pipeline Architecture)

This protocol governs how work products pass between teammates, mediated by leader, in the two-pipeline architecture.

---

## Core Principle

Teammates never talk to each other directly. Every handoff flows through leader:

```
upstream teammate → output artifact → leader reads → leader dispatches downstream → downstream reads artifact
```

Downstream teammates MUST reuse upstream artifacts. They MUST NOT re-discover or re-derive information that an upstream teammate already produced.

**Pipeline isolation principle**: Leader MUST enforce that code pipeline artifacts never reach the test pipeline, and vice versa. Only reviewer (the convergence point) sees both sides.

---

## Artifact Naming Convention

**ALL artifacts passed between agents MUST use the `.md` (Markdown) file extension.** This is a hard requirement, not a style preference. Markdown ensures artifacts are human-readable, diff-friendly, and renderable on GitHub.

Rules:
- Every handoff artifact is a `.md` file: `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`, `review.md`, `docs.md`, `shipper.md`, `comprehension.md`, `Architecture.md`, `mailbox.md`, `credentials.md`, `status.md`, `request.md`, `impact.md`
- Log entries in the run directory MUST be `.md` files: `log-entry.md` (with a `<!-- filename: YYYY-MM-DD-slug.md -->` header for workspace `runs/` naming)
- Lock files MUST be `.md` files
- No agent may produce a handoff artifact in any other format (no `.txt`, `.json`, `.yaml`, `.html`)

---

## Output Artifacts

Each teammate produces specific output artifacts per run stage:

| Teammate | Artifact(s) | Path | Pipeline |
| --- | --- | --- | --- |
| planner | `comprehension.md` | `.repos/workspace/<repo-name>/runs/<request-id>/comprehension.md` | Comprehension record |
| planner | `spec.md` | `.repos/workspace/<repo-name>/runs/<request-id>/spec.md` | → Code Pipeline |
| planner | `test-spec.md` | `.repos/workspace/<repo-name>/runs/<request-id>/test-spec.md` | → Test Pipeline |
| builder | `implementation.md` | `.repos/workspace/<repo-name>/runs/<request-id>/implementation.md` | Code Pipeline output |
| tester | `audit.md` | `.repos/workspace/<repo-name>/runs/<request-id>/audit.md` | Test Pipeline output |
| scriber | `Architecture.md` | `<target-repo>/Architecture.md` + `.repos/workspace/<repo-name>/runs/<request-id>/Architecture.md` | Architecture (mandatory; target repo root is primary, run dir copy for reviewer) |
| scriber | `log-entry.md` | `.repos/workspace/<repo-name>/runs/<request-id>/log-entry.md` | Log entry with process record (mandatory; synced to workspace `runs/` by shipper) |
| scriber | `docs.md` | `.repos/workspace/<repo-name>/runs/<request-id>/docs.md` | Documentation changes (synced to workspace `<repo-name>/docs.md` by shipper) |
| reviewer | `review.md` | `.repos/workspace/<repo-name>/runs/<request-id>/review.md` | Convergence output |
| shipper | `shipper.md` | `.repos/workspace/<repo-name>/runs/<request-id>/shipper.md` | Externalization output |

---

## Artifact Structure

Every output artifact MUST include these two sections:

### 1. Summary

A concise description of what the teammate did, what files were changed or examined, and any notable decisions made.

### 2. Verdict / Status

A clear status indicator:

| Teammate | Possible Verdicts |
| --- | --- |
| planner | `SPEC_READY` — comprehension verified, both specs produced | `HOLD` — needs user input to resolve ambiguity |
| builder | `IMPLEMENTED` — code and unit tests written | `HOLD` — spec unclear or API conflict |
| tester | `PASS` — all validation checks green | `BLOCK` — validation failed (routes to builder/scriber/planner) |
| scriber (recording mode) | `DOCUMENTED` — recording artifacts produced | `HOLD` — implementation unclear or contradicts spec |
| scriber (implementer mode) | `IMPLEMENTED` + `DOCUMENTED` — docs written and recorded | `HOLD` — spec unclear or contradicts existing docs |
| reviewer | `PASS` / `PASS WITH NOTE` — safe to ship | `STOP` — quality gate failed (routes per table) |
| shipper | `SHIPPED` — pushed, PR created | `HOLD` — permission or access issue |

---

## Handoff Chain

### Code Workflows (1, 2, 4, 5)

```
planner
├── spec.md ──────────→ builder (code pipeline)
│                           │
│                           └── implementation.md
│                                      │
└── test-spec.md ─────→ tester (test pipeline)    │
                            │                      │
                            └── audit.md           │
                                   │               │
                                   ▼               ▼
                                scriber (recording)
                         reads ALL artifacts from both pipelines
                         produces: Architecture.md (target repo root + run dir), log-entry.md, docs.md (run dir → workspace)
                                   │
                                   ▼
                               reviewer (convergence)
                                   │
                                   ▼
                                shipper
```

### Docs-Only Workflow (3)

```
planner
└── spec.md ──────────→ scriber (implementer + scriber)
                            │
                            ├── documentation changes
                            ├── implementation.md
                            ├── Architecture.md (target repo root + run dir), log-entry.md, docs.md (run dir → workspace)
                            │
                            ▼
                        reviewer (convergence)
                            │
                            ▼
                         shipper
```

**Key properties:**
1. Planner produces specs (only `spec.md` is used in docs-only; `test-spec.md` is unused)
2. **Code workflows**: builder ∥ tester in parallel, then scriber records
3. **Docs-only**: scriber replaces builder as implementer. No tester — docs don't need testing. Reviewer reviews directly.
4. Scriber is MANDATORY — the single owner of all documentation and recording
5. Reviewer is the convergence agent that cross-compares all outputs

---

## Pipeline-Aware Handoff Rules

### Code Workflows (1, 2, 4, 5)

**Planner → Builder (Code Pipeline)**
- Leader passes: `spec.md`, `request.md`, `impact.md`, `mailbox.md`
- Leader MUST NOT pass: `test-spec.md`

**Planner → Tester (Test Pipeline)**
- Leader passes: `test-spec.md`, `request.md`, `impact.md`, `mailbox.md`
- Leader MUST NOT pass: `spec.md`

**Builder + Tester → Scriber (Recording)**
- Leader passes: ALL available artifacts — `comprehension.md`, `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`, `request.md`, `impact.md`, `mailbox.md`
- Scriber reads everything to produce the process-record log entry, architecture diagram, and docs

### Docs-Only Workflow (3)

**Planner → Scriber (Implementer + Scriber)**
- Leader passes: `spec.md`, `request.md`, `impact.md`, `mailbox.md`, `comprehension.md`
- Scriber receives `spec.md` as the implementer (replaces builder). Implements documentation AND produces recording artifacts.
- No tester is dispatched — docs don't need testing. Reviewer reviews directly after scriber.

### All Workflows

**→ Reviewer (Convergence)**
- Leader passes: ALL artifacts — `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`, `Architecture.md`, `docs.md`, `request.md`, `impact.md`, `mailbox.md`, `comprehension.md`
- Reviewer is the convergence agent that cross-compares both pipelines AND scriber's output

**Reviewer → Shipper**
- Leader passes: `review.md`, `credentials.md`, `implementation.md`, `audit.md`

---

## Leader Mediation Rules

After each teammate returns, leader MUST:

1. **Read the output artifact** in full.
2. **Check the verdict.** If the verdict is `HOLD`, `BLOCK`, or `STOP`, do NOT dispatch the next downstream teammate.
3. **Check the mailbox** for any `HOLD_REQUEST` or `INTERFACE_CHANGE` messages.
4. **Verify pipeline isolation** — confirm no cross-pipeline artifacts were referenced.
5. **Update `status.md`** to reflect the completed stage.
6. **Dispatch the next teammate** with only the artifacts allowed by pipeline rules.

### After Planner Completes:
- Verify `spec.md` exists (and `test-spec.md` for code workflows)
- **Code workflows**: Dispatch builder AND tester IN PARALLEL in the same message. Give builder only `spec.md`; give tester only `test-spec.md`.
- **Docs-only workflow**: Dispatch scriber with `spec.md` (as implementer). After scriber completes, dispatch reviewer directly.

### After Builder and Tester Both Complete (Code Workflows):
- Read `implementation.md` and `audit.md`
- Check for BLOCK from tester (if so, respawn builder with failure details)
- If both succeeded, dispatch scriber for recording with ALL artifacts. After scriber completes, dispatch reviewer.

---

## Signal Handling During Handoff

Three signals, three owners, three responses. They never overlap.

### HOLD — Need User Input

**Owner**: planner, builder, scriber. **Status**: `HOLD`.

1. Leader reads the teammate's output artifact and `mailbox.md` (`HOLD_REQUEST` messages).
2. Leader asks the user the specific question via `AskUserQuestion`.
3. After the user responds, leader re-dispatches the same teammate with the answer.
4. Max 3 HOLD rounds per teammate. After 3, teammate must proceed with stated assumptions or declare the task unspecifiable.

### BLOCK — Validation Failed

**Owner**: tester (exclusively). **Status**: `BLOCKED`.

1. Leader reads `audit.md` to identify the failure and routing (builder, planner, or scriber).
2. **Leader respawns the responsible upstream teammate via `Agent` tool** with the failure description from `audit.md`.
   - **Pipeline isolation**: leader may share the failure description (e.g., "function returns wrong value for input X") but MUST NOT share `test-spec.md` itself.
   - **NO DIRECT FIXES**: Leader MUST NOT use Edit, Write, sed, or any tool to modify target repo files — even for seemingly trivial fixes. Always respawn the teammate. Reason: leader cannot run validation and may introduce new bugs.
3. After the teammate fix, leader re-dispatches tester to re-validate.
4. Max 3 BLOCK→respawn cycles. After 3, escalate to HOLD and ask user.

### STOP — Quality Gate Failed

**Owner**: reviewer (exclusively). **Status**: `STOPPED`.

1. Leader reads `review.md` to identify the concern and routing.
2. Leader respawns the teammate reviewer identifies.
3. After the fix, leader re-runs from the appropriate stage:
   - Builder respawned → re-run tester → re-run reviewer
   - Planner respawned → re-run both pipelines from scratch
   - Tester respawned → re-run tester → re-run reviewer
4. Max 3 STOP→respawn cycles. After 3, escalate to HOLD and ask user.

---

## Anti-Patterns

- **Cross-pipeline leakage**: Leader passes `test-spec.md` to builder or `spec.md` to tester. This breaks the adversarial verification model.
- **Re-discovery**: A downstream teammate re-reads the entire codebase instead of using the upstream artifact. This wastes tokens and risks inconsistency.
- **Artifact skipping**: Leader dispatches a teammate without pointing it to required upstream artifacts. The teammate then works from incomplete information.
- **Direct handoff**: Two teammates communicate without leader mediation (e.g., builder writes instructions for tester inside a code comment). All coordination goes through artifacts and mailbox.
- **Verdict ignoring**: Leader dispatches the next stage despite a `BLOCK` or `STOP` verdict. This violates the safety protocol.
- **Sequential pipeline dispatch**: Leader dispatches builder first, waits for it to complete, then dispatches tester. This misses the parallel opportunity and may inadvertently leak implementation details.
