---
description: Validate statsdoge.md and PUBLISH it as a NEW card (suggests /statsdoge:modify on a duplicate)
---

Publish the repository's knowledge document as a **new card**. This command
never silently updates an existing card; if the server detects a similar one,
the plugin suggests `/statsdoge:modify` and lets the user override only after
explicit confirmation.

Steps:

1. Read `.statsdoge.json` (repo root, then `~/.statsdoge.json`); if missing,
   stop and point to `/statsdoge:setup`. Never echo the key.

2. If `statsdoge.md` does not exist at the repo root, offer to run
   `/statsdoge:analyze` first; if the user declines, stop.

3. **Always validate first** (the file may be ours or hand-written):
   POST `$BASE/api/v1/validate` with `{content}` (python3 + urllib).
   - Invalid → print every error verbatim, one per line, and STOP.
   - Valid → show the parsed title and the `## Summary` line, then ask the
     user (AskUserQuestion: "Publish as a NEW card?", options
     `Publish / Cancel`).

4. Upload — get the git remote with `git remote get-url origin` (omit on
   error) and POST `$BASE/api/v1/imports` with
   `{"content": <file text>, "repo": <git remote URL or "">}`.
   The absence of `target_slug` tells the server: ALWAYS create a new card.

5. Handle by status code:
   - **401** → bad key. Point to `/statsdoge:setup`.
   - **400** `{errors:[…]}` → print them.
   - **409** `{duplicate:{title, slug, url, reason, is_yours}}` → a similar
     card already exists. Show its title and URL and the reason. Ask the user
     with AskUserQuestion:
       - "Modify the existing card instead (recommended)" → run
         `/statsdoge:modify <duplicate.slug>` (or stop and tell the user that
         is the next step if you cannot chain).
       - "It is genuinely different — publish as a separate new card anyway"
         → resend the same payload plus `"force": true`.
       - "Cancel".
     When `is_yours` is true, lead with: "This is one of your own cards
     (`<slug>`); modify it instead of creating a duplicate."
   - **200** → success. Report clearly:
       * "Created a new draft card."
       * Three labelled links:
           Card preview → `card_url`
           My imports (chat-refine & publish) → `session_url`
           Knowledge doc (web editor, version history) → `doc_url`
       * If `is_draft` is true (it should be), remind: the card goes to the
         public feed only after pressing **Publish** on the My-imports session
         page.

6. The server returns the canonical `markdown` (regenerated from the saved
   card). Ask whether to overwrite the local `statsdoge.md` with it (so local
   == server). Do what the user chooses. Offer to save it elsewhere too if
   they prefer.
