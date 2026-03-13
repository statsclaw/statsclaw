# Shared Skill: Worktree Isolation Protocol

This protocol governs how teammates are isolated from each other when they write to a target repository.

---

## When to Use Worktree Isolation

Use `isolation: "worktree"` when dispatching any teammate that **writes** to the target repository:

- **builder** -- implements code and test changes
- **scribe** -- updates documentation, examples, tutorials, and vignettes

Worktree isolation gives each writing teammate its own working copy of the repository. This prevents concurrent writers from interfering with each other and ensures that partial work from one teammate never corrupts another's checkout.

## When NOT to Use Worktree Isolation

Do **not** use worktree isolation for read-only teammates:

- **auditor** (when reviewing or running validation commands on an existing checkout)
- **skeptic** (reviews the evidence chain, never writes to the target repo)
- **theorist** (produces a spec artifact, does not modify target repo files)
- **github** (interacts with the remote via git/gh commands on the main checkout)

Read-only teammates operate on the main checkout or on a worktree that a writing teammate already produced, depending on where the latest changes live.

---

## Write Surface Enforcement

Every writing teammate receives an explicit **write surface** in its dispatch prompt. The write surface lists the exact files and directories that the teammate is allowed to modify.

### Rules

1. A teammate may **only** create, edit, or delete files within its assigned write surface.
2. **No two writing teammates may have overlapping write surfaces.** If builder owns `src/` and scribe owns `docs/`, neither may touch the other's directory.
3. If a teammate discovers that it needs to modify a file outside its surface, it MUST NOT do so. Instead, it appends a message to `mailbox.md` describing the needed change and continues with its own surface.
4. Only **lead** may mutate `status.md` and files under `locks/`. Teammates must never write to these paths.
5. Teammates may write their own output artifact (e.g., `implementation.md`, `docs.md`) to the run directory. This is always within their allowed surface.

### Overlap Detection

Lead is responsible for ensuring non-overlapping surfaces before dispatch. If a request requires two writers to touch the same file (e.g., builder and scribe both need to edit a README that contains code examples), lead must serialize them: dispatch the first writer, wait for completion, then dispatch the second with the updated state.

---

## Worktree Merge-Back

After a writing teammate completes in its worktree:

1. **Lead reads the output artifact** to confirm the teammate succeeded (no HOLD or BLOCK).
2. **Lead verifies the write surface** -- only expected files were modified.
3. **Changes from the worktree are merged back** into the main checkout. The Agent tool handles this automatically when the worktree teammate returns.
4. If merge conflicts arise (e.g., two writing teammates were dispatched in parallel on non-overlapping surfaces but git detects structural conflicts), lead must resolve them before dispatching the next downstream teammate.
5. After merge-back, the worktree is no longer active. Subsequent teammates (auditor, skeptic) operate on the merged main checkout.

---

## Summary

| Teammate | Writes to target repo? | Use worktree? |
| --- | --- | --- |
| builder | Yes | Yes |
| scribe | Yes | Yes |
| auditor | No (runs commands) | No |
| skeptic | No (reviews only) | No |
| theorist | No (spec only) | No |
| github | No (git/gh commands) | No |
| lead | No (runtime only) | N/A |
