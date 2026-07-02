---
name: statsotter-publish
description: How StatsClaw turns a finished package into a StatsOtter card — scriber PRODUCES statsotter.md (at the target repo root) following the card grammar. StatsClaw never uploads and holds no API key; the user publishes with the StatsOtter plugin (natural language, no slash commands). Use when a run requests publishing to StatsOtter.
---

# StatsOtter Publish — the StatsClaw → StatsOtter bridge

This skill defines how a finished StatsClaw package becomes a **card** on
[StatsOtter](https://statsotter.ai).

**StatsClaw only PRODUCES the card document — it never uploads.** StatsClaw holds
no StatsOtter API key: the personal `sd_…` key belongs to the user and is stored
by the **StatsOtter plugin**, not by StatsClaw. StatsClaw also runs inside
worktrees / the workspace repo, where that key isn't available anyway. So the
bridge is a clean two-step hand-off:

- **scriber** *produces* `statsotter.md` at the **target repo root**, following the
  card grammar below.
- **the user** *uploads* it with the **StatsOtter plugin** — the plugin is
  natural-language only (no slash commands): the user just says "publish this
  repo to StatsOtter" in Claude Code. shipper does NOT call any StatsOtter API or
  read any key; it just points the user at that sentence.

It is **opt-in**: it runs only when the user asks to publish to StatsOtter
("publish to statsotter", "make a StatsOtter card", "ship + publish").
When publishing is not requested, scriber does NOT emit `statsotter.md`.

The StatsOtter plugin (distribution repo `TianzhuQin/statsotter-plugin`; source
lives in the statsotter website repo under `statsotter-plugin/`) is the only side
that holds the key and talks to the server. Its publish flow reads `statsotter.md`
from the repo root — exactly where scriber writes it — so the hand-off is
seamless.

---

## Card grammar (the server contract)

The server (`workflows/knowledge.py` → `parse_markdown` / `KNOWN_SECTIONS`) is the
final validator — it runs when the plugin uploads. A document is valid iff ALL
hold:

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
   `\uXXXX`. Do not put raw `##` headings inside section bodies (use `###`+ or bold).

Start from `templates/statsotter-card.md` (a valid skeleton). Card-facing sections
(Summary, Description, Results, Inputs, Steps…) are concise and human-readable;
`## AI Notes` is the exhaustive AI-facing dump.

---

## Producer (scriber)

When the run requests StatsOtter publishing, scriber writes **`statsotter.md` to
the target repo root** — exactly where the StatsOtter plugin's publish flow reads
it — built from the package it just documented:

- Copy `templates/statsotter-card.md` and fill every section from `comprehension.md`,
  `spec.md`, `implementation.md`, `audit.md`, `ARCHITECTURE.md`, and the package's
  own README / docs / public API. Use real function names, parameters and outputs —
  never invent APIs.
- The `## Description` opens with a one-line attribution; adapt it to the package
  (e.g. for a community showcase of someone else's method, credit the authors).
- `## AI Notes` is exhaustive: parameter tables, defaults, edge cases, benchmarks,
  numerical-stability notes, design decisions.
- `## Figures`: only real hot-linkable image URLs (e.g. from the package's docs
  site). When in doubt, `- none`.

scriber does NOT upload and needs NO API key — it only produces the file, following
the card grammar above so the document publishes cleanly when the user uploads it.

---

## Publishing — hand off to the StatsOtter plugin

StatsClaw does not upload. After `statsotter.md` is written, shipper records the
hand-off in `shipper.md`, and the run summary tells the user how to publish:

> `statsotter.md` is ready at the repo root. To publish it as a StatsOtter card:
> - Install the StatsOtter plugin once:
>   `/plugin marketplace add TianzhuQin/statsotter-plugin` then
>   `/plugin install statsotter@statsotter`.
> - Then just say, in plain language: **"publish this repo to StatsOtter"**.
>   The plugin has no slash commands — it asks for your API key on first use
>   (StatsOtter → Settings → API keys → + New key), validates `statsotter.md`,
>   uploads it as a draft card, and can publish it to the public feed right
>   there in the conversation.

**shipper MUST NOT** read `.statsotter.json`, call any `/api/v1/*` endpoint, or
echo a key — none of that lives on the StatsClaw side. The publish hand-off is
non-blocking: it never affects the target repo push, workspace sync, or brain
upload.

The full client-side reference (the JSON API, the duplicate/409 flow, editing an
existing card, the sidebar/taxonomy surface) lives with the plugin in the
statsotter repo under `statsotter-plugin/skills/`. The card grammar above is the
same contract the plugin validates against, so a well-formed `statsotter.md` from
scriber publishes without edits.
