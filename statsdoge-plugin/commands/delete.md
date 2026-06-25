---
description: Delete one of your StatsDoge cards (irreversible)
---

Delete a card from the configured account. `$ARGUMENTS` should identify the
card — a slug (preferred) or a title fragment.

1. Read `.statsdoge.json` (repo root, then `~/.statsdoge.json`); if missing,
   stop and point to `/statsdoge:setup`.

2. Resolve the target: GET `$BASE/api/v1/cards` and match `$ARGUMENTS`
   against slugs first, then titles (case-insensitive substring). No
   argument → show the list and ask which one. Multiple matches → list them
   and ask the user to pick.

3. Confirm explicitly before deleting (AskUserQuestion). State the card's
   exact title and that deletion is **permanent**: steps, votes, comments and
   every knowledge-doc version go with it; linked imports are marked
   discarded. Options: Delete permanently / Cancel.

4. On confirmation: `DELETE $BASE/api/v1/cards/<slug>` with the Bearer key
   (python3 + urllib, method="DELETE").
   - 404 → no such card under this account (maybe already deleted).
   - 401 → bad key → `/statsdoge:setup`.
   - 200 → report: `Deleted "<title>".`

5. If the repo's `statsdoge.md` was the source of that card, mention the file
   is still on disk locally — re-publishing it would recreate the card.
