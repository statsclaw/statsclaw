---
description: Update one of your existing cards from statsdoge.md (pick which card to overwrite)
---

Update an EXISTING card under the user's account with the contents of
`statsdoge.md`. The user picks which card — never silent.

`$ARGUMENTS` may identify the target card: a slug (preferred) or a fragment
of the title. Optional.

Steps:

1. Read `.statsdoge.json` (repo root, then `~/.statsdoge.json`); if missing,
   stop and point to `/statsdoge:setup`.

2. If `statsdoge.md` is missing at the repo root, stop and tell the user to
   write it (or run `/statsdoge:analyze`).

3. List the user's cards: GET `$BASE/api/v1/cards` (python3 + urllib).
   - 401 → bad key, point to `/statsdoge:setup`.
   - Empty list → tell the user they have no cards yet and suggest
     `/statsdoge:publish` to create one.

4. Resolve the target:
   - If `$ARGUMENTS` is a slug that matches one of the returned `cards[].slug`
     exactly, use it.
   - Else case-insensitive substring match against `cards[].title`. If
     ambiguous (more than one hit) or none, show the full table and ask the
     user with AskUserQuestion which one to modify (options = the matched
     titles, plus Cancel).
   - No argument → show the table and ask.

5. Validate `statsdoge.md`: POST `$BASE/api/v1/validate` with `{content}`.
   - Invalid → print errors verbatim, STOP. Do not upload.
   - Valid → show the new title and `## Summary` line. If the document's
     title differs from the chosen card's title, mention that explicitly:
     "This will rename `<old>` → `<new>`." Ask the user to confirm the
     update (AskUserQuestion: "Update `<old slug>` with this content?",
     options `Update / Cancel`).

6. Upload: POST `$BASE/api/v1/imports` with
   `{"content": <file text>, "target_slug": "<chosen slug>"}`.
   - 401 → setup.
   - 400 → print errors.
   - 404 → the slug is no longer yours (deleted? regenerated?); refresh the
     list and ask again.
   - 200 → success. Report:
       * "Updated `<title>` — saved as knowledge-doc version N+1."
       * Links: Card preview, My imports session, Knowledge doc.
       * If `is_draft` is true, mention how to publish from My imports.

7. Offer to overwrite the local `statsdoge.md` with the server's canonical
   regenerated markdown (`markdown` field of the response), so local stays in
   sync with the saved card.
