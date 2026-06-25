# StatsDoge Publish — the StatsClaw → StatsDoge bridge

This skill defines how a finished StatsClaw package becomes a **card** on
[StatsDoge](https://statsdoge.ai). It is the single source of truth for two
teammates:

- **scriber** *produces* the knowledge document `statsdoge.md` (run directory),
  following the card grammar below.
- **shipper** *publishes* it: validate → import against the StatsDoge JSON API.

It is **opt-in**. It runs only when the user asks to publish to StatsDoge
("publish to statsdoge", "发布成卡片", "make a StatsDoge card", "ship + publish")
AND a StatsDoge API key is configured (see Config). When publishing is not
requested, scriber does NOT emit `statsdoge.md` and shipper skips the publish
step entirely.

The same publishing client also ships as a standalone Claude Code plugin under
`statsdoge-plugin/` (commands `/statsdoge:setup|analyze|publish|modify|list|delete`)
for users who want to publish a repository without running a full StatsClaw
workflow. The grammar and API below are identical for both paths.

---

## Config (`.statsdoge.json`)

Auth + endpoint live in `.statsdoge.json` — repo root first, then `~/.statsdoge.json`:

```json
{"base_url": "https://statsdoge.ai", "api_key": "sd_…"}
```

- `base_url` is configurable (default `https://statsdoge.ai`) for local / self-hosted
  servers — never hard-code the host.
- `api_key` is a personal key from **StatsDoge → Settings → API keys → + New key**.
  **Never echo the full key**; refer to it as `sd_…<last4>`.
- If neither config exists, publishing cannot proceed: tell the user to run
  `/statsdoge:setup sd_…` (the plugin) or create `.statsdoge.json` by hand, then
  continue. This is a HOLD-style pause, not a hard failure of the run.

`.statsdoge.json` MUST be gitignored — it holds a secret. The plugin's
`/statsdoge:setup` adds the gitignore entry automatically.

---

## Card grammar (the server contract)

The server (`workflows/knowledge.py` → `parse_markdown` / `KNOWN_SECTIONS`) is the
final validator. A document is valid iff ALL hold:

1. Exactly one H1 `# <title>` before any `##` section. No prose may appear before
   the first `##` section (it parses as "content before the first section" = error).
2. Only these H2 sections, each at most once (any other `## X` is an error):
   `Summary, Metadata, Description, Results, Inputs, Input example, Figures, Steps, AI Notes`
3. `## Summary` is required and non-empty (1–3 plain sentences for the card).
4. `## Metadata` holds only these bullets (`-` for an empty value):
   `- Source: <url or ->`, `- Tags: A, B` (2–4 Title-Case identification-strategy
   tags), `- Cover: <image url or ->`.
5. `## Figures`: lines `- https://… | one-sentence caption`, or `- none`. Only real,
   hot-linkable image URLs; the first figure becomes the cover when no Cover is set.
6. `## Steps` is required with 1–10 blocks. Each block starts `### N. <stage> — <name>`
   where `<stage>` ∈ `prep, diagnostic, estimation, inference, robustness,
   heterogeneity, reporting, other`. Inside a block (all optional): `- URL: …`,
   `- Note: …` (what happens AND why), `- Formula: <KaTeX, no $ delimiters>`, and at
   most one fenced code block.
7. `## AI Notes`: exhaustive free markdown — everything a future AI should learn.
   Never shown on the card.
8. Body math uses `$…$` / `$$…$$`. Write real Unicode (×, –, α) — never literal
   `\uXXXX`. Do not put raw `## ` headings inside section bodies (use `###`+ or bold).

Start from `templates/statsdoge-card.md` (a valid skeleton). Card-facing sections
(Summary, Description, Results, Inputs, Steps…) are concise and human-readable;
`## AI Notes` is the exhaustive AI-facing dump.

---

## Producer (scriber)

When the run requests StatsDoge publishing, scriber writes **`statsdoge.md` to the
run directory** (NOT the target repo root — keep the target repo clean), built from
the package it just documented:

- Copy `templates/statsdoge-card.md` and fill every section from `comprehension.md`,
  `spec.md`, `implementation.md`, `audit.md`, `ARCHITECTURE.md`, and the package's
  own README / docs / public API. Use real function names, parameters and outputs —
  never invent APIs.
- The `## Description` opens with a one-line attribution; adapt it to the package
  (e.g. for a community showcase of someone else's method, credit the authors).
- `## AI Notes` is exhaustive: parameter tables, defaults, edge cases, benchmarks,
  numerical-stability notes, design decisions.
- `## Figures`: only real hot-linkable image URLs (e.g. from the package's docs
  site). When in doubt, `- none`.

scriber does NOT upload — it only produces the file. shipper publishes it.

---

## Publisher (shipper)

After workspace sync / brain upload, if `statsdoge.md` exists in the run directory
and publishing was requested:

1. **Load config** (`.statsdoge.json`, repo root then `~`). Missing → record in
   `shipper.md` and skip (non-blocking).
2. **Validate** — `POST {base_url}/api/v1/validate` with `{content}`.
   Errors → print them verbatim, record in `shipper.md`, and STOP publishing
   (do NOT import an invalid document). This is non-blocking for the rest of the run.
3. **Import** — `POST {base_url}/api/v1/imports` with
   `{content, repo: <target git remote URL or "">}` (no `target_slug` → the server
   always CREATES a new draft card). Handle by status:
   - **401** → bad/expired key; tell the user to re-run `/statsdoge:setup`.
   - **400** `{errors}` → print verbatim.
   - **409** `{duplicate:{title, slug, url, reason, is_yours}}` → a similar card
     exists. Report it; suggest `/statsdoge:modify <slug>` to update it instead, or
     re-send with `"force": true` only on explicit user consent.
   - **200** → success. Record `card_url`, `session_url`, `doc_url`, and `is_draft`.
     Remind the user a new card is a **draft** — it reaches the public feed only after
     they press **Publish** on the `session_url` page.
4. **Record** all of the above in `shipper.md` under a "StatsDoge publish" section.

Publishing is **non-blocking**: a publish failure MUST NOT undo or block the target
repo push, workspace sync, or brain upload.

Use python3 + urllib (no curl/jq quoting pitfalls). Reads `statsdoge.md` from the
run directory:

```bash
python3 - "$RUN_DIR/statsdoge.md" "$TARGET_REMOTE_URL" <<'PY'
import json, pathlib, sys, urllib.request, urllib.error
md_path, repo = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
cfg_path = next((p for p in (pathlib.Path(".statsdoge.json"),
                             pathlib.Path.home()/".statsdoge.json") if p.exists()), None)
assert cfg_path, "No .statsdoge.json — run /statsdoge:setup first."
cfg = json.loads(cfg_path.read_text())
content = pathlib.Path(md_path).read_text()
def call(path, payload):
    req = urllib.request.Request(cfg["base_url"] + path,
        data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + cfg["api_key"],
                 "Content-Type": "application/json"}, method="POST")
    try:
        return 200, urllib.request.urlopen(req).read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
code, body = call("/api/v1/validate", {"content": content})
print("validate", code, body)
v = json.loads(body) if code == 200 else {}
if v.get("ok"):
    code, body = call("/api/v1/imports", {"content": content, "repo": repo})
    print("import", code, body)
PY
```

---

## JSON API reference

| Endpoint | Body / params | Success | Errors |
|---|---|---|---|
| `POST /api/v1/validate` | `{content}` | `{ok, errors[], title}` | 401 bad key |
| `POST /api/v1/imports` | `{content, repo?, target_slug?, force?}` | `{ok, action: created\|updated, card_url, session_url, doc_url, is_draft, markdown}` | 400 `{errors}` · 404 (target not yours) · 409 `{duplicate}` · 401 |
| `GET /api/v1/cards` | — | `{ok, count, cards:[…]}` | 401 |
| `DELETE /api/v1/cards/<slug>` | — | `{ok, deleted}` | 404 not yours · 401 |

The publish flow never sends `target_slug` (always create). The modify flow
(`/statsdoge:modify`) sends `target_slug` to update a card in place. The success
`markdown` is the canonical regenerated document. See `statsdoge-plugin/skills/
statsdoge-template/SKILL.md` for the full plugin-side reference.
