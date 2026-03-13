# Shared Skill: handoff

Use this skill whenever an agent finishes a stage or needs another agent to continue.

## Purpose

This skill standardizes how teammates hand work back to `lead` and downstream agents.

## Rules

1. Write the stage artifact first.
2. Add a concise mailbox message naming:
   - what is finished
   - what changed
   - who should act next
3. Ask `lead` to update `status.md`; teammates do not mutate status directly.
4. If the result is blocked, state:
   - blocking reason
   - responsible next owner
   - whether locks must change

## Handoff Checklist

- artifact written
- mailbox message appended
- unresolved risks called out
- next owner named
- status change requested from `lead`

## Never Do

- finish a task without an artifact
- silently assume the next teammate will notice an interface change
- change workflow ownership without `lead`
