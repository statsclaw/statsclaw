# Team Mailbox

Request ID: [request-id]

Append-only: teammates add new messages at the end. Never edit or delete existing entries.

## Message Format

```markdown
---
**Timestamp:** YYYY-MM-DD HH:MM UTC
**From:** <agent-name>
**Type:** INFO | HOLD_REQUEST | INTERFACE_CHANGE
**Subject:** <one-line summary>

<message body — as concise as possible>
```

| Type | Meaning |
| --- | --- |
| `INFO` | Non-blocking observation or note for downstream teammates |
| `HOLD_REQUEST` | Cannot continue without user input — corresponds to HOLD signal |
| `INTERFACE_CHANGE` | Function signature, file path, or API surface changed |

## Messages

_No messages yet._
