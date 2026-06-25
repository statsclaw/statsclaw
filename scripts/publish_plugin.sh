#!/usr/bin/env bash
#
# Publish the statsdoge-plugin/ subfolder to its own lightweight repo, so
# plugin users never clone the full StatsClaw framework. The plugin is the
# StatsDoge publishing client; it lives here as StatsClaw's built-in publish
# command AND is still distributed standalone via this script.
#
# One-time setup: create an EMPTY repo on GitHub named statsdoge-plugin
# (no README), then run:
#
#   bash scripts/publish_plugin.sh git@github.com:TianzhuQin/statsdoge-plugin.git
#
# Re-run the same command after every plugin change to sync it.
#
set -euo pipefail
cd "$(dirname "$0")/.."

REMOTE="${1:-}"
if [ -z "$REMOTE" ]; then
  echo "usage: bash scripts/publish_plugin.sh <git-remote-url>"
  echo "e.g.   bash scripts/publish_plugin.sh git@github.com:TianzhuQin/statsdoge-plugin.git"
  exit 1
fi

if ! git diff --quiet -- statsdoge-plugin; then
  echo "!! uncommitted changes under statsdoge-plugin/ — commit them first."
  exit 1
fi

echo "==> Splitting statsdoge-plugin/ history"
SHA=$(git subtree split --prefix=statsdoge-plugin HEAD)

echo "==> Pushing to $REMOTE (branch main)"
git push -f "$REMOTE" "$SHA:refs/heads/main"

echo "Done. Users install with:"
echo "  /plugin marketplace add TianzhuQin/statsdoge-plugin"
echo "  /plugin install statsdoge@statsdoge"
