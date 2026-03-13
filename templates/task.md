# Task Record

Task ID: [task-id]  
Request ID: [request-id]  
Owner: [lead / theorist / builder / scribe / auditor / skeptic / github]  
Layer: [Control / Planning / Production / Assurance / Externalization]  
Status: [queued / in_progress / blocked / completed / cancelled]

## Goal

[What this worker is expected to accomplish.]

## Required Inputs

- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md` [if relevant]
- `.statsclaw/runs/<request-id>/mailbox.md`
- [other required artifact]

## Expected Output

- `.statsclaw/runs/<request-id>/[artifact].md`

## Isolation

- Assigned write paths:
  - `[path or glob]`
- Required locks:
  - `.statsclaw/runs/<request-id>/locks/[lock-file].md`

## Constraints

- [ownership rule]
- [scope limit]

## Handoff

- Next owner: [agent]
- Success state: [PLANNED / SPEC_READY / IMPLEMENTED / VALIDATED / DOCUMENTED / REVIEW_PASSED / READY_TO_SHIP / DONE]
