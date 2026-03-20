# Lock Record

Lock ID: [lock-id]  
Request ID: [request-id]  
Owner: [leader / planner / builder / scriber / tester / reviewer / shipper]  
Status: [held / released]

## Surface

- Assigned write paths:
  - `[path or glob]`

## Rules

- No other teammate may write these paths while the lock is held.
- `leader` is the only agent allowed to create, transfer, or release locks.
- Locks should be as narrow as possible while still preventing conflicts.
