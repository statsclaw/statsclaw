# Skill: Progress Bar

Renders a visual progress bar to the user showing the current workflow state. Leader MUST call this after every `status.md` update to keep the user informed.

---

## When to Display

- After every state transition in `status.md`
- When dispatching a teammate (show which stage is active)
- When a signal (HOLD, BLOCK, STOP) interrupts the workflow
- At workflow completion (DONE)

---

## Progress Bar Format

Leader outputs the progress bar directly as text (markdown) to the user. No tool call needed — just print it.

### Full Pipeline (Workflows 1, 2, 4, 5)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress                                          [3/7] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [▶] Specs ── [ ] Build/Test        │
│       ── [ ] Docs ── [ ] Review ── [ ] Ship                        │
│                                                                     │
│  ▶ Active: planner producing specs...                              │
│  ⏱ Elapsed: 2m 15s                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Docs-Only Pipeline (Workflow 3)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress                                          [2/5] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [▶] Specs ── [ ] Docs/Implement    │
│       ── [ ] Review                                                 │
│                                                                     │
│  ▶ Active: planner producing specs...                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Simulation Pipeline (Workflows 11, 12)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress (simulation)                             [4/7] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [▶] Build/Sim/Test    │
│       ── [ ] Docs ── [ ] Review ── [ ] Ship                        │
│                                                                     │
│  ▶ Active (parallel):                                               │
│    ├─ builder: implementing estimator in worktree...               │
│    ├─ simulator: implementing DGP + harness in worktree...         │
│    └─ tester: preparing validation scenarios...                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Simulation-Only Pipeline (Workflow 12)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress (simulation-only)                        [4/7] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [▶] Sim/Test          │
│       ── [ ] Docs ── [ ] Review ── [ ] Ship                        │
│                                                                     │
│  ▶ Active (parallel):                                               │
│    ├─ simulator: implementing DGP + harness in worktree...         │
│    └─ tester: preparing validation scenarios...                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Lightweight Pipelines (Workflows 6, 7, 8)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress (lightweight)                            [1/2] │
│                                                                     │
│  [▶] Validate ── [ ] Done                                          │
│                                                                     │
│  ▶ Active: tester running validation...                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Simplified Pipeline (Workflow 10 — small requests)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress (simplified)                             [2/4] │
│                                                                     │
│  [✔] Plan ── [▶] Implement ── [ ] Validate ── [ ] Ship             │
│                                                                     │
│  ▶ Active: builder implementing changes...                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## State-to-Step Mapping

### Full Pipeline

| State | Step # | Label | Symbol |
| --- | --- | --- | --- |
| `CREDENTIALS_VERIFIED` | 1 | Credentials | `[✔]` when passed |
| `PLANNED` | 2 | Plan | `[✔]` when impact.md written |
| `SPEC_READY` | 3 | Specs | `[✔]` when planner completes |
| `PIPELINES_COMPLETE` | 4 | Build/Test | `[✔]` when builder + tester complete |
| `DOCUMENTED` | 5 | Docs | `[✔]` when scriber completes |
| `REVIEW_PASSED` | 6 | Review | `[✔]` when reviewer passes |
| `DONE` | 7 | Ship | `[✔]` when shipper completes (or skipped) |

### Docs-Only Pipeline

| State | Step # | Label |
| --- | --- | --- |
| `CREDENTIALS_VERIFIED` | 1 | Credentials |
| `PLANNED` | 2 | Plan |
| `SPEC_READY` | 3 | Specs |
| `DOCUMENTED` | 4 | Docs/Implement |
| `REVIEW_PASSED` | 5 | Review |

### Simulation Pipeline (Workflow 11)

| State | Step # | Label |
| --- | --- | --- |
| `CREDENTIALS_VERIFIED` | 1 | Credentials |
| `PLANNED` | 2 | Plan |
| `SPEC_READY` | 3 | Specs |
| `PIPELINES_COMPLETE` | 4 | Build/Sim/Test |
| `DOCUMENTED` | 5 | Docs |
| `REVIEW_PASSED` | 6 | Review |
| `DONE` | 7 | Ship |

