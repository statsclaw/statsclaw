# Shared Skill: Credential Setup — Automatic GitHub Authentication

This skill automates GitHub credential detection and configuration so users never need to manually set up PATs or SSH keys before running a workflow.

---

## Trigger

This skill is invoked automatically by lead at the start of every workflow that targets a GitHub repository. It is NOT user-facing — users never need to think about credentials.

---

## Detection Sequence

Lead runs these checks in order. The first successful method is used.

### Step 1 — Check Environment Variable

```bash
echo "${GITHUB_TOKEN:+SET}"
```

If `GITHUB_TOKEN` is set, configure `gh` and `git`:
```bash
echo "$GITHUB_TOKEN" | gh auth login --with-token 2>/dev/null
gh auth status
```

### Step 2 — Check gh CLI Auth

```bash
gh auth status 2>&1
```

If `gh` is already authenticated, extract the token for git operations:
```bash
gh auth token
```

### Step 3 — Check SSH Key

```bash
ssh -T git@github.com 2>&1
```

If SSH returns a successful authentication message (even with exit code 1), SSH is available.

### Step 4 — Check Git Credential Helper

```bash
git config --global credential.helper
```

If a credential helper is configured, test it:
```bash
git ls-remote https://github.com/<owner>/<repo>.git 2>&1
```

### Step 5 — Ask User

If all automated checks fail, use `AskUserQuestion`:

```
I need GitHub access to push fixes and comment on issues.
How would you like to authenticate?

Option 1: Paste a GitHub Personal Access Token (PAT)
  - Go to https://github.com/settings/tokens
  - Create a token with 'repo' and 'issues' scope

Option 2: The environment already has SSH keys configured

Option 3: Set GITHUB_TOKEN environment variable and restart
```

---

## Configuration

Once a working method is found:

### For PAT / Token:
```bash
# Configure git remote with token
git remote set-url origin "https://<TOKEN>@github.com/<owner>/<repo>.git"

# Configure gh CLI
echo "<TOKEN>" | gh auth login --with-token
```

### For SSH:
```bash
# Ensure remote uses SSH URL
git remote set-url origin "git@github.com:<owner>/<repo>.git"
```

---

## Verification

After configuration, ALWAYS verify:

```bash
# Test git access
git ls-remote origin 2>&1

# Test gh CLI access
gh repo view <owner/repo> --json name 2>&1
```

Both must succeed. If either fails, retry with the next method or ask the user.

---

## Write Credentials Record

After successful verification, write `credentials.md`:

```markdown
# Credential Verification

Target Repository: <owner/repo>
Remote URL Tested: <url>
Method: <PAT / SSH / gh-cli / env-token>
Test Command: git ls-remote <url>
Result: PASS
Timestamp: <YYYY-MM-DD HH:MM>

## Verification Log
<exact output>

## Permissions Verified
- [x] Push access (git ls-remote)
- [x] Issue access (gh issue list)
- [x] PR access (gh pr list)
```

---

## Cloud Environment Notes

In Claude Code cloud environments:

1. **`GITHUB_TOKEN` is often pre-set** — Step 1 usually succeeds
2. **`gh` CLI is usually pre-authenticated** — Step 2 is the fallback
3. **SSH keys may not be available** — Step 3 often fails in cloud
4. If nothing works, the user needs to set `GITHUB_TOKEN` in their cloud environment's secrets/settings panel

---

## Error Messages

Provide clear, actionable error messages:

| Situation | Message |
| --- | --- |
| No auth found | "No GitHub credentials detected. Please set GITHUB_TOKEN in your environment secrets." |
| Token expired | "GitHub token is expired or revoked. Please generate a new one at https://github.com/settings/tokens" |
| Insufficient scope | "Token lacks required permissions. Needs: repo, issues. Please regenerate with correct scopes." |
| SSH key rejected | "SSH key not authorized for this repository. Please add your key at https://github.com/settings/keys" |
