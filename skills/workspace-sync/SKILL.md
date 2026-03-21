# Shared Skill: Workspace Sync — Centralized Workflow Log Repository

All workflow-generated logs, process records, handoff documents, reference materials, **and runtime state** are stored in a dedicated **workspace repository** on GitHub. The user chooses the repo name (e.g., `[username]/workspace`) and tells StatsClaw which repo to use. Each target repository gets its own folder inside the workspace repo, which serves as both the runtime state directory during workflows and the permanent log archive after shipping. This keeps target repositories clean — only code and essential documentation live in the target repo.

---

## Concept

The **workspace repo** is a per-user GitHub repository that serves dual roles: (1) it is the **runtime state directory** where all workflow artifacts are written during execution, and (2) it is the **permanent archive** where completed run logs, changelogs, and handoff documents are pushed. Each target repository gets its own folder inside the workspace repo. This ensures:

1. **Target repos stay clean** — only source code, `Architecture.md`, and necessary user-facing documentation (README, help files, vignettes, man pages)
2. **Full traceability** — every workflow run's process record, before/after comparisons, and design decisions are preserved
3. **Cross-project visibility** — all workflow history in one place
4. **No redundant state directories** — runtime state and final logs live in the same place

---

## Workspace Repo Structure

```text
workspace/
├── README.md
├── <repo-name>/
│   ├── context.md                # active project context (runtime)
│   ├── CHANGELOG.md              # timeline index of all runs (pushed)
│   ├── HANDOFF.md                # active handoff for next session (pushed)
│   ├── docs.md                   # latest documentation change summary (pushed)
│   ├── ref/                      # reference docs for future work (pushed)
│   │   └── <topic>.md
│   ├── runs/
│   │   ├── <request-id>/         # active run artifacts (runtime, local)
│   │   │   ├── request.md, status.md, impact.md, ...
│   │   │   └── (all workflow artifacts)
│   │   ├── <YYYY-MM-DD>-<slug>.md  # completed run logs (pushed)
│   │   └── <YYYY-MM-DD>-<slug>.md
│   ├── logs/                     # diagnostic logs (local)
│   └── tmp/                      # transient data (local)
└── ...
```

- **`<repo-name>/`**: folder name matches the target repo name (e.g., `fect`, `panelview`). For repos with the same name under different owners, use `<owner>-<repo>` (e.g., `alice-utils`, `bob-utils`).
- **`CHANGELOG.md`**: timeline index linking every workflow run. Append-only — each run adds an entry with date, slug, one-line summary, and status. Newest entries at the top.
- **`HANDOFF.md`**: active handoff document — what the next developer or session needs to know. Overwritten each run with the latest handoff notes extracted from `log-entry.md`.
- **`ref/`**: reference documents produced during workflows that are useful for future work (comparison tables, algorithm specs, design explorations). Files accumulate — never deleted.
- **`runs/<request-id>/`**: active run directories containing all workflow artifacts (request.md, status.md, spec.md, audit.md, etc.). These are runtime state — created during workflow execution, cleaned up after 7 days. Not individually committed to the workspace repo.
- **`runs/<YYYY-MM-DD>-<slug>.md`**: completed run log files promoted from `log-entry.md` by shipper. These are the permanent record — committed and pushed to the workspace repo.
- **`logs/`** and **`tmp/`**: local-only directories for diagnostic output and transient data. Not committed to the workspace repo. Add them to the workspace repo's `.gitignore` if needed.
- **`runs/<date>-<slug>.md`**: one file per workflow run. Full process record. Accumulates chronologically. Never overwritten or deleted.

---

## Workspace Repo Naming

The workspace repo name is **user-configurable**. The user tells StatsClaw which GitHub repository to use as the workspace. There is no hardcoded default name — leader MUST ask the user if no workspace repo is configured.

Common patterns:
- `xuyiqing/workspace` — simple and clean
- `xuyiqing/statsclaw-logs` — descriptive
- Any repo the user has push access to

The workspace repo URL is determined by the repo itself (its git remote). Leader asks the user which workspace repo to use at the start of the first workflow if no workspace checkout exists.

---

## Where the Workspace Repo Lives Locally

The workspace repo is cloned into `.repos/` alongside target repos:

```text
.repos/
├── fect/                    # target repo checkout
├── panelview/               # another target repo
└── workspace/         # workspace repo (workflow logs)
```

