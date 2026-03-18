# Shared Skill: Credential Setup — Automatic GitHub Authentication

This skill automates GitHub credential detection and configuration so users never need to manually set up PATs or SSH keys before running a workflow.

---

## Trigger

This skill is invoked automatically by leader at the start of every workflow that targets a GitHub repository. It is NOT user-facing — users never need to think about credentials.

---

## Detection Sequence

Leader runs these checks in order. The first successful method is used.

### Step 1 — Check Environment Variable

```bash
echo "${GITHUB_TOKEN:+SET}"
```

If `GITHUB_TOKEN` is set, configure git for the **target repository**:
```bash
# Configure the target repo's remote with the token (most reliable method)
cd <TARGET_REPO_CHECKOUT>
git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/<owner>/<repo>.git"

# Also configure gh CLI if available
echo "$GITHUB_TOKEN" | gh auth login --with-token 2>/dev/null
```

**CRITICAL**: Always configure the **target repository's** git remote, not just the gh CLI. The token must be embedded in the target repo's remote URL for `git push` to work.

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
# Configure gh CLI (preferred — token stays in gh's secure store)
echo "<TOKEN>" | gh auth login --with-token

# Configure git remote with token (fallback — stores token in .git/config plaintext)
git remote set-url origin "https://<TOKEN>@github.com/<owner>/<repo>.git"
```

**Security note**: Embedding the token in the remote URL stores it in `.git/config` in plaintext. Prefer `gh auth login` when possible, which uses a secure credential store. If the token-in-URL method is used, it only persists in the local checkout and is not committed.

### For SSH:
```bash
# Ensure remote uses SSH URL
git remote set-url origin "git@github.com:<owner>/<repo>.git"
```

---

## Verification

After configuration, verify push access for **both** the target repo and the brain repo.

### Target Repo Verification (HARD GATE)

```bash
# MUST run these commands inside the target repo checkout, NOT in StatsClaw or any other repo
cd <TARGET_REPO_CHECKOUT>

# Test write access (PREFERRED — confirms push ability to the actual target)
git push --dry-run origin <branch> 2>&1

# Fallback: test read access (only if push --dry-run is not feasible)
git ls-remote origin 2>&1
```

**CRITICAL**: The verification MUST target the actual repository the workflow will push to. Testing against a different repository (e.g., the StatsClaw framework repo) does NOT satisfy this gate. A credential that works for repo A may not work for repo B.

**Note**: `git ls-remote` only confirms **read** access. A read-only token will pass `git ls-remote` but fail on push. Use `git push --dry-run` when possible to confirm write access. If `--dry-run` is not feasible (e.g., no commits yet), proceed with `git ls-remote` and note in `credentials.md` that write access is unconfirmed until first push.

If verification fails, retry with the next detection method or ask the user.

### Brain Repo Verification (SOFT GATE — warning, not blocking)

If the brain repo (`.repos/statsclaw-brain`) was acquired in step 2, also verify push access:

```bash
cd .repos/statsclaw-brain

# Configure remote with same token (if using token-based auth)
git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/<owner>/statsclaw-brain.git"

# Test write access
git push --dry-run origin main 2>&1
```

If brain repo push verification fails:
- **Do NOT block the workflow** — brain sync is not a hard gate
- **Warn the user**: "Brain repo push access not confirmed — workflow logs will not be synced to `[owner]/statsclaw-brain`."
- **Record in `credentials.md`**: `Brain Repo: FAIL — push access not confirmed`
- The workflow continues normally; brain sync is skipped at the end

---

## Write Credentials Record

After successful verification, write `credentials.md`:

```markdown
# Credential Verification

## Target Repository
Target Repository: <owner/repo>
Remote URL Tested: <url>
Method: <PAT / SSH / gh-cli / env-token>
Test Command: git push --dry-run origin <branch>
Result: PASS
Timestamp: <YYYY-MM-DD HH:MM>

### Verification Log
<exact output>

### Permissions Verified
- [x] Read access (git ls-remote)
- [ ] Write access (git push --dry-run — check if confirmed, or deferred to first real push)
- [x] Issue access (gh issue list)
- [x] PR access (gh pr list)

## Brain Repository
Brain Repository: <owner>/statsclaw-brain
Brain Repo Status: <PASS / FAIL / NOT_AVAILABLE>
Test Command: git push --dry-run origin main
Result: <PASS / FAIL — reason>
Timestamp: <YYYY-MM-DD HH:MM>

### Notes
<If FAIL or NOT_AVAILABLE: reason and whether user was notified>
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
