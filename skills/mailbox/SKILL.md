# Shared Skill: Mailbox Communication Protocol

This protocol governs how teammates communicate with each other and with lead through the shared mailbox during a run.

---

## Location

The mailbox for each run lives at:

```
.statsclaw/runs/<request-id>/mailbox.md
```

Lead creates this file when the run starts. If it does not exist when a teammate needs to write, the teammate creates it.

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
**Type:** INFO | BLOCKER | INTERFACE_CHANGE
**Subject:** <one-line summary>

<message body — as concise as possible>
```

### Message Types

| Type | Meaning | Action Required |
| --- | --- | --- |
| `INFO` | Non-blocking observation or note for downstream teammates | Lead reads and forwards if relevant |
| `BLOCKER` | The sender cannot continue without resolution | Lead must address before dispatching downstream work |
| `INTERFACE_CHANGE` | A function signature, file path, export, or API surface changed in a way that affects other teammates | Lead must notify affected downstream teammates in their dispatch prompt |

---

## When to Use the Mailbox

Teammates SHOULD write to the mailbox when:

- They discover that an upstream artifact is incomplete or ambiguous but can work around it
- They change a function signature, file name, or export that downstream teammates depend on
- They encounter a blocker that prevents completing their assigned task
- They make a judgment call not covered by the spec and want to document it for the skeptic
- They notice an out-of-scope issue that should be addressed in a future run

Teammates SHOULD NOT use the mailbox for:

- Routine progress updates (the output artifact covers this)
- Duplicating information already in their output artifact
- Communicating directly with the user (only lead talks to the user)

---

## Lead Responsibilities

After each teammate completes, lead MUST:

1. Read the teammate's output artifact.
2. Read `mailbox.md` for any new messages since the last check.
3. If a `BLOCKER` message exists, address it before dispatching the next teammate.
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

The function `calc_stats()` in `src/stats.R` was renamed to `compute_statistics()` to match the naming convention used elsewhere in the package. All internal callers have been updated. Scribe should update any documentation or examples that reference the old name.

---
**Timestamp:** 2026-03-13 14:45 UTC
**From:** auditor
**Type:** BLOCKER
**Subject:** Test suite requires fixture file not present in repo

`tests/test_regression.py` references `fixtures/sample_data.csv` which does not exist. Cannot run validation suite. Builder needs to either create the fixture or update the test.
```