The workspace repo is treated like any other repo checkout — it's git-ignored and never committed to StatsClaw.

---

## Two-Phase Workflow: Pull First, Push Last

Workspace sync has two distinct phases that bookend the entire workflow:

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: ACQUIRE (start of workflow, step 2)           │
│  ├── git pull target repo                               │
│  └── git pull workspace repo (or clone, or auto-create)     │
├─────────────────────────────────────────────────────────┤
│  ... workflow runs (planner → builder → tester → ...) │
├─────────────────────────────────────────────────────────┤
│  PHASE 2: PUSH (end of workflow, shipper agent)          │
│  ├── git push target repo (code + docs only)            │
│  └── git push workspace repo (CHANGELOG + HANDOFF + run log) │
└─────────────────────────────────────────────────────────┘
```

---

## Phase 1: Acquire (Leader, Step 2 of Mandatory Protocol)

Leader is responsible for acquiring BOTH repos at the START of every workflow. This happens in step 2 of the Mandatory Execution Protocol (ACQUIRE REPOS).

### Step 1 — Check for Existing Local Checkout

```bash
# If workspace repo is already cloned locally, use it
if [ -d ".repos/workspace" ]; then
    WORKSPACE_REPO=$(git -C .repos/workspace remote get-url origin | sed 's|.*github.com[:/]||;s|\.git$||')
    git -C .repos/workspace pull origin main
    # Done — skip to Step 4
fi
```

If `.repos/workspace` already exists locally, pull latest and skip to Step 4.

### Step 2 — Detect User and Probe Default Name

If no local checkout exists, determine the user's GitHub identity and probe for the default workspace repo name:

```bash
GH_USER=$(gh api user --jq '.login')
DEFAULT_WORKSPACE="${GH_USER}/workspace"
gh repo view "$DEFAULT_WORKSPACE" --json name,description 2>&1
```

This produces one of two outcomes:

### Step 3a — Repo `<user>/workspace` Does Not Exist

Ask the user via `AskUserQuestion`:

> "You don't have a `workspace` repository on GitHub yet. I use a workspace repo to store workflow logs, process records, and runtime state for all your projects. Should I create `<user>/workspace` for you?"
>
> Options:
> 1. **Yes, create it** — creates `<user>/workspace` as a public repo
> 2. **Use a different name** — you specify the repo name
> 3. **Skip workspace** — workflow proceeds without log recording (not recommended)

- If **yes**: create and clone (see Step 3c below)
- If **different name**: ask for the name, then probe that name (loop back to check existence)
- If **skip**: set `workspace_available: false` in `request.md`, warn user, continue

### Step 3b — Repo `<user>/workspace` Already Exists

Clone it and use it directly:

```bash
git clone "https://github.com/${DEFAULT_WORKSPACE}.git" .repos/workspace
```

Proceed to Step 4. The workspace repo is the user's repo — no markers or validation needed. StatsClaw simply creates per-repo subdirectories (e.g., `fect/`, `panelview/`) inside it alongside whatever content already exists.

### Step 3c — Create a New Workspace Repo

```bash
gh repo create "$WORKSPACE_REPO" --public --description "StatsClaw workflow logs and process records"
git clone "https://github.com/${WORKSPACE_REPO}.git" .repos/workspace
```

Then initialize with a README:

```markdown
# StatsClaw Workspace

