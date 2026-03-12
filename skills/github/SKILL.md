# Skill: github — GitHub Operations Agent

GitHub handles issue and pull request interactions for the active target project. It can inspect issues, sync issue queues, read PR comments, inspect checks, and convert actionable GitHub items into StatsClaw runs.

This skill supports both interactive use and Claude-managed scheduled issue scans.

---

## Triggers

Invoke `github` when the user:

- asks to inspect GitHub issues
- asks to look at PRs or review comments
- asks about CI checks or GitHub checks
- asks to triage open issues
- asks to maintain labels, milestones, or GitHub queue state
- asks to scan issues on a schedule

Also invoke `github` before `triage` when the source of work is a GitHub issue rather than a free-form user request.

---

## Tools

Read, Write, Edit, Bash

---

## Workflow

### Step 1 — Resolve the target GitHub repository

Read:

- `.statsclaw/CONTEXT.md`
- active project context if present

Determine the target GitHub repo in this order:

1. explicit user-provided `owner/repo`
2. git remote of the active target project
3. configured repo in project context

If the repo is still unclear, raise a **HOLD** and ask one concise question.

### Step 2 — Detect GitHub access mode

Before making GitHub requests, detect the available access mode in this order:

1. `gh` CLI is installed and authenticated
2. `GH_TOKEN` or `GITHUB_TOKEN` is available for GitHub REST API access
3. neither is available

Expected behavior:

- if `gh` exists, use it by default
- if `gh` does not exist but a token is available, use `curl` against the GitHub REST API
- if neither exists, raise a **HOLD** and explain that GitHub access is unavailable

Do not fail immediately just because `gh` is missing.

### Step 3 — Check for a scheduled issue scan

Read `.statsclaw/CONTEXT.md` and determine whether a GitHub schedule is configured, for example:

- `daily 00:00 America/Los_Angeles`

If the user explicitly asks to schedule recurring scans:

- parse the schedule from natural language and record it in `GitHubIssueSchedule`
- parse any issue filter from natural language and record it in `GitHubIssueFilter`
- parse whether automatic solving is requested and record it in `GitHubAutoSolve`
- record the target repo in the active project context when useful

Examples of natural-language parsing:

- "每天 0 点 PT 扫描" → `GitHubIssueSchedule: daily 00:00 America/Los_Angeles`
- "每周一早上 9 点扫一次" → `GitHubIssueSchedule: weekly Monday 09:00 [best-known timezone]`
- "只看 bug label" → `GitHubIssueFilter: label:bug`
- "只看 open 的 enhancement" → `GitHubIssueFilter: is:open label:enhancement`
- "自动激活整个 workflow 去解决" → `GitHubAutoSolve: true`
- "先排队不要自动解决" → `GitHubAutoSolve: false`

If a schedule exists and the current time is at or past the scheduled scan time and `LastGitHubIssueScanAt` is stale, run the issue scan before any other GitHub action.

StatsClaw itself does not wake Claude Code from nothing. The schedule is enforced whenever Claude is invoked or when a session is active and reaches the due time.

### Step 4 — Inspect GitHub state

Use the active GitHub access mode to inspect the relevant GitHub objects.

Examples:

- `gh issue list` / `gh issue view`
- `gh pr list` / `gh pr view`
- `gh api` for review comments and checks when needed
- `curl https://api.github.com/repos/<owner>/<repo>/issues`
- `curl https://api.github.com/repos/<owner>/<repo>/pulls`
- `curl https://api.github.com/repos/<owner>/<repo>/issues/<n>/comments`

If `GitHubIssueFilter` is set, apply it when scanning issues.

Possible outputs:

- actionable issue queue
- issue details for a selected issue
- PR feedback summary
- failing checks summary

### Step 5 — Create or update the GitHub run artifact

If the work should enter the StatsClaw workflow, create or update:

```text
.statsclaw/runs/<request-id>/github.md
```

Use `templates/stage-report.md`.

If a GitHub issue becomes the source of work, also create or update:

```text
.statsclaw/runs/<request-id>/request.md
.statsclaw/runs/<request-id>/status.md
```

Set the next owner to `triage` unless the request is purely informational.

### Step 6 — Route or continue

- For issue-driven work: route to `triage`
- For PR review or checks work: route to `skeptic`, `builder`, or `auditor` as appropriate
- For release-facing GitHub actions: route to `release`

### Step 7 — Post-solution GitHub follow-up

When an issue-driven workflow completes successfully:

- ensure the solved work is handed to `release` for branch push and PR preparation when requested or when the issue-solving policy requires it
- ensure a GitHub issue comment is posted summarizing:
  - what was implemented
  - which branch contains the changes
  - whether a PR was created
  - any remaining risks or manual follow-up

Never auto-close the issue. Human maintainers must decide when to close it.

### Step 8 — Scheduled queue behavior

For daily scheduled scans:

- list open actionable issues
- summarize them into a queue artifact
- if `GitHubAutoSolve` is true, convert the top actionable issue into a StatsClaw run and route immediately to `triage`
- update `LastGitHubIssueScanAt` after the scan completes

Execution model:

- scheduled issue handling is managed inside the Claude workflow layer
- if a due scan is detected during a Claude session, `github` should perform it before continuing with other work
- if automatic issue solving is requested, `github` should create the run artifacts and activate the downstream workflow in the same Claude execution context
- if the issue is solved in the same execution context, `github` should route to `release` and then post a completion comment to the issue

---

## Quality Checks

- Do not assume the GitHub repo slug; verify it
- Do not assume `gh` exists; detect it
- Use token-backed REST API access when `gh` is unavailable
- Do not require the user to translate natural-language schedule requests into config fields manually
- Distinguish issues, PRs, review comments, and checks clearly
- If converting an issue into a run, make the request contract explicit
- Update `.statsclaw/runs/<request-id>/status.md` whenever a GitHub-driven run changes state
- Do not claim that a scheduled scan solved an issue unless the downstream StatsClaw workflow actually ran
- Do not auto-close issues after posting a resolution comment

---

## Output Format

- `.statsclaw/runs/<request-id>/github.md` when work enters the workflow
- optional `.statsclaw/runs/<request-id>/request.md` and `status.md`
- concise GitHub summary and routing decision
