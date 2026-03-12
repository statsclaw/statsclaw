# StatsClaw — Compatibility Context

This file is a compatibility pointer for environments that expect a repo-root `CONTEXT.md`.

StatsClaw runtime state lives under `.statsclaw/`, not in the versioned framework repository.

```yaml
Active: .statsclaw/CONTEXT.md
```

Next steps:

1. Open StatsClaw in Claude Code
2. Tell Claude the target project path and your request
3. StatsClaw will auto-create `.statsclaw/` as needed
