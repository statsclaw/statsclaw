# Shared Skill: Handoff Protocol

This protocol governs how work products pass between teammates, mediated by lead.

---

## Core Principle

Teammates never talk to each other directly. Every handoff flows through lead:

```
upstream teammate → output artifact → lead reads → lead dispatches downstream → downstream reads artifact
```

Downstream teammates MUST reuse upstream artifacts. They MUST NOT re-discover or re-derive information that an upstream teammate already produced.

---

## Output Artifacts

Each teammate produces exactly **one** output artifact per run stage:

| Teammate | Artifact | Path |
| --- | --- | --- |
| theorist | `spec.md` | `.statsclaw/runs/<request-id>/spec.md` |
| builder | `implementation.md` | `.statsclaw/runs/<request-id>/implementation.md` |
| auditor | `audit.md` | `.statsclaw/runs/<request-id>/audit.md` |
| scribe | `docs.md` | `.statsclaw/runs/<request-id>/docs.md` |
| skeptic | `review.md` | `.statsclaw/runs/<request-id>/review.md` |
| github | `github.md` | `.statsclaw/runs/<request-id>/github.md` |

---

## Artifact Structure

Every output artifact MUST include these two sections:

### 1. Summary

A concise description of what the teammate did, what files were changed or examined, and any notable decisions made.

### 2. Verdict / Status

A clear status indicator:

| Teammate | Possible Verdicts |
| --- | --- |
| theorist | `SPEC_COMPLETE`, `HOLD` (ambiguity needs user input) |
| builder | `IMPLEMENTED`, `HOLD` (spec unclear or conflict found) |
| auditor | `PASS` (all checks green), `BLOCK` (failures found) |
| scribe | `DOCUMENTED`, `HOLD` (implementation unclear) |
| skeptic | `PASS`, `PASS WITH NOTE`, `STOP` |
| github | `SHIPPED`, `HOLD` (permission or access issue) |

---

## Handoff Chain

The default handoff chain for a full workflow:

```
theorist (spec.md)
    ↓
builder (implementation.md)   ←  reads spec.md
    ↓
auditor (audit.md)            ←  reads implementation.md
    ↓
scribe (docs.md)              ←  reads implementation.md, audit.md
    ↓
skeptic (review.md)           ←  reads ALL upstream artifacts
    ↓
github (github.md)            ←  reads review.md
```

Not every stage is required. Lead determines which stages are needed based on the request and records them in `impact.md`.

---

## Lead Mediation Rules

After each teammate returns, lead MUST:

1. **Read the output artifact** in full.
2. **Check the verdict.** If the verdict is `HOLD`, `BLOCK`, or `STOP`, do NOT dispatch the next downstream teammate.
3. **Check the mailbox** for any `BLOCKER` or `INTERFACE_CHANGE` messages.
4. **Update `status.md`** to reflect the completed stage.
5. **Dispatch the next teammate** with all required context, including:
   - Paths to upstream artifacts the teammate needs to read
   - Any mailbox messages relevant to the teammate's work
   - The specific task and write surface

---

## Handling Failures

### On BLOCK (raised by auditor)

1. Lead reads `audit.md` to identify the failure.
2. Lead determines the responsible teammate (usually builder, sometimes theorist or scribe).
3. Lead respawns the responsible teammate with:
   - The original dispatch context
   - The `audit.md` failure details
   - Instructions to fix the specific issue
4. After the respawned teammate completes, lead re-dispatches auditor.

### On STOP (raised by skeptic)

1. Lead reads `review.md` to identify the concern.
2. Lead determines the responsible teammate.
3. Lead respawns the responsible teammate with the skeptic's concern.
4. After the fix, lead re-runs the chain from auditor onward (auditor, then skeptic again).

### On HOLD (raised by any teammate)

1. Lead reads the artifact to understand the ambiguity.
2. Lead asks the user for clarification.
3. After the user responds, lead respawns the teammate that raised HOLD with the clarification.

---

## Anti-Patterns

- **Re-discovery**: A downstream teammate re-reads the entire codebase instead of using the upstream artifact. This wastes tokens and risks inconsistency.
- **Artifact skipping**: Lead dispatches a teammate without pointing it to required upstream artifacts. The teammate then works from incomplete information.
- **Direct handoff**: Two teammates communicate without lead mediation (e.g., builder writes instructions for auditor inside a code comment). All coordination goes through artifacts and mailbox.
- **Verdict ignoring**: Lead dispatches the next stage despite a `BLOCK` or `STOP` verdict. This violates the safety protocol.
