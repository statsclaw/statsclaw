---
name: attribution
description: "Commit authorship policy — no co-author trailers, user is sole author"
user-invocable: false
disable-model-invocation: true
---
# Shared Skill: Attribution — Commit Authorship Policy

StatsClaw commits are attributed to the **user alone**. Shipper MUST NOT append any co-author trailer, tooling footer, or bot attribution to commit messages.

---

## Policy

Every commit produced by shipper — in the target repo, the workspace repo, or any brain-seedbank fork — uses a clean message with **no** trailers of the following forms:

- `Co-authored-by: StatsClaw <...StatsClaw-Shipper@users.noreply.github.com>`
- `Co-authored-by: Claude <noreply@anthropic.com>` (or any other `Co-authored-by:` line)
- `Generated with Claude Code` footer
- `https://claude.ai/code/session_...` URL
- Any other tool-attribution line

The git author and committer are the user, as determined by their local `user.name` / `user.email` config. Shipper does NOT pass `--author`, set `GIT_AUTHOR_*` / `GIT_COMMITTER_*`, or configure a bot identity.

---

## Rationale

- The user is the only person responsible for the change.
- GitHub's contributor list is driven by commit author/committer + `Co-authored-by` trailers. Adding bot trailers pollutes the contributor graph (e.g., `StatsClaw-Shipper`, `Claude`).
- Tooling footers leak session identifiers and add noise to `git log`.

---

## Scope

- **Applies to**: every commit shipper creates — target repo, workspace repo, brain-seedbank fork.
- **Applies to**: every commit any other agent makes locally inside its worktree (builder, scriber, simulator) — these commits are squashed/merged back, but their messages should also be clean.
- **Does not apply to**: PR titles or bodies, issue comments, or any non-commit artifact (those may reference StatsClaw or the workflow when useful).

---

## Enforcement

If shipper (or any other agent) emits a commit with a forbidden trailer, reviewer flags it as a STOP. The fix is to amend or reword the commit before pushing.
