# Shared Skill: mailbox

Use this skill whenever an agent needs to communicate with another agent without redefining scope or mutating shared state directly.

## Purpose

The mailbox is the shared, append-only coordination surface for Team Lead and teammates.

## Rules

1. Treat `.statsclaw/runs/<request-id>/mailbox.md` as append-only.
2. Add new messages; do not rewrite or delete prior entries.
3. Use the mailbox for:
   - interface changes
   - blockers
   - handoff notes
   - warnings
   - clarification requests routed through `lead`
4. Do not use the mailbox to silently change acceptance criteria or ownership.

## Message Hygiene

- Keep each message to one actionable point.
- Name the affected surface when relevant.
- Include `Lock Impact` when the message affects write ownership or path boundaries.
- Send messages to `lead` when status, ownership, or lock changes are needed.

## Never Do

- mutate `status.md` through mailbox prose
- use mailbox entries as a substitute for required artifacts
- hide breaking interface changes from downstream teammates
