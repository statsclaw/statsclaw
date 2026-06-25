---
description: Save your personal StatsDoge API key to this repo
---

Store the user's personal StatsDoge API key so the other plugin commands can
authenticate. The server URL defaults to the live site `https://statsdoge.ai`,
so this command normally only collects the key. (Developers running a local
copy can pass a different base URL — see the arguments below.)

Arguments (optional): `$ARGUMENTS` may contain the API key (a string starting
with `sd_`) and/or a base URL (anything starting with `http`). Use whatever is
provided; ask only for what's missing.

Steps:

1. Determine the two settings:
   - **API key**: if `$ARGUMENTS` contains a token starting with `sd_`, use it.
     Otherwise ask with AskUserQuestion: "Paste your StatsDoge API key
     (Settings → API keys → + New key on the website)." Never echo the full
     key back; refer to it as `sd_…<last 4 chars>`.
   - **Base URL**: if `$ARGUMENTS` contains an `http(s)://…` value, use it
     (strip any trailing slash). Otherwise default to `https://statsdoge.ai`.

2. Write the config to `.statsdoge.json` at the repo root (overwrite if
   present):
   ```json
   {"base_url": "https://statsdoge.ai", "api_key": "sd_…"}
   ```

3. Make sure `.statsdoge.json` is gitignored. If the repo has a `.gitignore`
   without that entry, append a line `.statsdoge.json`. If there is no
   `.gitignore`, create one with that single line. The key must never be
   committed.

4. Verify the key works:
   ```bash
   python3 - <<'PY'
   import json, pathlib, urllib.request
   cfg = json.loads(pathlib.Path(".statsdoge.json").read_text())
   req = urllib.request.Request(
       cfg["base_url"] + "/api/v1/validate",
       data=json.dumps({"content": ""}).encode(),
       headers={"Authorization": "Bearer " + cfg["api_key"],
                "Content-Type": "application/json"}, method="POST")
   try:
       print(urllib.request.urlopen(req).status)
   except urllib.error.HTTPError as e:
       print(e.code)
   PY
   ```
   `200` → key works (empty content is invalid markdown, but auth succeeded).
   `401` → key wrong/expired/deactivated; ask the user to issue a new one.
   Anything else → likely the server is not reachable; tell the user plainly.

5. Confirm: "StatsDoge configured with key sd_…<last4>. Try
   `/statsdoge:analyze` next."
