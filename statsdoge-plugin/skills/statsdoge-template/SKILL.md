---
name: statsdoge-template
description: The StatsDoge knowledge-document grammar (statsdoge.md) and the JSON API reference. Use when generating, validating, fixing or uploading a StatsDoge card from a repository.
---

# StatsDoge knowledge document — grammar & API

A StatsDoge **card** is the human-facing page (concise, key information only).
The **knowledge document** (`statsdoge.md`) is the AI-facing source of truth:
it contains everything the card shows PLUS an `## AI Notes` section with every
detail worth learning. The server parses this file deterministically — the
grammar below is strict, and the server is the final validator
(`POST /api/v1/validate`).

## Grammar (a document is valid iff ALL hold)

1. Exactly one H1 `# <title>` before any section. The title is the card title
   — specific, not clickbait, ideally "What the recipe does (PackageName)".
2. Only these H2 sections, each at most once (unknown `## X` = error):
   `Summary, Metadata, Description, Inputs, Input example, Figures, Steps, AI Notes`
3. `## Summary` is required and non-empty: 1–3 plain sentences for the card.
4. `## Metadata` holds only these bullets (`-` for an empty value):
   - `- Source: <url or ->`
   - `- Tags: A, B, C`  (2–4 Title-Case tags naming the identification
     strategy, e.g. DiD, Event Study, Synthetic Control — not the software)
   - `- Cover: <image url or ->`
5. `## Figures`: lines `- https://… | one-sentence caption`, or `- none`.
   Only real, hot-linkable image URLs. The first figure becomes the cover
   when no Cover is set.
6. `## Steps` is required with 1–10 blocks. Each block starts
   `### N. <stage> — <name>` where `<stage>` is one of:
   `prep, diagnostic, estimation, inference, robustness, heterogeneity, reporting, other`
   Inside a block (all optional): `- URL: …`, `- Note: …` (1–2 sentences,
   what happens AND why it matters), `- Formula: <KaTeX, no $ delimiters>`,
   and at most one fenced code block in the tutorial's own language.
7. `## AI Notes`: free markdown, as long as useful. Never shown on the card.
8. Math in prose uses `$…$` / `$$…$$` (the site renders KaTeX). Write real
   Unicode characters (×, –, α) — never literal `\uXXXX` escapes.
9. Markdown bodies must not contain raw `## ` headings (use `###`+ or bold);
   level-2 headings are reserved for the section grammar.

## Worked example

```markdown
# Honest sensitivity bounds for parallel trends (HonestDiD)

## Summary
One factual sentence (or a short paragraph) shown under the title.

## Metadata
- Source: https://github.com/asheshrambachan/HonestDiD
- Tags: DiD, Event Study
- Cover: https://docs.package.org/figure.png

## Description
> ⚠️ *Unofficial community showcase of [HonestDiD](https://…). All credit to the authors.*

The big picture, in markdown. Inline math $\tau$ and display math:
$$Y_{it}^{0} = \alpha_i + \xi_t + e_{it}$$

## Inputs
What goes in: data shape, the question. Markdown.

## Input example
```text
id,t,y,d
1,2018,3.4,0
```

## Figures
- https://docs.package.org/fig1.png | Event-study estimates with honest CIs.

## Steps

### 1. prep — Load the panel
- URL: https://docs.package.org/reference/load.html
- Note: One or two sentences on what happens and why it matters.
- Formula: \hat\tau = \bar Y_1 - \bar Y_0

```r
df <- read.csv("panel.csv")
```

### 2. estimation — Event-study regression
- Note: Steps repeat this shape; URL / Formula / code are each optional.

## AI Notes
Everything else an AI should know — full parameter tables, defaults, edge
cases, benchmarks, design decisions, quotes from the docs. Never on the card.
```

## JSON API (Bearer auth: `Authorization: Bearer sd_…`)

Config lives in `.statsdoge.json` (repo root; fallback `~/.statsdoge.json`):
`{"base_url": "https://statsdoge.ai", "api_key": "sd_…"}`. Never print the key.

| Endpoint | Body / params | Success | Errors |
|---|---|---|---|
| `POST /api/v1/validate` | `{content}` | `{ok, errors[], title}` | 401 bad key |
| `POST /api/v1/imports` | `{content, repo?, target_slug?, force?}` | `{ok, action: created\|updated, card_url, session_url, doc_url, is_draft, markdown}` | 400 `{errors}` · 404 (target not yours) · 409 `{duplicate:{title,slug,url,reason,is_yours}}` · 401 |
| `GET /api/v1/cards` | — | `{ok, count, cards:[{title, slug, card_url, doc_url, is_draft, updated_at, doc_versions}]}` | 401 |
| `DELETE /api/v1/cards/<slug>` | — | `{ok, deleted}` | 404 not yours · 401 |

Semantics worth remembering:
- The publish flow (`/statsdoge:publish`) NEVER sends `target_slug` → the
  server always tries to CREATE a new card. If a similar card exists (the
  user's own OR somebody else's), the server returns 409 with the duplicate's
  slug/url/`is_yours` flag so the plugin can suggest `/statsdoge:modify`. The
  upload only proceeds after the user explicitly sends `"force": true`.
- The modify flow (`/statsdoge:modify`) sends `"target_slug": "<slug>"` →
  the server updates THAT card in place. 404 if the slug is not owned by the
  requester (no cross-author edits via the plugin).
- The success response's `markdown` is the canonical regenerated document —
  offer to overwrite the local file with it so local == server.
- New cards are drafts (`is_draft: true`): the public feed shows them only
  after the user presses Publish on the `session_url` page.

Use python3 + urllib for all requests (no jq/curl quoting pitfalls):

```bash
python3 - <<'PY'
import json, pathlib, sys, urllib.request, urllib.error
cfg_path = next((p for p in (pathlib.Path(".statsdoge.json"),
                             pathlib.Path.home()/".statsdoge.json") if p.exists()), None)
assert cfg_path, "Run /statsdoge:setup first."
cfg = json.loads(cfg_path.read_text())
payload = {"content": pathlib.Path("statsdoge.md").read_text()}
req = urllib.request.Request(cfg["base_url"] + "/api/v1/imports",
    data=json.dumps(payload).encode(),
    headers={"Authorization": "Bearer " + cfg["api_key"],
             "Content-Type": "application/json"}, method="POST")
try:
    print(urllib.request.urlopen(req).read().decode())
except urllib.error.HTTPError as e:
    print(e.code); print(e.read().decode())
PY
```
