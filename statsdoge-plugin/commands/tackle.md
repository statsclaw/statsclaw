---
description: Find the StatsDoge workflow that best fits your goal and run it on the data in this folder
---

Apply a StatsDoge workflow to the data in the current folder. The flow is
deliberately multi-step: find the best-fitting published workflow, INTRODUCE it
and explain why it fits, get the user's confirmation, and only then run it on
the data — all the way to results.

`$ARGUMENTS` is the goal in plain language (e.g. "estimate the treatment effect
of the rollout", "event-study on these panels"). If it is empty, ask the user
what they want to do with the data before continuing.

Steps:

1. Read `.statsdoge.json` (repo root, then `~/.statsdoge.json`). If neither
   exists, stop and point to `/statsdoge:setup`. Never echo the key.

2. Understand the data — locally only. List the files in the folder and read
   just enough to describe the data: file names and formats, and for tabular
   files the column names, types and row counts (read the header and a few rows;
   do NOT load large files fully). This summary stays on the machine — it is
   never sent to the server.

3. Get the catalog of every published workflow. GET `$BASE/api/v1/catalog`
   (python3 + urllib). This is the platform's full table of contents — every
   card's title, slug, one-line summary and tags. Nothing about your data is
   sent; you are just reading the index of what exists.

4. Choose by understanding — not keyword matching. Read the WHOLE catalog
   against the user's goal and the local data shape, and shortlist the 2–5 most
   promising cards using your own judgement (a card can fit even when its wording
   differs from the goal). For a very large catalog you may narrow first with
   POST `$BASE/api/v1/search` `{"query": "<goal>"}`, but the catalog is the
   source of truth.
   - If genuinely nothing on the platform fits, tell the user so and stop;
     suggest the closest topic if there is one.

5. Open their notes and judge. For each shortlisted slug, GET
   `$BASE/api/v1/cards/<slug>/doc` → the card's FULL markdown: Steps (with code),
   Inputs, Input example, and the `## AI Notes` section. These documents ARE your
   notes — read them directly. Narrow to the single best workflow, keeping one or
   two alternatives in mind.

6. Introduce it, then CONFIRM — mandatory; do not run anything before it.
   Present, in plain language:
   - the chosen card's title, one-line summary and `card_url`;
   - why it fits this goal and this data (cite what you read in its notes);
   - what input it expects and what it will produce (the estimand and outputs);
   - the one or two alternatives, a sentence each.
   Then ask with AskUserQuestion: "Run this workflow on your data?" with options
   `Run it` / `Use an alternative` / `Cancel`. If the user picks an alternative,
   switch to it and introduce that one the same way. Only proceed once the user
   chooses Run it.

7. Run it on the data, to the end. Using the chosen card's document (already
   fetched in step 5), execute its Steps in order, adapting the code to the
   actual files and column names in this folder:
   - Map the user's columns to the inputs the method expects; ask only if a
     mapping is genuinely ambiguous.
   - Run each step (R / Python / whatever the card uses) in the folder, and
     install missing packages when you can. If a required runtime or tool is
     missing, say exactly what to install and stop with whatever you have.
   - Use the function names and arguments from the document — never invent an API.
   - Save outputs (tables, figures, a short `statsdoge-results.md`) into the
     folder as you go.

8. Report. Summarise what ran, the key results (estimate(s), and standard error
   or interval if any), the files produced, and link the card (`card_url`).
   Call out any step that was skipped or needs the user's attention.

All API calls use python3 + urllib (no curl/jq quoting pitfalls). The catalog
read (the `cards/<slug>/doc` read is identical — just change the path; the
`search` call adds `method="POST"` with a `{"query": ...}` body):

```bash
python3 <<'PY'
import json, pathlib, urllib.request, urllib.error
p = next((c for c in (pathlib.Path(".statsdoge.json"),
                      pathlib.Path.home() / ".statsdoge.json") if c.exists()), None)
assert p, "Run /statsdoge:setup first."
cfg = json.loads(p.read_text())
req = urllib.request.Request(
    cfg["base_url"] + "/api/v1/catalog",
    headers={"Authorization": "Bearer " + cfg["api_key"]}, method="GET")
try:
    print(urllib.request.urlopen(req).read().decode())
except urllib.error.HTTPError as e:
    print(e.code); print(e.read().decode())
PY
```
