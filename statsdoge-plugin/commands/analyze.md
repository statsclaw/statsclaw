---
description: Read this repo (or one tutorial in it) and write statsdoge.md, the validated knowledge document
---

Generate `statsdoge.md` — the StatsDoge knowledge document for this repository
— and validate it against the server. Use the statsdoge-template skill as the
authoritative grammar reference.

Scope argument: `$ARGUMENTS` may name ONE tutorial to focus on — a file path
(`vignettes/05-cfe.Rmd`, `docs/tutorial.md`), a directory, or a topic in plain
language ("the event-study chapter"). If given, the card covers THAT tutorial,
not the whole repo. If empty, cover the repository's main workflow.

Steps:

1. Read `.statsdoge.json` (repo root, then `~/.statsdoge.json`). If neither
   exists, stop and tell the user to run `/statsdoge:setup` first.

2. Study the material seriously before writing:
   - the chosen tutorial file(s) — or, with no argument: README, docs/,
     vignettes/, examples/, and the main source files;
   - enough of the actual code to describe real function names, parameters
     and outputs (never invent APIs).

3. Write `statsdoge.md` at the repository ROOT, strictly following the
   template in the statsdoge-template skill:
   - Card-facing sections (Summary, Description, Inputs, Steps…) stay concise
     and human-readable — key information only, for a statistics / causal
     inference audience. The Description must OPEN with a one-line
     unofficial-showcase attribution linking this repository.
   - `## AI Notes` is the opposite: exhaustive. Parameter tables, defaults,
     edge cases, gotchas, benchmarks, design decisions — everything a future
     AI should learn from this repo. This section never shows on the card.
   - Figures: only real, hot-linkable image URLs (e.g. files served from the
     repo's documentation site). When in doubt, use `- none`.

4. Validate server-side (build the JSON payload with python3 so quoting is
   safe; never echo the key):
   ```bash
   python3 - <<'PY'
   import json, pathlib, urllib.request
   cfg = json.loads((pathlib.Path(".statsdoge.json").read_text()))
   req = urllib.request.Request(
       cfg["base_url"] + "/api/v1/validate",
       data=json.dumps({"content": pathlib.Path("statsdoge.md").read_text()}).encode(),
       headers={"Authorization": "Bearer " + cfg["api_key"],
                "Content-Type": "application/json"}, method="POST")
   print(urllib.request.urlopen(req).read().decode())
   PY
   ```
   If `ok` is false, fix `statsdoge.md` according to each error and re-validate
   (at most 3 rounds). If errors persist, show them verbatim and stop.

5. Report: confirm `statsdoge.md` is written and valid, show its first ~15
   lines as a preview, and suggest `/statsdoge:publish` to upload it.
