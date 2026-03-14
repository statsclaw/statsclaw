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

## Output Artifacts

Each teammate produces specific output artifacts per run stage:

| Teammate | Artifact(s) | Path | Pipeline |
| --- | --- | --- | --- |
| theorist | `spec.md` | `.statsclaw/runs/<request-id>/spec.md` | → Code Pipeline |
| theorist | `test-spec.md` | `.statsclaw/runs/<request-id>/test-spec.md` | → Test Pipeline |
| builder | `implementation.md` | `.statsclaw/runs/<request-id>/implementation.md` | Code Pipeline output |
| auditor | `audit.md` | `.statsclaw/runs/<request-id>/audit.md` | Test Pipeline output |
| scribe | `architecture.md` | `.statsclaw/runs/<request-id>/architecture.md` | Architecture (mandatory) |
| scribe | `docs.md` | `.statsclaw/runs/<request-id>/docs.md` | Code Pipeline (docs) |
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
| theorist | `SPEC_COMPLETE` (both specs produced), `HOLD` (ambiguity needs user input) |
| builder | `IMPLEMENTED`, `HOLD` (spec unclear or conflict found) |
| auditor | `PASS` (all checks green), `BLOCK` (failures found) |
| scribe | `DOCUMENTED`, `HOLD` (implementation unclear) |
| skeptic | `PASS`, `PASS WITH NOTE`, `STOP` |
| github | `SHIPPED`, `HOLD` (permission or access issue) |

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
                               skeptic (convergence)
                          reads ALL from both pipelines
                                   │
                                   └── review.md
                                          │
                                          ▼
                                       github
```

**Key differences from linear handoff:**
1. Theorist produces TWO artifacts (not one)
2. Builder and auditor receive DIFFERENT artifacts and run IN PARALLEL
3. Neither builder nor auditor sees the other's input or output
4. Skeptic is the FIRST agent to see both pipelines' artifacts together
5. Scribe (if needed) runs from implementation.md, not from both pipelines

---

## Pipeline-Aware Handoff Rules

### Theorist → Builder (Code Pipeline)
- Lead passes: `spec.md`, `request.md`, `impact.md`, `mailbox.md`
- Lead MUST NOT pass: `test-spec.md`

### Theorist → Auditor (Test Pipeline)
- Lead passes: `test-spec.md`, `request.md`, `impact.md`, `mailbox.md`
- Lead MUST NOT pass: `spec.md`

### Builder + Auditor → Skeptic (Convergence)
- Lead passes: ALL artifacts — `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`, `request.md`, `impact.md`, `mailbox.md`, `docs.md` (if exists)
- Skeptic is the ONLY agent that receives artifacts from both pipelines

### Skeptic → Github
- Lead passes: `review.md`, `credentials.md`, `implementation.md`, `audit.md`

---

## Lead Mediation Rules

After each teammate returns, lead MUST:

1. **Read the output artifact** in full.
2. **Check the verdict.** If the verdict is `HOLD`, `BLOCK`, or `STOP`, do NOT dispatch the next downstream teammate.
3. **Check the mailbox** for any `BLOCKER` or `INTERFACE_CHANGE` messages.
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
- If both succeeded, dispatch skeptic with ALL artifacts

---

## Handling Failures

### On BLOCK (raised by auditor)

1. Lead reads `audit.md` to identify the failure.
2. Lead determines the responsible teammate (usually builder, sometimes theorist).
3. Lead respawns the responsible teammate with:
   - The original dispatch context
   - The `audit.md` failure details (exception: auditor routes failures WITHOUT revealing spec.md details)
   - Instructions to fix the specific issue
4. After the respawned teammate completes, lead re-dispatches auditor.
5. **Pipeline isolation during respawn**: When respawning builder due to an auditor BLOCK, lead may share the specific failure description from audit.md (e.g., "function returns wrong value for input X") but MUST NOT share test-spec.md itself.

### On STOP (raised by skeptic)

1. Lead reads `review.md` to identify the concern.
2. Lead determines the responsible teammate per skeptic's routing table.
3. Lead respawns the responsible teammate with the skeptic's concern.
4. After the fix, lead re-runs from the appropriate pipeline stage:
   - If builder is respawned: re-run auditor, then skeptic
   - If theorist is respawned: re-run both pipelines from scratch
   - If auditor is respawned: re-run auditor, then skeptic

### On HOLD (raised by any teammate)

1. Lead reads the artifact to understand the ambiguity.
2. Lead asks the user for clarification.
3. After the user responds, lead respawns the teammate that raised HOLD with the clarification.

---

## Anti-Patterns

- **Cross-pipeline leakage**: Lead passes `test-spec.md` to builder or `spec.md` to auditor. This breaks the adversarial verification model.
- **Re-discovery**: A downstream teammate re-reads the entire codebase instead of using the upstream artifact. This wastes tokens and risks inconsistency.
- **Artifact skipping**: Lead dispatches a teammate without pointing it to required upstream artifacts. The teammate then works from incomplete information.
- **Direct handoff**: Two teammates communicate without lead mediation (e.g., builder writes instructions for auditor inside a code comment). All coordination goes through artifacts and mailbox.
- **Verdict ignoring**: Lead dispatches the next stage despite a `BLOCK` or `STOP` verdict. This violates the safety protocol.
- **Sequential pipeline dispatch**: Lead dispatches builder first, waits for it to complete, then dispatches auditor. This misses the parallel opportunity and may inadvertently leak implementation details.
