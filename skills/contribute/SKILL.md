---
name: contribute
description: "Session knowledge contribution to the shared brain"
user-invocable: true
---
# Skill: Contribute — Session Knowledge Contribution

The `/contribute` command lets users explicitly trigger knowledge extraction and contribution at any point during a session. It summarizes what worked, what required manual intervention, and what domain-specific patterns emerged — then offers to submit these lessons to the shared brain.

This is the **user-invocable entry point** for brain contributions. While the standard workflow dispatches distiller automatically after noteworthy workflows (brain-sync Phase 3), `/contribute` gives users direct control: they can invoke it whenever they want to share what they've learned.

---

## Trigger Phrases

| User says | Detected intent |
| --- | --- |
| `/contribute` | Direct skill invocation |
| `"contribute"` / `"contribute to brain"` / `"share what I learned"` | Natural language trigger |
| `"submit lessons"` / `"share knowledge"` / `"add to brain"` | Natural language trigger |
| `"summarize lessons"` / `"what did we learn"` + intent to share | Natural language trigger |

---

## When to Use

- **After completing a workflow** — the user wants to contribute knowledge from the current or recent session
- **Mid-session** — the user has accumulated insights across multiple runs and wants to batch-contribute
- **Standalone** — no active workflow required; the user may invoke `/contribute` purely to share knowledge from their experience

---

## Prerequisites

1. **Brain mode must be `"connected"`**. If brain mode is `"isolated"` or unset:
   - Leader asks the user via `AskUserQuestion`: "Brain mode is currently disabled. Would you like to enable it to contribute knowledge?"
   - If the user says yes: set `BrainMode: "connected"` in `context.md`, acquire brain repos (Phase 1 of `skills/brain-sync/SKILL.md`), then proceed.
   - If the user says no: inform them that `/contribute` requires brain mode and stop.

2. **Brain repos must be available**. If `.repos/brain/` or `.repos/brain-seedbank/` are not cloned:
   - Leader acquires them (same as brain-sync Phase 1).
   - If acquisition fails: warn the user and stop.

3. **Workspace repo should be available** (for storing the contribution artifact in the run directory). If not, `/contribute` still proceeds — the contribution goes to brain-seedbank regardless.

4. **Push credentials** for the user's fork of `statsclaw/brain-seedbank` must be verifiable. Leader checks during the flow and warns if push access cannot be confirmed.

---

## Parameters

| Parameter | Source | Default |
| --- | --- | --- |
| `scope` | User prompt or inferred | `"session"` — all runs in the current session |
| `run_id` | User prompt (optional) | Latest completed run if not specified |
| `target_repo` | User prompt or inferred from context | Current active repo from `context.md` |

---

## Execution Flow

### Step 1 — Gather Artifacts

Leader collects all available run artifacts for the specified scope:

**Session scope** (default): scan `.repos/workspace/<repo-name>/runs/` for all runs from the current session. Collect from each run:
- `comprehension.md`, `spec.md`, `test-spec.md`, `sim-spec.md`
- `implementation.md`, `simulation.md`, `audit.md`
- `log-entry.md`, `docs.md`, `mailbox.md`
- `review.md`

**Single run scope**: collect artifacts from the specified `<run_id>` only.

If no artifacts are found (e.g., no runs have been executed yet), inform the user: "No workflow artifacts found to extract knowledge from. Run a workflow first, then use `/contribute`."

### Step 2 — Create Contribution Run

Generate a contribution-specific run directory:
- Run ID format: `CONTRIBUTE-<timestamp>`
- Create `.repos/workspace/<repo-name>/runs/CONTRIBUTE-<timestamp>/`
- Write `request.md` with scope, source runs, and intent

### Step 3 — Dispatch Distiller

Leader dispatches the **distiller** agent with:
- All collected artifact paths from Step 1
- Path to `.repos/brain/index.md` for duplicate checking
- Path to `.repos/brain/` for existing entry browsing
- Instruction to produce `brain-contributions.md` in the contribution run directory

Distiller follows its standard workflow (`agents/distiller.md`):
1. Scan artifacts for extractable knowledge
2. Apply the 5-question quality gate
3. Apply privacy scrub (`skills/privacy-scrub/SKILL.md`)
4. Check for duplicates against brain index
5. Format entries using `templates/brain-entry.md`
6. Write `brain-contributions.md`

### Step 4 — Present to User (Mandatory Consent)

Leader reads `brain-contributions.md` and presents the FULL content to the user via `AskUserQuestion`:

```
Here's a summary of what StatsClaw learned during this session:

---
[Full content of brain-contributions.md, showing each proposed entry with:
 - What worked well
 - What required manual intervention
 - What domain-specific patterns emerged]
---

Would you like to contribute this to StatsClaw's shared brain?
Your contribution will be publicly visible on GitHub (statsclaw/brain-seedbank)
with your GitHub username as the contributor.

1. Yes — contribute all entries above
2. Yes, but let me pick which ones (partial)
3. No — skip this time
```

**This consent step is MANDATORY and NEVER skipped.** The user always sees exactly what would be shared.

