# Shared Skill: Attribution — Commit Co-Author Trailers

Commits pushed by the shipper agent include a `Co-authored-by` trailer that credits both the user and StatsClaw. This follows the standard Git trailer convention recognized by GitHub, which displays co-authors on the commit page.

---

## Default Behavior

Every commit to the **target repository** includes:

```
Co-authored-by: StatsClaw <statsclaw@users.noreply.github.com>
```

The user remains the primary author (determined by git config `user.name` / `user.email`). The trailer is appended after the commit body, separated by a blank line.

Workspace repo commits (sync operations) do NOT include this trailer.

---

## Configuration

The `CommitTrailers` field in `context.md` controls attribution:

```yaml
CommitTrailers: "statsclaw"   # co-author trailers appended to commits; set to "" to disable
```

| Value | Behavior |
| --- | --- |
| `"statsclaw"` (default) | Append `Co-authored-by: StatsClaw <statsclaw@users.noreply.github.com>` |
| `""` | No trailer — commits attributed to user only |

To disable, edit `context.md` in the workspace repo and set `CommitTrailers: ""`.

---

## Scope

- **Applies to**: target repo commits made by shipper (code changes, ARCHITECTURE.md, user-facing docs)
- **Does not apply to**: workspace repo sync commits, workspace CHANGELOG/HANDOFF updates
- **Does not apply to**: PR descriptions, issue comments, or any non-commit artifact

---

## Implementation Notes

- Shipper reads `context.md` during startup (step 10 of startup checklist)
- If `context.md` is missing or `CommitTrailers` field is absent, default to `"statsclaw"` (include trailer)
- The trailer is placed after the commit body, following a blank line, per Git convention
- GitHub automatically parses `Co-authored-by` trailers and shows co-authors on the commit page
