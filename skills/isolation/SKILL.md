# Shared Skill: isolation

Use this skill whenever an agent writes files or receives a task with a writable surface.

## Purpose

This skill defines the hard-isolation rules for writing teammates.

## Rules

1. Prefer one worktree per active writing teammate when available.
2. If worktrees are unavailable, use lock-based isolation under `.statsclaw/runs/<request-id>/locks/`.
3. Never write outside the task's `Assigned write paths`.
4. Never write a path covered by another active lock.
5. Only `lead` may create, transfer, or release locks.

## Writer Protocol

- Read the task record before editing.
- Confirm the required lock exists.
- Stay inside the assigned surface.
- If the task surface is incomplete, message `lead` instead of expanding it yourself.

## Never Do

- overlap writable surfaces between active teammates
- grab an implicit lock by editing first
- expand a task from code into docs or docs into code without a new assignment
