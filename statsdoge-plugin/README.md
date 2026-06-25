# StatsDoge Claude Code plugin

Turn any code repository — or a single tutorial inside it — into a StatsDoge
card, or apply a published workflow to your own data — all without leaving
Claude Code. The plugin drives the whole loop:

```
/statsdoge:setup     save your personal API key (once)
/statsdoge:analyze   read the repo (or one tutorial) → write statsdoge.md → validate
/statsdoge:publish   validate → confirm → upload as a NEW card (duplicate detector
                     suggests /statsdoge:modify on a hit)
/statsdoge:modify    pick one of your cards → overwrite it with statsdoge.md
/statsdoge:list      every card under your account
/statsdoge:delete    permanently remove one of your cards

/statsdoge:apply     find the workflow that fits your goal → run it on your data
```

## Install

From the lightweight distribution repo (recommended — it contains only this
plugin, not the website codebase):

```
/plugin marketplace add TianzhuQin/statsdoge-plugin
/plugin install statsdoge@statsdoge
```

For local development, point Claude Code straight at the folder:

```
claude --plugin-dir /path/to/statsclaw/statsdoge-plugin
```

(Maintainers: sync this folder to the distribution repo with
`bash scripts/publish_plugin.sh git@github.com:TianzhuQin/statsdoge-plugin.git`.)

## First run

1. On the website: **Settings → API keys → + New key** (label it, pick an
   expiry, copy the `sd_…` key — it is shown once).
2. In your repo: `/statsdoge:setup sd_…`
   The key is stored in `.statsdoge.json` (gitignored automatically). The
   server defaults to `https://statsdoge.ai`; pass a different `http(s)://`
   URL to `/statsdoge:setup` only if you run a local copy.
3. `/statsdoge:analyze vignettes/05-cfe.Rmd` — or no argument to cover the
   whole repo. Claude writes `statsdoge.md` at the repo root and validates it
   against the server's strict template.
4. `/statsdoge:publish` — after your confirmation a **new draft card** is
   created and appears under *My imports* on the site. Already have a similar
   card? The server returns 409 and the plugin suggests `/statsdoge:modify
   <slug>` to update it instead — or you can override and create a separate
   new card.

5. `/statsdoge:modify [<slug or title>]` — pick one of your existing cards
   and replace its contents with the current `statsdoge.md` (recorded as a
   new knowledge-doc version on that card). The plugin lists your cards if
   you do not name one.

## The statsdoge.md contract

`statsdoge.md` at the repo root is the single source of truth. Hand-written
or generated, it must pass the strict template (H1 title; fixed `##` sections;
`### N. stage — name` steps; an `## AI Notes` section that holds every detail
for the AI and never appears on the card). `/statsdoge:publish` always
validates first and reports precise, line-level errors instead of uploading
anything malformed. Edit the file → `/statsdoge:publish` again → the website
card updates, with full version history kept server-side.

## Troubleshooting

- **401** — key wrong, expired or deactivated: generate a new one on the site
  and re-run `/statsdoge:setup`.
- **409 duplicate** — the server found a similar existing card; open it, or
  confirm "It's different" to force the upload.
- **Validation errors** — fix `statsdoge.md` per the listed lines; the
  statsdoge-template skill in this plugin contains the full grammar and a
  worked example.