### Simulation-Only Pipeline (Workflow 12)

| State | Step # | Label |
| --- | --- | --- |
| `CREDENTIALS_VERIFIED` | 1 | Credentials |
| `PLANNED` | 2 | Plan |
| `SPEC_READY` | 3 | Specs |
| `PIPELINES_COMPLETE` | 4 | Sim/Test |
| `DOCUMENTED` | 5 | Docs |
| `REVIEW_PASSED` | 6 | Review |
| `DONE` | 7 | Ship |

### Simplified Pipeline

| State | Step # | Label |
| --- | --- | --- |
| `PLANNED` | 1 | Plan |
| `PIPELINES_COMPLETE` | 2 | Implement |
| `REVIEW_PASSED` | 3 | Validate |
| `DONE` | 4 | Ship |

---

## Symbols

| Symbol | Meaning |
| --- | --- |
| `[✔]` | Step completed |
| `[▶]` | Step in progress |
| `[ ]` | Step pending |
| `[✘]` | Step failed (BLOCK/STOP) |
| `[⏸]` | Step paused (HOLD — waiting for user) |

---

## Interrupt Display

When a signal interrupts the workflow, the progress bar shows the interruption:

### HOLD (waiting for user)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress                                          [3/7] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [⏸] Specs ── [ ] Build/Test        │
│       ── [ ] Docs ── [ ] Review ── [ ] Ship                        │
│                                                                     │
│  ⏸ HOLD: planner needs clarification (see question below)          │
└─────────────────────────────────────────────────────────────────────┘
```

### BLOCK (validation failed)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress                                          [4/7] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [✘] Build/Test        │
│       ── [ ] Docs ── [ ] Review ── [ ] Ship                        │
│                                                                     │
│  ✘ BLOCKED: tester found test failures → respawning builder (1/3)  │
└─────────────────────────────────────────────────────────────────────┘
```

### STOP (quality gate failed)

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress                                          [6/7] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [✔] Build/Test        │
│       ── [✔] Docs ── [✘] Review ── [ ] Ship                        │
│                                                                     │
│  ✘ STOPPED: reviewer found isolation breach → respawning builder     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Completion Display

```
┌─────────────────────────────────────────────────────────────────────┐
│  StatsClaw Progress                                          [7/7] │
│                                                                     │
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [✔] Build/Test        │
│       ── [✔] Docs ── [✔] Review ── [✔] Ship                        │
│                                                                     │
│  ✔ DONE — All changes shipped successfully                          │
│  Summary: 3 files changed, PR #42 opened                           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Sequential Stage Indicator

When builder completes and tester runs next, show the active stage:

```
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [▶] Build/Test        │
│                                                                     │
│  ▶ Active: builder: implementing changes in worktree...             │
└─────────────────────────────────────────────────────────────────────┘
```

After builder completes:

```
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [▶] Build/Test        │
│                                                                     │
│  ▶ Active: tester: running test scenarios...                        │
└─────────────────────────────────────────────────────────────────────┘
```

In simulation workflows (11), builder and simulator run in parallel:

```
│  [✔] Credentials ── [✔] Plan ── [✔] Specs ── [▶] Build/Test        │
│                                                                     │
│  ▶ Active (parallel):                                               │
│    ├─ builder: implementing changes in worktree...                  │
│    └─ simulator: implementing DGP in worktree...                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Rule

Leader MUST output the progress bar as markdown text directly after each state transition. This is a **text output**, not a tool call. Leader constructs the bar from `status.md` state and the active workflow type.

**Minimum frequency**: After EVERY `status.md` write. Optionally also when dispatching a teammate (to show the "Active" line changing).

**No separate tool needed** — leader simply prints the formatted text block above as part of its response.
