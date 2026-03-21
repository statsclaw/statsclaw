# Shared Skill: Issue Patrol — Automated GitHub Issue Monitor

This skill enables StatsClaw to automatically scan open GitHub issues in a target repository, triage them, fix bugs, push fixes, and reply to issues — all from a simple user prompt.

---

## Trigger Phrases

Any of the following user intents activate this skill. **Exact wording is NOT required** — leader routes semantically:

- "Monitor issues on [repo]"
- "Check issues and fix bugs in [repo]"
- "Patrol [repo] issues"
- "Auto-fix issues in [repo]"
- "Watch [repo] for bugs and fix them"
- "Auto-check [repo] issues and fix them"
- "Periodically check [repo] issues"

A short prompt like `"patrol fect issues on cfe"` is sufficient.

---

## What This Skill Does

1. **Scan** — Fetches all open issues from the target GitHub repository using `gh issue list`
2. **Triage** — Classifies each issue as actionable (bug, test failure, error) or non-actionable (feature request, question, discussion)
3. **Prioritize** — Orders actionable issues by severity (crashes > test failures > warnings > minor bugs)
4. **Fix Loop** — For each actionable issue, runs the full StatsClaw workflow:
   - Creates a fix branch from the specified base branch
   - Dispatches planner → [builder ∥ tester] → reviewer → shipper
   - Pushes the fix and opens a PR
   - Posts a comment on the original issue linking the PR and summarizing the fix
5. **Report** — Produces a patrol report summarizing all actions taken

---

## Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `repo` | Yes | — | GitHub repository (e.g., `xuyiqing/fect`) |
| `base_branch` | No | `main` | Branch to create fix branches from |
| `branch_prefix` | No | `claude/fix` | Prefix for fix branch names |
| `labels` | No | all open issues | Filter issues by label (e.g., `bug`) |
| `max_issues` | No | 10 | Maximum issues to process per patrol run |
| `auto_push` | No | `true` | Automatically push fix branches |
| `auto_reply` | No | `true` | Automatically post comments on issues |
| `auto_pr` | No | `true` | Automatically create pull requests |
| `loop_interval` | No | `0` (one-shot) | Minutes between patrol runs (0 = run once) |

Leader extracts these from the user's natural language prompt. Missing parameters use defaults.

---

## Leader Execution Protocol

When this skill is activated, leader follows this sequence:

### Phase 1 — Setup

1. Parse the user prompt to extract parameters (repo, base branch, etc.)
2. Verify credentials (standard credential gate from CLAUDE.md)
3. Clone or locate the target repository
4. Create a patrol run: `.repos/workspace/<repo-name>/runs/PATROL-<timestamp>/`
5. Write `request.md` with patrol parameters

### Phase 2 — Scan and Triage

1. Fetch open issues:
   ```bash
   gh issue list --repo <owner/repo> --state open --limit <max_issues> --json number,title,body,labels,createdAt
   ```
2. For each issue, classify intent:
   - **Actionable**: describes a bug, error, crash, test failure, or incorrect behavior with enough detail to reproduce
   - **Non-actionable**: feature request, enhancement, question, discussion, or too vague to act on
3. Write `patrol-triage.md` to the run directory with the classification table

### Phase 3 — Fix Loop

For each actionable issue (in priority order):

1. Create a sub-run: `.repos/workspace/<repo-name>/runs/PATROL-<timestamp>/issue-<number>/`
2. Write `request.md` scoped to this specific issue
3. Write `impact.md` based on the issue description and codebase exploration
4. Run the full workflow: planner → [builder ∥ tester] → reviewer
   - Planner produces `spec.md` and `test-spec.md` for the issue
   - Builder and tester are dispatched in parallel with isolated specs
5. If reviewer PASS:
   - Dispatch shipper to create fix branch (`<branch_prefix>-issue-<number>-<short-desc>` from `<base_branch>`), push, create PR, and comment on the issue
   - The shipper agent MUST post a comment on the issue (see shipper agent's Issue Auto-Reply section)
6. If reviewer STOP:
   - Log the failure in the patrol report
   - Move to the next issue

### Phase 4 — Report

Write `patrol-report.md` summarizing:
- Total issues scanned
- Issues classified as actionable vs. non-actionable
- Issues successfully fixed (with PR links)
- Issues that failed (with reasons)
- Issues skipped (with reasons)

### Phase 5 — Loop (Optional)

If `loop_interval > 0`, repeat from Phase 2. Use the `/loop` skill via the `Skill` tool — do NOT implement polling with `sleep`.

---

## Branch Naming Convention

```
<branch_prefix>-issue-<number>-<short-description>
```

Examples:
- `claude/fix-issue-42-null-pointer`
- `claude/fix-issue-17-test-timeout`

Short description is derived from the issue title, lowercased, spaces replaced with hyphens, max 30 chars.

---

## Issue Auto-Reply Format

When shipper posts a comment on the issue, use this template:

```markdown
## Automated Fix Available

A fix for this issue has been pushed to branch `<branch-name>` and a pull request has been opened: #<pr-number>

### Summary of Changes
<brief description of what was changed and why>

### Validation
- R CMD check: PASS (0 errors, 0 warnings, N notes)
- Tests: all passing
- Review: approved by automated review

Please review the PR and let us know if the fix addresses your concern.

---
*This comment was generated by [StatsClaw](https://github.com/xuyiqing/StatsClaw) automated issue patrol.*
```

---

## Safety Rules

- **Never close issues** — only comment and link PRs. Closure is a human decision.
- **Never force-push** — always use regular push.
- **Skip ambiguous issues** — if the issue doesn't clearly describe a bug, skip it and log why.
- **One branch per issue** — never mix fixes for different issues in the same branch.
- **Respect the full workflow** — every fix goes through planner → [builder ∥ tester] → reviewer. No shortcuts.
- **Credential gate** — do not attempt any GitHub operations without verified credentials.

---

## Example User Prompts

All of these should trigger the same workflow:

```
"patrol fect issues on cfe"
"check open issues in xuyiqing/fect, fix bugs, push to cfe branch"
"monitor fect issues and auto-fix them"
"check fect issues and fix them on cfe branch"
"auto-fix fect issues"
```
