# Shared Skill: Mailbox Communication Protocol

This protocol governs how teammates communicate with each other and with leader through the shared mailbox during a run.

---

## Location

The mailbox for each run lives at:

```
.repos/workspace/<repo-name>/runs/<request-id>/mailbox.md
```

Leader creates this file when the run starts. If it does not exist when a teammate needs to write, the teammate creates it.

---

## Append-Only Rule

The mailbox is **append-only**. Teammates may only add new messages to the end of the file. They MUST NOT:

- Delete existing messages
- Edit existing messages
- Reorder messages
- Overwrite the file

This ensures a reliable audit trail of cross-teammate communication.

---

## Message Format

Each message follows this exact format:

```markdown
---
**Timestamp:** YYYY-MM-DD HH:MM UTC
**From:** <agent-name>
**Type:** INFO | HOLD_REQUEST | INTERFACE_CHANGE
**Subject:** <one-line summary>

<message body — as concise as possible>
```

### Message Types

| Type | Meaning | Action Required |
| --- | --- | --- |
| `INFO` | Non-blocking observation or note for downstream teammates | Leader reads and forwards if relevant |
| `HOLD_REQUEST` | The sender cannot continue without user input — corresponds to a HOLD signal | Leader must ask the user the specific question before dispatching downstream work |
| `INTERFACE_CHANGE` | A function signature, file path, export, or API surface changed in a way that affects other teammates | Leader must notify affected downstream teammates in their dispatch prompt |

### Relationship to Workflow Signals

Mailbox message types are **not** workflow signals. They are communication records. The mapping:

| Mailbox Type | Corresponding Signal | Who Acts |
| --- | --- | --- |
| `HOLD_REQUEST` | HOLD (raised by the teammate) | Leader asks user, re-dispatches teammate |
| `INFO` | (none — no signal raised) | Leader reads and optionally forwards |
| `INTERFACE_CHANGE` | (none — no signal raised) | Leader includes in downstream dispatch |

Note: BLOCK and STOP are NOT mailbox types. They are verdicts written directly in `audit.md` (BLOCK) and `review.md` (STOP). The mailbox is for inter-teammate communication, not for verdict delivery.

---

## When to Use the Mailbox

Teammates SHOULD write to the mailbox when:

- They need user input to continue (type: `HOLD_REQUEST`)
- They change a function signature, file name, or export that downstream teammates depend on (type: `INTERFACE_CHANGE`)
- They discover an upstream artifact is incomplete but can work around it (type: `INFO`)
- They make a judgment call not covered by the spec and want to document it for reviewer (type: `INFO`)
- They notice an out-of-scope issue for a future run (type: `INFO`)

Teammates SHOULD NOT use the mailbox for:

- Routine progress updates (the output artifact covers this)
- Duplicating information already in their output artifact
- Communicating directly with the user (only leader talks to the user)
- Delivering BLOCK or STOP verdicts (those go in audit.md and review.md)

---

## Leader Responsibilities

After each teammate completes, leader MUST:

1. Read the teammate's output artifact.
2. Read `mailbox.md` for any new messages since the last check.
3. If a `HOLD_REQUEST` message exists, forward the question to the user via `AskUserQuestion` before dispatching downstream work.
4. If an `INTERFACE_CHANGE` message exists, include the change details in the dispatch prompt for any affected downstream teammate.
5. If an `INFO` message is relevant to downstream work, summarize it in the next dispatch prompt.

---

## Example

```markdown
---
**Timestamp:** 2026-03-13 14:22 UTC
**From:** builder
**Type:** INTERFACE_CHANGE
**Subject:** Renamed `calc_stats()` to `compute_statistics()`

The function `calc_stats()` in `src/stats.R` was renamed to `compute_statistics()` to match the naming convention used elsewhere in the package. All internal callers have been updated. Scriber should update any documentation or examples that reference the old name.

---
**Timestamp:** 2026-03-13 14:45 UTC
**From:** planner
**Type:** HOLD_REQUEST
**Subject:** Undefined symbol in equation (3)

In equation (3) of the uploaded PDF, the symbol $\hat\Sigma$ is used but never defined. Is this: (a) the sample covariance matrix $X'X/N$, (b) the residual covariance $\hat{e}\hat{e}'/N$, or (c) something else? Its dimension ($N \times N$ vs $T \times T$) also needs clarification.
```
