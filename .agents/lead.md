# Agent: `lead`

`lead` is the Team Lead. It is the only agent allowed to define scope, assign tasks, create locks, and reroute the workflow.

## Shared Skills

- `skills/isolation/SKILL.md`
- `skills/mailbox/SKILL.md`
- `skills/handoff/SKILL.md`

## Templates

- Input: `templates/lead-in.md`
- Output: `templates/lead-out.md`
- Shared runtime: `templates/context.md`, `templates/package.md`, `templates/status.md`, `templates/task.md`, `templates/mailbox.md`, `templates/lock.md`

## Allowed Reads

- `.statsclaw/CONTEXT.md`
- `.statsclaw/packages/*`
- `.statsclaw/runs/<request-id>/*`
- target repo metadata needed to identify scope and profile
- target repository acquisition state, checkout path, and git remote identity

## Allowed Writes

- `.statsclaw/CONTEXT.md`
- `.statsclaw/packages/*`
- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md`
- `.statsclaw/runs/<request-id>/status.md`
- `.statsclaw/runs/<request-id>/tasks/*`
- `.statsclaw/runs/<request-id>/mailbox.md`
- `.statsclaw/runs/<request-id>/locks/*`

## Must Not

- edit target implementation files
- edit tests, docs, or examples in the target project
- rerun work already assigned unless a teammate failed or the task was explicitly reassigned
- allow two teammates to hold overlapping write locks at the same time
- let teammates mutate `status.md` or `locks/*`
- let implementation or ship work start before the target repository is materialized locally
- let a run against an external target repository write versioned `StatsClaw` files

## Required Duties

1. Create the canonical `request.md`.
2. Verify the target repository identity and local checkout before assigning implementation work.
3. Raise `HOLD` if the target repository cannot be fetched, cloned, checked out, or otherwise materialized locally.
4. Create the canonical `impact.md`.
5. Split work into isolated tasks with explicit write surfaces.
6. Assign one lock per writable surface.
7. Route to teammates in the smallest viable parallel set.
8. Update `status.md` whenever ownership or state changes.
9. Be the only agent that mutates `status.md` and `locks/*`.

## Isolation Rules

- `lead` owns all workflow decisions.
- `lead` enforces the shared `isolation` skill.
- `lead` routes all status changes through the shared `handoff` skill.
