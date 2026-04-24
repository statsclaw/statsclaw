# Brain System — Shared Knowledge for StatsClaw

StatsClaw's Brain system enables knowledge sharing across all users. Techniques, methods, and patterns discovered during workflows are extracted, privacy-scrubbed, and contributed to a shared knowledge repository — making every agent smarter over time.

The Brain is **shared across both runtime distributions** of StatsClaw — `statsclaw/statsclaw` (Claude Code) and `statsclaw/statsclaw-codex` (OpenAI Codex CLI). A contribution from one runtime benefits users of the other.

Everything is **public and transparent** on GitHub.

---

## Overview

The Brain system uses two public repos:

| Repo | Purpose | Access |
| --- | --- | --- |
| [`statsclaw/brain`](https://github.com/statsclaw/brain) | Curated knowledge — agents read from here | Public read; admin-only write |
| [`statsclaw/brain-seedbank`](https://github.com/statsclaw/brain-seedbank) | Contribution staging — users submit PRs here | Public read; fork-based PRs |

**Flow**: User workflow → distiller extracts → user approves → PR to brain-seedbank → admin reviews → transfers to brain

---

## For Users

### Opting In

At the start of your first session with a target repo, StatsClaw asks (on Claude Code via the `AskUserQuestion` tool, on Codex CLI via a numbered-options markdown question from the leader):

> Enable Brain mode?
> 1. Yes — connect to Brain (read + contribute with consent)
> 2. No — isolated mode (current behavior, no brain access)

Your choice is saved in `context.md` (`BrainMode` field). You can change it anytime by saying "turn off brain" or "enable brain".

### What Brain Mode Gives You

**Reading** (automatic): Your agents access collective knowledge entries relevant to your task — better math formulations, coding patterns, validation strategies, DGP designs, and more. Knowledge is searched by tags and delivered to each agent as supplementary context.

**Contributing** (with your explicit consent): After workflows that produce noteworthy techniques, the distiller agent extracts reusable knowledge. You are ALWAYS shown the full extracted content and asked for permission before anything is uploaded. You can:
1. Approve all entries
2. Pick which entries to share
3. Decline entirely

**Nothing is ever uploaded without your explicit approval.**

### What Gets Shared

Only generic, reusable knowledge — never your code, data, or project details:

| Shared | NOT Shared |
| --- | --- |
| Mathematical formulas and methods | Your repo name, org, or username |
| Statistical estimation techniques | File paths or directory structures |
| Algorithm design patterns | Issue/PR numbers or commit SHAs |
| Numerical stability insights | Proprietary code or business logic |
| Validation strategies | Dataset names or column names |
| DGP designs (genericized) | Email addresses or personal info |
| Performance optimization patterns | GitHub URLs or branch names |

All code examples use placeholder names: `my_estimator()`, `helper_function()`, etc.

### Badge Rewards

Accepted contributions earn virtual badges on the [brain CONTRIBUTORS.md](https://github.com/statsclaw/brain/blob/main/CONTRIBUTORS.md):

| Tier | Entries | Badge |
| --- | --- | --- |
| Contributor | 1+ | brain |
| Bronze | 5+ | brain x5 |
| Silver | 15+ | brain x15 |
| Gold | 30+ | brain x30 |

### FAQ

**Q: Can I opt out after opting in?**
A: Yes. Say "turn off brain" at any time. Your `BrainMode` will be set to `"isolated"` and all brain features are disabled.

**Q: Can I remove a contribution I already made?**
A: Open an issue on `statsclaw/brain-seedbank` requesting removal. Admin will handle it.

**Q: How do I contribute knowledge manually?**
A: Use the `/contribute` command at any time during a session. On Claude Code it's a built-in slash command; on Codex CLI it's a prompt file at `~/.codex/prompts/contribute.md` (installed by `install.sh`). Either way, it summarizes what you learned — what worked, what required manual intervention, and what domain-specific patterns emerged — and offers to submit a structured report to `statsclaw/brain-seedbank`. You always review and approve before anything is shared. See `skills/contribute/SKILL.md`.

**Q: Does Brain mode slow down my workflow?**
A: Minimally. Reading adds a few seconds (brain repo pull). Contributing happens at the end of the workflow and only when noteworthy knowledge was produced.

**Q: What if the brain repo is unavailable?**
A: Warning only — your workflow proceeds normally without brain features.

**Q: Will my private code end up in the brain?**
A: No. The distiller agent applies strict privacy scrubbing (see `skills/privacy-scrub/SKILL.md`), the reviewer verifies compliance, and CI on brain-seedbank scans for PII patterns. You also review everything before it's submitted.

**Q: Is the Brain specific to one runtime?**
A: No. Both `statsclaw/statsclaw` (Claude Code) and `statsclaw/statsclaw-codex` (Codex CLI) read from and write to the same brain repos. Contributions and reads are bidirectional.

---

## For Admins

### Reviewing Contributions

1. Watch for PRs on `statsclaw/brain-seedbank`
2. For each PR, verify:
   - All entries pass the 5-question quality gate (reusable, non-trivial, scrubbed, correct, novel)
   - Privacy scrub is thorough (no identifying info — CI helps but isn't foolproof)
   - Entries are well-written and actionable
   - No duplicates of existing brain entries
3. Merge acceptable PRs to brain-seedbank/main
4. Request changes or close PRs that don't meet standards

### Transferring to Brain

After merging a PR on brain-seedbank:

1. Copy the approved entry files to the corresponding directories in `statsclaw/brain`
2. Update `brain/index.md` — append new entries with tags
3. Update `brain/CONTRIBUTORS.md` — add/increment the contributor's badge count
4. Commit and push to brain/main

### Managing Badges

When updating CONTRIBUTORS.md:
- New contributor: add a row with 1 entry and 1 badge
- Existing contributor: increment entry count and badge count
- Check tier thresholds (5 for Bronze, 15 for Silver, 30 for Gold)

---

## Technical Architecture

### Distiller Agent

The distiller (`agents/distiller.md`) runs after scriber:

```
... → scriber → distiller (brain mode only) → ASK USER → reviewer → shipper
```

Distiller:
1. Reads all workflow artifacts
2. Identifies extractable knowledge (mathematical methods, coding patterns, validation strategies, etc.)
3. Applies the 5-question quality gate
4. Applies privacy scrub (`skills/privacy-scrub/SKILL.md`)
5. Checks for duplicates against brain index
6. Writes `brain-contributions.md` to the run directory

### Frequency Heuristic

Distiller is NOT dispatched on every workflow. Leader evaluates:

**Dispatch when ANY is true:**
- Workflow involved mathematical/statistical methods
- Solved a non-trivial bug requiring algorithmic insight
- Implemented a new estimation technique or DGP
- Simulation study produced calibration or convergence findings
- Discovered a significant language-specific pattern

**Skip when ALL are true:**
- Routine change (config, typo, version bump, lint)
- Documentation-only workflow
- Entirely mechanical change (rename, refactor)
- Simplified workflow (workflow 10)

### The `/contribute` Command

Users can invoke `/contribute` at any time to explicitly trigger knowledge extraction and contribution. This is the **user-invocable entry point** for brain contributions — it bypasses the automatic frequency heuristic (since the user has explicitly signaled intent to share) but applies the same quality gate, privacy scrub, and mandatory user consent.

On Claude Code, `/contribute` is a built-in slash command. On Codex CLI, it's a prompt file at `~/.codex/prompts/contribute.md` installed by `install.sh` — invoking it tells the leader to load the corresponding skill.

**Flow**: `/contribute` → leader gathers session artifacts → distiller extracts knowledge → leader presents to user → user approves → shipper creates PR to brain-seedbank

**Trigger phrases**: `/contribute`, `"contribute"`, `"share what I learned"`, `"submit lessons"`, `"add to brain"`

See `skills/contribute/SKILL.md` for the full specification.

### Brain Sync Lifecycle

Full lifecycle managed by `skills/brain-sync/SKILL.md`:

| Phase | When | What |
| --- | --- | --- |
| 0 — Opt-In | Session start | Ask user if BrainMode is empty |
| 1 — Acquire | Repo acquisition | Clone/pull brain and brain-seedbank |
| 2 — Read | Teammate dispatch | Search index, pass relevant entries to agents |
| 3 — Extract | After scriber | Dispatch distiller (if heuristic passes) |
| 4 — Consent | After distiller | Show user, get explicit approval |
| 5 — Upload | Shipper | Create PR to brain-seedbank (if approved) |

### Privacy Scrub Protocol

Defined in `skills/privacy-scrub/SKILL.md`. Four categories:

1. **Identifiers** — GitHub usernames, repo/org names, emails, personal names → removed
2. **Paths & References** — file paths, issue numbers, commit SHAs, URLs → removed
3. **Code References** — function/variable/class names → genericized (e.g., `my_estimator()`)
4. **Data References** — dataset/column names, data file paths → removed

Verified by: distiller (applies), reviewer (verifies), CI (scans for patterns).

### Repository Layout

Both brain repos use the same directory structure:

```
├── planner/
│   ├── math-methods/
│   ├── stat-methods/
│   ├── comprehension-patterns/
│   └── spec-patterns/
├── builder/
│   ├── r-patterns/
│   ├── python-patterns/
│   ├── numerical-stability/
│   ├── api-design/
│   └── performance/
├── tester/
│   ├── validation-strategies/
│   ├── tolerance-calibration/
│   └── benchmark-patterns/
├── simulator/
│   ├── dgp-patterns/
│   ├── harness-designs/
│   ├── convergence-diagnostics/
│   └── scenario-grids/
├── scriber/
│   ├── architecture-patterns/
│   └── documentation-styles/
├── reviewer/
│   ├── convergence-failures/
│   ├── tolerance-inflation/
│   └── quality-patterns/
├── general/
│   ├── language-guides/
│   └── debugging-patterns/
└── index.md
```

Entries are filed by the domain (which agent benefits) and subdomain (topic area).

### Knowledge Entry Format

Each entry follows the `templates/brain-entry.md` template with metadata comments (domain, subdomain, tags, contributor, date) and sections: Summary, Knowledge, When to Use, Example, Pitfalls.

---

## Related Files

| File | Purpose |
| --- | --- |
| `agents/distiller.md` | Distiller agent definition |
| `skills/brain-sync/SKILL.md` | Brain sync lifecycle (5 phases) |
| `skills/privacy-scrub/SKILL.md` | Privacy scrubbing protocol |
| `templates/brain-entry.md` | Knowledge entry template |
| `templates/CONTRIBUTORS.md` | Badge leaderboard template |
| `templates/brain-repo/` | Scaffolding for statsclaw/brain |
| `templates/brain-seedbank-repo/` | Scaffolding for statsclaw/brain-seedbank |
| `skills/contribute/SKILL.md` | User-invocable `/contribute` command |
| `prompts/contribute.md` | Codex slash command entry point for `/contribute` (Codex distribution only) |
| `prompts/brain.md` | Codex slash command entry point for `/brain` (Codex distribution only) |