Centralized repository for workflow logs, process records, and reference documents generated by [StatsClaw](https://github.com/xuyiqing/StatsClaw).

Each subdirectory corresponds to a target repository. Inside each:
- `context.md` — active project context and runtime state
- `CHANGELOG.md` — timeline index of all workflow runs
- `HANDOFF.md` — active handoff for the next developer/session
- `ref/` — reference documents for future work
- `runs/` — chronological process records for every workflow run

These artifacts are automatically generated and pushed by the StatsClaw workflow framework.
```

Commit and push the README.

### Step 3d — If Repo Creation Fails

If `gh repo create` fails (insufficient permissions, API error, etc.):

1. **Warn the user explicitly** via `AskUserQuestion` or direct message:
   > "I cannot create the workspace repository. Workflow logs will NOT be recorded for this session. Please either:
   > 1. Create the repository manually at https://github.com/new and tell me the name
   > 2. Grant the current token `repo` scope for repository creation
   >
   > The workflow will continue, but without log recording."

2. **Record in `credentials.md`**: `Workspace Repo: FAIL — creation failed, user notified`
3. **Set `workspace_available: false`** in the run's `request.md`
4. **Continue the workflow** — workspace sync is skipped at the end, but code changes still proceed normally

**This is NOT a silent skip.** The user MUST be informed.

### Step 4 — Verify Workspace Repo Push Access

After acquiring the workspace repo, verify push access:

```bash
cd .repos/workspace
git push --dry-run origin main 2>&1
```

If this fails, configure the remote with the same token used for the target repo:

```bash
git -C .repos/workspace remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${WORKSPACE_REPO}.git"
```

Record result in `credentials.md` under a `Workspace Repo` section.

---

## Phase 2: Push (Shipper Agent, End of Workflow)

The shipper agent handles pushing to BOTH repos at the end of the workflow.

### Order of Operations

```
1. Pull latest from target repo (in case of remote changes during workflow)
2. Stage + commit code changes to target repo
3. Push target repo
4. Pull latest from workspace repo (in case of concurrent workspace syncs from other sessions)
5. Copy workflow artifacts to workspace repo
6. Commit + push workspace repo
7. Create PR, post issue comments (if applicable)
```

### Target Repo Push (Steps 1–3)

Standard shipper agent workflow — stage code + user-facing docs + `Architecture.md`, commit, push. No other workflow artifacts.

### Workspace Repo Push (Steps 4–6)

```bash
# 4. Pull latest
git -C .repos/workspace pull origin main

# 5. Copy artifacts
REPO_NAME=$(basename "$(git -C "$TARGET_REPO" remote get-url origin)" .git)
WORKSPACE_DIR=".repos/workspace/${REPO_NAME}"
mkdir -p "${WORKSPACE_DIR}/runs"
mkdir -p "${WORKSPACE_DIR}/ref"

# 5a. Copy run log (new file — accumulates)
LOGFILE=$(grep -oP '(?<=<!-- filename: ).*(?= -->)' "${RUN_DIR}/log-entry.md")
cp "${RUN_DIR}/log-entry.md" "${WORKSPACE_DIR}/runs/${LOGFILE}"

# 5b. Copy docs.md (overwrite with latest documentation change summary)
cp "${RUN_DIR}/docs.md" "${WORKSPACE_DIR}/docs.md"

# 5c. Update CHANGELOG.md (prepend new entry to timeline index)
# Format: | date | slug | one-line summary | status |
# Shipper reads implementation.md/request.md for the summary line

# 5d. Update HANDOFF.md (overwrite with latest handoff notes)
# Extract "Handoff Notes" section from log-entry.md and write to HANDOFF.md

# 5e. Copy reference docs to ref/ (if any were produced)
# Only if scriber or planner produced reference materials for future work

# 6. Commit and push (only pushed artifacts, not local-only dirs)
cd .repos/workspace
git add "${REPO_NAME}/CHANGELOG.md" "${REPO_NAME}/HANDOFF.md" "${REPO_NAME}/docs.md" "${REPO_NAME}/runs/${LOGFILE}" "${REPO_NAME}/ref/"
git commit -m "sync: ${REPO_NAME} — <short description of the change>"
git push origin main
```

#### CHANGELOG.md Format

Shipper maintains `CHANGELOG.md` as a reverse-chronological timeline index. Each entry is one line in a markdown table:

```markdown
# Changelog — <repo-name>

| Date | Run | Summary | Status |
| --- | --- | --- | --- |
| 2026-03-17 | [convergence-conditioning](runs/2026-03-17-convergence-conditioning.md) | Fix convergence check in conditioning step | PASS |
| 2026-03-16 | [cv-unification](runs/2026-03-16-cv-unification.md) | Unify CV methods under single dispatcher | PASS |
```

Newest entries at the top. Each run links to its process record in `runs/`.

#### HANDOFF.md Format

Shipper overwrites `HANDOFF.md` each run with the latest handoff notes extracted from `log-entry.md` → "Handoff Notes" section. This is a living document — always reflects the most recent run's handoff state.

```markdown
# Active Handoff — <repo-name>

> Last updated: <YYYY-MM-DD> from run `<slug>`

<content of Handoff Notes section from log-entry.md>
```

#### ref/ Directory

Reference documents accumulate in `ref/`. These are produced when a workflow generates comparison tables, algorithm specifications, design explorations, or other materials useful for future work. Shipper copies them from the run directory if the scriber or planner explicitly marks files for `ref/` in their output artifacts.

### Workspace-Sync-Only Dispatch

If the workflow does NOT include a ship step (workflows 1, 3, 6, 8), leader MUST still dispatch the shipper agent with a **workspace-sync-only** task. In this case:
- Shipper skips steps 1–3 (no target repo push)
- Shipper executes steps 4–6 (workspace repo sync only)
- No PR or issue comments
- `shipper.md` records workspace sync status only

---

## What Goes Where: Target Repo vs Workspace Repo

| Artifact | Target Repo | Workspace Repo | Notes |
| --- | --- | --- | --- |
| Source code changes | Yes | No | Builder's work |
| Unit tests | Yes | No | Builder's work |
| User-facing docs (README, help, vignettes) | Yes | No | Scriber's work |
| `Architecture.md` | **Yes** (root) | No | Scriber writes to target repo root + run directory; committed by shipper |
| `docs.md` | No | **Yes** | Scriber writes to run dir; shipper syncs to workspace `<repo-name>/docs.md` |
| `runs/<date>-<slug>.md` | No | **Yes** | Scriber writes `log-entry.md` to run dir; shipper syncs to `runs/` |
| `CHANGELOG.md` | No | **Yes** | Shipper maintains — timeline index of all runs |
| `HANDOFF.md` | No | **Yes** | Shipper maintains — latest handoff notes |
| `ref/<topic>.md` | No | **Yes** (if produced) | Reference docs for future work |
| Run directory artifacts (spec.md, audit.md, etc.) | No | Local only | Live in `.repos/workspace/<repo-name>/runs/<request-id>/` during workflow; not pushed |

---

## Credential Handling

The workspace repo typically uses the **same credentials** as the target repo (same owner). During step 4 of the Mandatory Execution Protocol (VERIFY CREDENTIALS):

1. **Verify target repo push access** — hard gate (workflow cannot proceed without this)
2. **Verify workspace repo push access** — soft gate (workflow proceeds, but user is warned if this fails)

If the workspace repo is under a different owner (edge case), separate credential verification is needed.

The credential setup skill (`skills/credential-setup/SKILL.md`) configures git remotes with tokens. The same token configuration should be applied to the workspace repo's remote URL.

---

## Symlink Support

Some users prefer to keep target repos outside of `.repos/` and symlink them in. This is fully supported:

```bash
# User's external checkout
ln -s ~/GitHub/fect .repos/fect
```

The workspace repo itself can also be symlinked if the user prefers a different location. StatsClaw follows symlinks transparently — all operations use the resolved path.

**Rules**:
- Always use `-L` flag with `test` when checking if a directory exists: `test -L .repos/fect -o -d .repos/fect`
- Never delete symlink targets — only the symlink itself if cleanup is needed
- `git -C` works through symlinks natively

---

## Error Handling

| Situation | Leader Action (Phase 1) | Shipper Action (Phase 2) |
| --- | --- | --- |
| Workspace repo doesn't exist on GitHub | Ask user whether to create it (Step 3a) | N/A (already handled in Phase 1) |
| `<user>/workspace` already exists | Clone and use it directly (Step 3b) | N/A |
| Workspace repo creation fails | **Warn user explicitly**, set `workspace_available: false`, continue workflow | Skip workspace sync, note in `shipper.md` |
| Workspace repo clone/pull fails (network) | Retry up to 3 times. If all fail, warn user, set `workspace_available: false` | Skip workspace sync, note in `shipper.md` |
| Workspace repo push fails | N/A | Retry up to 3 times with exponential backoff. If all fail, **warn user**, note in `shipper.md` |
| Target repo has no remote (local-only) | Use directory name as folder name in workspace | Use directory name as folder name |
| User chooses "skip workspace" | Set `workspace_available: false`, warn user | Skip workspace sync entirely |
| `workspace_available: false` in request.md | N/A | Skip workspace sync entirely |

**Key rule**: Workspace sync failures MUST NOT block the main workflow. Target repo code changes are always the priority. But the user MUST be explicitly informed when logs cannot be recorded — never silently skip.
