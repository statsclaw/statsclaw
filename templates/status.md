# Run Status

Request ID: [request-id]  
Package: [package-name]  
Current State: [state]  
Current Owner: [agent]  
Next Step: [action]  
Active Profile: [profile]  
Target Repository: [owner/repo or local path]  
Target Checkout: [absolute path or unavailable]  
Last Updated: [YYYY-MM-DD HH:MM]

## Ownership Ledger

- Layer: [Control / Planning / Production / Assurance / Externalization]
- Authority: [which artifact or agent currently owns the next decision]

## Active Isolation

- Held locks:
  - `[lock-id]`
- Current write owner:
  - `[agent or none]`

## Open Risks

- [risk]

## Blocking Reason

[optional]

## Repo Boundary

- Framework repository may receive:
  - `.statsclaw/` runtime artifacts only
- Target repository may receive:
  - `[code/docs/tests/ship actions or none]`

## Persistence Rule

This file must be updated after every completed stage and every `HOLD`, `BLOCKED`, or `STOPPED` transition.
