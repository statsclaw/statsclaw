## What does this PR do?

<!-- Briefly describe the change -->

## Related issues

<!-- Link to related issues: Fixes #123, Relates to #456 -->

## Type of change

- [ ] Bug fix
- [ ] New feature / enhancement
- [ ] New language profile
- [ ] New skill
- [ ] Agent definition (`agents/`)
- [ ] Template or brain-entry schema (`templates/`)
- [ ] Dispatch / wrapper script (`scripts/`) — *Codex distribution only*
- [ ] Slash command prompt (`prompts/`) — *Codex distribution only*
- [ ] Installer (`install.sh` / `uninstall.sh` / `codex-config.example.toml`) — *Codex distribution only*
- [ ] Documentation
- [ ] Cross-distribution sync (mirroring a change between `statsclaw/statsclaw` and `statsclaw/statsclaw-codex`)
- [ ] Brain system (knowledge sharing, distiller, privacy scrub)
- [ ] Other: <!-- describe -->

## Checklist

- [ ] I've read the [Contributing Guide](../CONTRIBUTING.md)
- [ ] Changes are focused on a single concern
- [ ] I've tested with **Claude Code or Codex CLI** (whichever this repo targets)
- [ ] Existing functionality is not broken
- [ ] If this touches a file that is **shared across both distributions** (agents, skills, profiles, templates, brain-entry schemas), I've either opened a paired PR on the other repo or flagged the cross-repo implication so a maintainer can mirror it
- [ ] If this is a Codex-side port of a Claude Code change, I've re-applied the Codex primitive substitutions (`Agent` → `scripts/dispatch.sh`, `AskUserQuestion` → numbered-options markdown, `Skill` tool → file reference, `${CLAUDE_PLUGIN_ROOT}` → `${STATSCLAW_CODEX_ROOT}`)
