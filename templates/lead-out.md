# Lead Output

Use this template to define what `lead` must produce after planning and routing.

## Required Outputs

- `.statsclaw/packages/<package>.md`
- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md`
- `.statsclaw/runs/<request-id>/status.md`
- `.statsclaw/runs/<request-id>/tasks/*.md`
- `.statsclaw/runs/<request-id>/mailbox.md`
- `.statsclaw/runs/<request-id>/locks/*.md` when write isolation is needed

## Required Content

- package context when missing or stale
- canonical request contract
- authoritative impact map
- teammate assignments
- non-overlapping write surfaces
- lock ownership
- next owner and next step

## Success Condition

Downstream teammates can start without re-scoping the request or rediscovering the repo surface.
