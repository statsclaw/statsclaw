---
description: List the cards under your StatsDoge account
---

List every card belonging to the configured account.

1. Read `.statsdoge.json` (repo root, then `~/.statsdoge.json`); if missing,
   stop and point to `/statsdoge:setup`.

2. GET `$BASE/api/v1/cards` with the Bearer key (python3 + urllib; never echo
   the key). 401 → bad key, point to `/statsdoge:setup`.

3. Render the result as a compact markdown table, newest first:

   | Title | Status | Versions | Updated | Links |
   |---|---|---|---|---|
   | … | draft / published | doc_versions | YYYY-MM-DD | [card](card_url) · [doc](doc_url) |

   Below the table, mention the total count and that `/statsdoge:delete
   <slug>` removes one (the slug is the last path segment of card_url; include
   the slug for each row somewhere visible, e.g. under the title in the same
   cell as `slug-name`).

4. If the account has no cards, say so and suggest `/statsdoge:analyze` +
   `/statsdoge:publish`.
