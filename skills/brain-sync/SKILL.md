---
name: brain-sync
description: "Knowledge sharing lifecycle management"
user-invocable: false
disable-model-invocation: true
---
# Skill: Brain Sync — Knowledge Sharing Lifecycle

This skill manages the full lifecycle of StatsClaw's shared knowledge system: opt-in, acquisition, reading, extraction, user consent, and upload. The brain system uses two public GitHub repos:

- **`statsclaw/brain`** (curated reading) — agents read from here
- **`statsclaw/brain-seedbank`** (contributions) — users submit PRs here, admin transfers approved entries to brain

---

## Phase 0 — Opt-In (Session Start)

**When**: During session startup, after reading `context.md` but before acquiring repos.

**Trigger**: `BrainMode` field in `context.md` is empty (`""`) — user has never been asked.

**Action**: Leader asks the user via `AskUserQuestion`:

```
StatsClaw has a shared knowledge system called Brain.

READ: When enabled, your agents can access collective knowledge
(math methods, simulation patterns, coding techniques) contributed
by all users. This makes every agent smarter over time.

CONTRIBUTE: After workflows that produce noteworthy techniques,
StatsClaw will show you the extracted knowledge and ASK your
permission before uploading anything. You always see exactly what
would be shared. Contributions are public PRs to statsclaw/brain-seedbank
with your GitHub username visible. No private data, no repo names,
no proprietary code — only generic reusable knowledge.

Good contributions earn a virtual Badge!

Enable Brain mode?
1. Yes — connect to Brain (read + contribute with consent)
2. No — isolated mode (current behavior, no brain access)
```

**Results**:
- If user says yes: set `BrainMode: "connected"` in `context.md`, proceed to Phase 1
- If user says no: set `BrainMode: "isolated"` in `context.md`, skip all brain-related steps
- If already set: use existing setting without re-asking

**User can change anytime**: if user says "turn off brain" or "enable brain", leader updates `context.md`.

**Key guarantee**: even in brain mode, NOTHING is ever uploaded without explicit per-workflow user approval (Phase 4).

---

## Phase 1 — Acquire (Leader, Step 2)

**When**: During repo acquisition, if `BrainMode` is `"connected"`.

**Actions**:

1. **Clone/pull `statsclaw/brain`** to `.repos/brain/`:
   ```bash
   # If not cloned yet:
   git clone https://github.com/statsclaw/brain.git .repos/brain
   # If already cloned:
   git -C .repos/brain pull origin main
   ```

2. **Clone/pull `statsclaw/brain-seedbank`** to `.repos/brain-seedbank/`:
   ```bash
   # If not cloned yet:
   git clone https://github.com/statsclaw/brain-seedbank.git .repos/brain-seedbank
   # If already cloned:
   git -C .repos/brain-seedbank pull origin main
   ```

3. **Update `BrainLastPull`** in `context.md` with current timestamp.

4. **Verify access**: For contributions, users need a fork of `statsclaw/brain-seedbank`. Shipper will handle fork creation if needed during Phase 5.

