# Shared Skill: Handoff Protocol (Two-Pipeline Architecture)

This protocol governs how work products pass between teammates, mediated by lead, in the two-pipeline architecture.

---

## Core Principle

Teammates never talk to each other directly. Every handoff flows through lead:

```
upstream teammate → output artifact → lead reads → lead dispatches downstream → downstream reads artifact
```

Downstream teammates MUST reuse upstream artifacts. They MUST NOT re-discover or re-derive information that an upstream teammate already produced.

**Pipeline isolation principle**: Lead MUST enforce that code pipeline artifacts never reach the test pipeline, and vice versa. Only skeptic (the convergence point) sees both sides.

---

## Artifact Naming Convention

**ALL artifacts passed between agents MUST use the `.md` (Markdown) file extension.** This is a hard requirement, not a style preference. Markdown ensures artifacts are human-readable, diff-friendly, and renderable on GitHub.

Rules:
- Every handoff artifact is a `.md` file: `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`, `review.md`, `docs.md`, `github.md`, `comprehension.md`, `architecture.md`, `mailbox.md`, `credentials.md`, `status.md`, `request.md`, `impact.md`
- Log entries in `<target-repo>/log/` MUST be `.md` files: `log/<YYYY-MM-DD>-<short-slug>.md`
- Lock files MUST be `.md` files
- No agent may produce a handoff artifact in any other format (no `.txt`, `.json`, `.yaml`, `.html`)

---

## Output Artifacts

Each teammate produces specific output artifacts per run stage:

| Teammate | Artifact(s) | Path | Pipeline |
| --- | --- | --- | --- |
| theorist | `comprehension.md` | `.statsclaw/runs/<request-id>/comprehension.md` | Comprehension record |
| theorist | `spec.md` | `.statsclaw/runs/<request-id>/spec.md` | → Code Pipeline |
| theorist | `test-spec.md` | `.statsclaw/runs/<request-id>/test-spec.md` | → Test Pipeline |
| builder | `implementation.md` | `.statsclaw/runs/<request-id>/implementation.md` | Code Pipeline output |
| auditor | `audit.md` | `.statsclaw/runs/<request-id>/audit.md` | Test Pipeline output |
| scribe | `architecture.md` | `.statsclaw/runs/<request-id>/architecture.md` | Architecture (mandatory) |
| scribe | `log/<date>-<slug>.md` | `<TARGET_REPO>/log/<YYYY-MM-DD>-<short-slug>.md` | Log entry with process record (mandatory, target repo) |
| scribe | `docs.md` | `.statsclaw/runs/<request-id>/docs.md` | Documentation changes |
| skeptic | `review.md` | `.statsclaw/runs/<request-id>/review.md` | Convergence output |
| github | `github.md` | `.statsclaw/runs/<request-id>/github.md` | Externalization output |

---

## Artifact Structure

Every output artifact MUST include these two sections:

### 1. Summary

A concise description of what the teammate did, what files were changed or examined, and any notable decisions made.

### 2. Verdict / Status

A clear status indicator:

| Teammate | Possible Verdicts |
| --- | --- |
| theorist | `SPEC_COMPLETE` — comprehension verified, both specs produced | `HOLD` — needs user input to resolve ambiguity |
| builder | `IMPLEMENTED` — code and unit tests written | `HOLD` — spec unclear or API conflict |
| auditor | `PASS` — all validation checks green | `BLOCK` — validation failed (routes to builder/theorist) |
| scribe | `DOCUMENTED` — docs and architecture diagram produced | `HOLD` — implementation unclear or contradicts spec |
| skeptic | `PASS` / `PASS WITH NOTE` — safe to ship | `STOP` — quality gate failed (routes per table) |
| github | `SHIPPED` — pushed, PR created | `HOLD` — permission or access issue |

---

## Handoff Chain (Two-Pipeline Architecture)

The handoff chain reflects the parallel pipeline structure:

```
theorist
├── spec.md ──────────→ builder (code pipeline)
│                           │
│                           └── implementation.md
│                                      │
└── test-spec.md ─────→ auditor (test pipeline)    │
                            │                      │
                            └── audit.md           │
                                   │               │
                                   ▼               ▼
                                scribe (recording)
                         reads ALL artifacts from both pipelines
                         produces: architecture.md, log/, docs.md
                                   │
                                   ▼
                               skeptic (convergence)
                          reads ALL from both pipelines + scribe output
                                   │
                                   └── review.md
                                          │
                                          ▼
                                       github
```

**Key properties:**
1. Theorist produces TWO artifacts (not one)
2. Builder and auditor receive DIFFERENT artifacts and run IN PARALLEL
3. Neither builder nor auditor sees the other's input or output
4. Scribe is MANDATORY — produces architecture diagram, process-record log entry, and docs
5. Skeptic is the convergence agent that cross-compares both pipelines and scribe's output

---

## Pipeline-Aware Handoff Rules

### Theorist → Builder (Code Pipeline)
- Lead passes: `spec.md`, `request.md`, `impact.md`, `mailbox.md`
- Lead MUST NOT pass: `test-spec.md`

