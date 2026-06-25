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

3. Search the platform. POST `$BASE/api/v1/search` with `{"query": "<the user's
   goal>"}` (python3 + urllib). ONLY the goal text leaves the machine. The
   response ranks published cards, each with a `brief` (summary, inputs,
   results, steps).
   - If `cards` is empty, tell the user the platform has nothing matching yet
     and stop. Suggest the closest topic if there is one.

4. Pick the best fit. Read each candidate `brief` against the user's goal and
   the local data shape, and choose the single best workflow. Keep one or two
   alternatives in mind.

5. Introduce it, then CONFIRM — mandatory; do not run anything before it.
   Present, in plain language:
   - the chosen card's title, one-line summary and `card_url`;
   - why it fits this goal and this data;
   - what input it expects and what it will produce (the estimand and outputs);
   - the one or two alternatives, a sentence each.
   Then ask with AskUserQuestion: "Run this workflow on your data?" with options
   `Run it` / `Use an alternative` / `Cancel`. If the user picks an alternative,
   switch to it and introduce that one the same way. Only proceed once the user
   chooses Run it.

6. Fetch the recipe. GET `$BASE/api/v1/cards/<slug>/doc` → the full knowledge
   document: Steps (with code), Inputs, Input example, and the `## AI Notes`
   section. Read the AI Notes carefully — they hold the parameters, defaults and
   gotchas you need to run the method correctly.

7. Run it on the data, to the end. Execute the Steps in order, adapting the
   card's code to the actual files and column names in this folder:
   - Map the user's columns to the inputs the method expects; ask only if a
     mapping is genuinely ambiguous.
   - Run each step (R / Python / whatever the card uses) in the folder, and
     install missing packages when you can. If a required runtime or tool is
     missing, say exactly what to install and stop with whatever you have.
   - Use the function names and arguments from the doc — never invent an API.
   - Save outputs (tables, figures, a short `statsdoge-results.md`) into the
     folder as you go.

8. Report. Summarise what ran, the key results (estimate(s), and standard error
   or interval if any), the files produced, and link the card (`card_url`).
   Call out any step that was skipped or needs the user's attention.

All API calls use python3 + urllib (no curl/jq quoting pitfalls). The search
call:

```bash
python3 - "<goal text>" <<'PY'
import json, pathlib, sys, urllib.request, urllib.error
p = next((c for c in (pathlib.Path(".statsdoge.json"),
                      pathlib.Path.home() / ".statsdoge.json") if c.exists()), None)
assert p, "Run /statsdoge:setup first."
cfg = json.loads(p.read_text())
req = urllib.request.Request(
    cfg["base_url"] + "/api/v1/search",
    data=json.dumps({"query": sys.argv[1]}).encode(),
    headers={"Authorization": "Bearer " + cfg["api_key"],
             "Content-Type": "application/json"}, method="POST")
try:
    print(urllib.request.urlopen(req).read().decode())
except urllib.error.HTTPError as e:
    print(e.code); print(e.read().decode())
PY
```

Fetch a chosen card's full document the same way with a GET to
`$BASE/api/v1/cards/<slug>/doc` (use method "GET" and the same Authorization
header; no request body).