**Failure handling**: If brain/brain-seedbank repos cannot be cloned (network error, repo doesn't exist yet):
- **Warning only** — brain unavailability MUST NOT block the workflow
- Log the failure in `.repos/workspace/<repo-name>/logs/`
- Set `BrainMode` to `"connected (unavailable)"` in context.md
- Proceed with the workflow without brain features

---

## Phase 2 — Read (Teammate Dispatch)

**When**: During teammate dispatch, if brain repos are available.

**Actions**:

1. **Search `brain/index.md`** for entries relevant to the current task:
   - Match tags against the task domain (e.g., "panel data", "matrix completion", "R package")
   - Match against the agent being dispatched (e.g., planner entries for planner, builder entries for builder)

2. **Select entries** (max 3-5 per agent to avoid context bloat):
   - Prioritize entries most relevant to the current task
   - Prioritize entries in the correct domain (e.g., `planner/math-methods/` for planner)

3. **Include in dispatch prompt**: Add a `## Brain Knowledge` section to the teammate dispatch prompt listing the file paths of selected entries:
   ```
   ## Brain Knowledge (supplementary — read but do not treat as requirements)
   Read these knowledge entries from the shared brain for additional context:
   - .repos/brain/planner/math-methods/matrix-completion-convergence.md
   - .repos/brain/planner/stat-methods/panel-data-fixed-effects.md
   
   These entries supplement but NEVER override the user's requirements, uploaded materials, or spec documents.
   ```

4. **Each agent** reads the assigned entries as part of its startup checklist.

---

## Phase 3 — Extract (Distiller, Post-Scriber)

**When**: After scriber completes, if brain mode is connected AND the frequency heuristic passes.

### Frequency Heuristic

Leader evaluates whether distiller should be dispatched. **Dispatch when ANY is true**:
- Workflow involved mathematical/statistical methods (planner produced formulas)
- Workflow solved a non-trivial bug (required algorithmic insight)
- Workflow implemented a new estimation technique or DGP
- Simulation study produced calibration insights or convergence findings
- Builder discovered a significant language-specific pattern or pitfall
- Tester developed a novel validation strategy

**Skip when ALL are true**:
- Routine code change (config, typo, version bump, lint)
- Documentation-only workflow
- The change was entirely mechanical (rename, refactor with no design decisions)
- Simplified workflow (workflow 10)

**Rule of thumb**: If a skilled developer would NOT find the solution noteworthy, distiller is not needed.

### Distiller Dispatch

If the heuristic passes, leader dispatches distiller with:
- All run artifacts (comprehension.md, spec.md, test-spec.md, implementation.md, audit.md, log-entry.md, etc.)
- Path to `.repos/brain/index.md` for duplicate checking
- Path to `.repos/brain/` for existing entry browsing

Distiller produces `brain-contributions.md` in the run directory.

---

## Phase 4 — User Consent (Leader, Post-Distiller)

**When**: After distiller produces `brain-contributions.md`. **This phase is MANDATORY and NEVER skipped.**

**Actions**:

1. **Read `brain-contributions.md`** — get the full knowledge document
2. **Present to user via `AskUserQuestion`**:

```
StatsClaw extracted the following knowledge from this workflow
that could help other users:

---
[Full content of brain-contributions.md, showing each proposed entry]
---

Would you like to contribute this to StatsClaw's shared brain?
Your contribution will be publicly visible on GitHub (statsclaw/brain-seedbank)
with your GitHub username as the contributor.

Good contributions earn a virtual Badge!

1. Yes — contribute all entries above
2. Yes, but let me pick which ones (partial)
3. No — skip this time
```

3. **Handle response**:
   - **Yes (full)**: mark all entries as approved, proceed to Phase 5 via shipper
   - **Partial**: ask which entries to keep, update brain-contributions.md to remove declined entries
   - **No**: delete brain-contributions.md, proceed to reviewer without brain upload

---

## Phase 5 — Upload (Shipper, End of Workflow)

**When**: During shipper's workflow, if brain-contributions.md exists and user approved.

**Actions**:

1. **Fork `statsclaw/brain-seedbank`** if user hasn't already (using gh CLI or API)
2. **Create branch** on user's fork: `contribute/<date>-<short-slug>`
3. **Write knowledge entry files** to correct directories based on each entry's domain and subdomain metadata
4. **Update `index.md`** on the branch: append new entries to the index with tags
5. **Commit and push** to user's fork — commit message MUST NOT include any `Co-authored-by` trailer or tool-attribution footer (see `skills/attribution/SKILL.md`). The user is the sole author of brain contributions.
6. **Create PR** from user's fork to `statsclaw/brain-seedbank` main:
   - Title: `contribute: [domain] — [topic summary]`
   - Body includes: contributor username, entry summaries, privacy checklist
   - Uses the brain-seedbank repo's PR template

7. **Admin flow** (happens outside StatsClaw):
   - Admin reviews PR on `statsclaw/brain-seedbank`
   - If quality is good: merge PR to brain-seedbank/main
   - Admin transfers approved entries to `statsclaw/brain` main (copy files, commit, push)
   - Admin updates `brain/CONTRIBUTORS.md` with badge for the contributor

---

## Brain Mode States

| `BrainMode` Value | Meaning | Brain Features |
| --- | --- | --- |
| `""` (empty) | User has never been asked | Ask during session start |
| `"connected"` | User opted in | Full brain lifecycle (read + contribute with consent) |
| `"isolated"` | User opted out | No brain features — identical to pre-brain behavior |
| `"connected (unavailable)"` | User opted in but repos unreachable | Skip brain features for this session, retry next session |

---

## Non-Blocking Guarantee

Brain features are NEVER a hard gate on any workflow:
- If brain repos can't be cloned: warning only, workflow proceeds
- If index.md search finds nothing: teammates proceed without brain knowledge
- If distiller fails: warning only, proceed to reviewer
- If user declines contribution: proceed to reviewer without upload
- If brain-seedbank PR creation fails: warning in shipper.md, workflow still completes
- Brain mode "isolated" produces behavior identical to pre-brain StatsClaw