### Theorist → Auditor (Test Pipeline)
- Lead passes: `test-spec.md`, `request.md`, `impact.md`, `mailbox.md`
- Lead MUST NOT pass: `spec.md`

### Builder + Auditor → Scribe (Recording)
- Lead passes: ALL available artifacts — `comprehension.md`, `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`, `request.md`, `impact.md`, `mailbox.md`
- Note: `review.md` does not exist yet (skeptic runs after scribe). If this is a re-run after STOP, `review.md` from the previous cycle may exist.
- Scribe reads everything to produce the process-record log entry, architecture diagram, and docs

### Scribe → Skeptic (Convergence)
- Lead passes: ALL artifacts — `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`, `architecture.md`, `docs.md`, `request.md`, `impact.md`, `mailbox.md`, `comprehension.md`
- Skeptic is the convergence agent that cross-compares both pipelines AND scribe's output

### Skeptic → Github
- Lead passes: `review.md`, `credentials.md`, `implementation.md`, `audit.md`

---

## Lead Mediation Rules

After each teammate returns, lead MUST:

1. **Read the output artifact** in full.
2. **Check the verdict.** If the verdict is `HOLD`, `BLOCK`, or `STOP`, do NOT dispatch the next downstream teammate.
3. **Check the mailbox** for any `HOLD_REQUEST` or `INTERFACE_CHANGE` messages.
4. **Verify pipeline isolation** — confirm no cross-pipeline artifacts were referenced.
5. **Update `status.md`** to reflect the completed stage.
6. **Dispatch the next teammate** with only the artifacts allowed by pipeline rules.

### After Theorist Completes:
- Verify BOTH `spec.md` AND `test-spec.md` exist
- Dispatch builder AND auditor IN PARALLEL in the same message
- Give builder only `spec.md`; give auditor only `test-spec.md`

### After Builder and Auditor Both Complete:
- Read both `implementation.md` and `audit.md`
- Check for BLOCK from auditor (if so, respawn builder with failure details)
- If both succeeded, dispatch scribe with ALL artifacts (scribe produces architecture.md, log entry with process record, and docs.md)
- After scribe completes, dispatch skeptic with ALL artifacts (including scribe's output)

---

## Signal Handling During Handoff

Three signals, three owners, three responses. They never overlap.

### HOLD — Need User Input

**Owner**: theorist, builder, scribe. **Status**: `HOLD`.

1. Lead reads the teammate's output artifact and `mailbox.md` (`HOLD_REQUEST` messages).
2. Lead asks the user the specific question via `AskUserQuestion`.
3. After the user responds, lead re-dispatches the same teammate with the answer.
4. Max 3 HOLD rounds per teammate. After 3, teammate must proceed with stated assumptions or declare the task unspecifiable.

### BLOCK — Validation Failed

**Owner**: auditor (exclusively). **Status**: `BLOCKED`.

1. Lead reads `audit.md` to identify the failure and routing (builder, theorist, or scribe).
2. **Lead respawns the responsible upstream teammate via `Agent` tool** with the failure description from `audit.md`.
   - **Pipeline isolation**: lead may share the failure description (e.g., "function returns wrong value for input X") but MUST NOT share `test-spec.md` itself.
   - **NO DIRECT FIXES**: Lead MUST NOT use Edit, Write, sed, or any tool to modify target repo files — even for seemingly trivial fixes. Always respawn the teammate. Reason: lead cannot run validation and may introduce new bugs.
3. After the teammate fix, lead re-dispatches auditor to re-validate.
4. Max 3 BLOCK→respawn cycles. After 3, escalate to HOLD and ask user.

### STOP — Quality Gate Failed

**Owner**: skeptic (exclusively). **Status**: `STOPPED`.

1. Lead reads `review.md` to identify the concern and routing.
2. Lead respawns the teammate skeptic identifies.
3. After the fix, lead re-runs from the appropriate stage:
   - Builder respawned → re-run auditor → re-run skeptic
   - Theorist respawned → re-run both pipelines from scratch
   - Auditor respawned → re-run auditor → re-run skeptic
4. Max 3 STOP→respawn cycles. After 3, escalate to HOLD and ask user.

---

## Anti-Patterns

- **Cross-pipeline leakage**: Lead passes `test-spec.md` to builder or `spec.md` to auditor. This breaks the adversarial verification model.
- **Re-discovery**: A downstream teammate re-reads the entire codebase instead of using the upstream artifact. This wastes tokens and risks inconsistency.
- **Artifact skipping**: Lead dispatches a teammate without pointing it to required upstream artifacts. The teammate then works from incomplete information.
- **Direct handoff**: Two teammates communicate without lead mediation (e.g., builder writes instructions for auditor inside a code comment). All coordination goes through artifacts and mailbox.
- **Verdict ignoring**: Lead dispatches the next stage despite a `BLOCK` or `STOP` verdict. This violates the safety protocol.
- **Sequential pipeline dispatch**: Lead dispatches builder first, waits for it to complete, then dispatches auditor. This misses the parallel opportunity and may inadvertently leak implementation details.