Handle responses:
- **Yes (full)**: mark all entries as approved, proceed to Step 5
- **Partial**: ask which entries to keep, update `brain-contributions.md` to remove declined entries, proceed to Step 5
- **No**: inform the user that no contributions were made, clean up the contribution run directory, stop

### Step 5 — Dispatch Shipper (Brain Upload Only)

Leader dispatches **shipper** with a brain-upload-only task:
- `brain-contributions.md` path
- User approval status
- No target repo push needed (this is brain-only)
- Workspace sync: copy `brain-contributions.md` and a minimal log to the workspace repo

Shipper follows its brain upload workflow (`agents/shipper.md` Step 7b):
1. Fork `statsclaw/brain-seedbank` (if not already forked)
2. Create contribution branch: `contribute/<date>-<short-slug>`
3. Write knowledge entry files to correct directories
4. Update `index.md` on the branch
5. Commit and push to user's fork
6. Create PR from fork to `statsclaw/brain-seedbank`

### Step 6 — Report

Leader reports to the user:
- Number of entries contributed
- PR URL on brain-seedbank (if successful)
- Any entries that were rejected by the quality gate (with reasons)
- Reminder: "An admin will review your contribution. Accepted entries earn badges!"

---

## Output Artifacts

| Artifact | Location | Purpose |
| --- | --- | --- |
| `request.md` | Contribution run directory | Records contribution scope and intent |
| `brain-contributions.md` | Contribution run directory | Proposed entries (from distiller) |
| `shipper.md` | Contribution run directory | Brain-seedbank PR URL and status |

---

## State Model

The `/contribute` command uses a simplified state flow (no full pipeline):

```
BRAIN_CHECK → ARTIFACTS_GATHERED → DISTILLER_DISPATCHED → USER_CONSENT → UPLOAD → DONE
```

| State | Meaning |
| --- | --- |
| `BRAIN_CHECK` | Verifying brain mode and repo availability |
| `ARTIFACTS_GATHERED` | Collected run artifacts for extraction |
| `DISTILLER_DISPATCHED` | Distiller is extracting knowledge |
| `USER_CONSENT` | Waiting for user to approve/decline |
| `UPLOAD` | Shipper is creating brain-seedbank PR |
| `DONE` | Contribution complete (or declined) |

---

## Relationship to Standard Brain Workflow

| Aspect | Standard (brain-sync Phase 3-5) | `/contribute` |
| --- | --- | --- |
| **Trigger** | Automatic after noteworthy workflows | User-invoked at any time |
| **Scope** | Single run | Session-wide or single run |
| **Frequency heuristic** | Leader decides if distiller should run | Always runs (user explicitly asked) |
| **Distiller** | Same agent, same rules | Same agent, same rules |
| **Privacy scrub** | Mandatory | Mandatory |
| **User consent** | Mandatory | Mandatory |
| **Upload** | Via shipper (end of workflow) | Via shipper (standalone dispatch) |
| **Quality gate** | 5-question gate | 5-question gate |

The key difference: `/contribute` bypasses the frequency heuristic because the user has explicitly signaled intent to share knowledge. Everything else (distiller, privacy scrub, quality gate, user consent, shipper upload) is identical.

---

## Edge Cases

- **No artifacts**: If no runs exist in the current session, inform the user and stop.
- **All entries rejected**: If distiller's quality gate rejects all candidates, inform the user: "No entries met the quality threshold for contribution. This is normal for routine changes."
- **Brain repos unavailable**: Warn the user and stop. Do not proceed without brain repos.
- **Already contributed**: If the latest run already has a `brain-contributions.md` from the standard workflow, distiller should check for duplicates against it to avoid re-proposing the same entries.
- **Mixed repos**: If the user worked on multiple target repos in one session, `/contribute` extracts from all of them (scanning each repo's workspace runs).

---

## Non-Blocking Guarantee

Like all brain features, `/contribute` failures are non-blocking:
- If distiller fails: warn the user, stop gracefully
- If shipper fails to create PR: warn the user, note that entries are saved locally in `brain-contributions.md`
- If brain repos can't be cloned: warn and stop
- The user's main workflow is never affected by `/contribute` failures

---

## Example Usage

```
User: /contribute
→ Leader checks brain mode (connected? repos available?)
→ Leader gathers artifacts from all session runs
→ Leader dispatches distiller
→ Distiller extracts 3 entries: a math method, a coding pattern, a validation strategy
→ Leader shows all 3 entries to user
→ User: "Yes, contribute all"
→ Leader dispatches shipper for brain upload
→ Shipper creates PR to statsclaw/brain-seedbank
→ Leader: "3 entries contributed! PR: https://github.com/statsclaw/brain-seedbank/pull/42"
```

```
User: contribute what we learned about panel data
→ Same flow, but distiller focuses extraction on panel-data-related knowledge
→ User reviews, approves 2 of 3 entries
→ PR created with 2 entries
```

```
User: share the lessons from run REQ-20260404-001
→ Leader scopes to single run
→ Same extraction and consent flow
```
