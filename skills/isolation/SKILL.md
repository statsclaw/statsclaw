# Shared Skill: Two-Pipeline Isolation Protocol

This protocol governs how teammates are isolated from each other in the two-pipeline architecture. There are two levels of isolation: **worktree isolation** (filesystem-level) and **pipeline isolation** (information-level).

---

## Pipeline Isolation (Information-Level)

The two-pipeline architecture enforces strict information barriers between the code pipeline and the test pipeline:

### Code Pipeline (builder)
- **Receives**: `spec.md` (from planner), `request.md`, `impact.md`
- **Never receives**: `test-spec.md`, `sim-spec.md`, `audit.md`, `simulation.md`
- **Produces**: `implementation.md`, code changes, unit tests

### Test Pipeline (tester)
- **Receives**: `test-spec.md` (from planner), `request.md`, `impact.md`
- **Never receives**: `spec.md`, `sim-spec.md`, `implementation.md`, `simulation.md`
- **Produces**: `audit.md`, validation evidence

### Simulation Pipeline (simulator) — workflows 11, 12 only
- **Receives**: `sim-spec.md` (from planner), `request.md`, `impact.md`
- **Never receives**: `spec.md`, `test-spec.md`, `implementation.md`, `audit.md`
- **Produces**: `simulation.md`, DGP code, simulation harness code

### Bridge (planner)
- **Receives**: `request.md`, `impact.md`, target repo read access
- **Produces**: `spec.md`, `test-spec.md`, and `sim-spec.md` (simulation workflows only)
- **Ensures**: all specs are independently sufficient — none requires reading another

### Convergence Point (reviewer)
- **Receives**: ALL artifacts from ALL pipelines
- **Only agent that sees all sides**
- **Verifies**: convergence, isolation integrity, and cross-consistency across all pipelines

### Isolation Enforcement

Leader is responsible for enforcing pipeline isolation at dispatch time:

1. When dispatching builder: include `spec.md` in the prompt, NEVER mention `test-spec.md` or `sim-spec.md`
2. When dispatching tester: include `test-spec.md` in the prompt, NEVER mention `spec.md`, `sim-spec.md`, or `implementation.md`
3. When dispatching simulator: include `sim-spec.md` in the prompt, NEVER mention `spec.md`, `test-spec.md`, or `implementation.md`
4. When dispatching reviewer: include ALL artifacts — reviewer is the convergence point

**Why**: If builder knows what tests will be run, it can "teach to the test" — passing validation without actually satisfying the requirement. If tester knows how the code works, it can't provide truly independent verification. If simulator knows the implementation details, it can't provide independent evaluation of finite-sample properties. The multi-pipeline design ensures adversarial verification: all sides must independently converge on the same correct result.

---

## Worktree Isolation (Filesystem-Level)

Use `isolation: "worktree"` when dispatching any teammate that **writes** to the target repository:

- **builder** — implements code and test changes
- **simulator** — implements DGP and simulation harness code
- **scriber** — updates documentation, examples, tutorials, and vignettes

Worktree isolation gives each writing teammate its own working copy of the repository. This prevents concurrent writers from interfering with each other and ensures that partial work from one teammate never corrupts another's checkout.

## When NOT to Use Worktree Isolation

Do **not** use worktree isolation for non-writing teammates:

- **tester** (runs validation commands on the merged checkout — see timing note below)
- **reviewer** (reviews the evidence chain, never writes to the target repo)
- **planner** (produces spec artifacts, does not modify target repo files)
- **shipper** (interacts with the remote via git/gh commands on the main checkout)

### Tester Timing: Sequential After Writers

Tester is dispatched **after all writing teammates (builder, simulator) complete and merge back**. This ensures tester always validates the fully merged code:

1. **Writing phase**: Builder (and simulator, in simulation workflows) implement code in their worktrees. In simulation workflows, builder and simulator run in parallel.
2. **Merge-back**: Writing teammates' worktrees merge back into the main checkout when they complete.
3. **Validation phase**: Leader dispatches tester. Tester runs its validation commands on the **merged checkout** containing all new code.

The key principle: **writers finish first, tester validates the merged result.** This eliminates the race condition where tester might validate pre-change code.

---

## Write Surface Enforcement

Every writing teammate receives an explicit **write surface** in its dispatch prompt. The write surface lists the exact files and directories that the teammate is allowed to modify.

### Rules

1. A teammate may **only** create, edit, or delete files within its assigned write surface.
2. **No two writing teammates may have overlapping write surfaces.** If builder owns `src/` and scriber owns `docs/`, neither may touch the other's directory.
3. If a teammate discovers that it needs to modify a file outside its surface, it MUST NOT do so. Instead, it appends a message to `mailbox.md` describing the needed change and continues with its own surface.
4. Only **leader** may mutate `status.md` and files under `locks/` (at `.repos/workspace/<repo-name>/runs/<request-id>/locks/`). Teammates must never write to these paths.
5. Teammates may write their own output artifact (e.g., `implementation.md`, `docs.md`) to the run directory. This is always within their allowed surface.

### Overlap Detection

Leader is responsible for ensuring non-overlapping surfaces before dispatch. If a request requires two writers to touch the same file (e.g., builder and scriber both need to edit a README that contains code examples), leader must serialize them: dispatch the first writer, wait for completion, then dispatch the second with the updated state.

---

## Worktree Merge-Back

After a writing teammate completes in its worktree:

1. **Leader reads the output artifact** to confirm the teammate succeeded (no HOLD or BLOCK).
2. **Leader verifies the write surface** — only expected files were modified.
3. **Changes from the worktree are merged back** into the main checkout. The Agent tool handles this automatically when the worktree teammate returns.
4. If merge conflicts arise (e.g., two writing teammates were dispatched in parallel on non-overlapping surfaces but git detects structural conflicts), leader must resolve them before dispatching the next downstream teammate.
5. After merge-back, the worktree is no longer active. Subsequent teammates (tester, reviewer) operate on the merged main checkout.

**Important for two-pipeline architecture**: Tester is always dispatched AFTER all writing teammates' worktrees merge back, so it validates the actual merged code — but it does so using test-spec.md scenarios, not knowledge of what builder or simulator changed.

---

## Summary

| Teammate | Pipeline | Writes to target repo? | Use worktree? | Receives |
| --- | --- | --- | --- | --- |
| planner | Bridge | No | No | request.md, impact.md |
| builder | Code | Yes | Yes | spec.md (NEVER test-spec.md or sim-spec.md) |
| tester | Test | No (runs commands) | No | test-spec.md (NEVER spec.md or sim-spec.md) |
| simulator | Simulation | Yes | Yes | sim-spec.md (NEVER spec.md or test-spec.md) — workflows 11, 12 only |
| scriber (scriber) | All | Yes | Yes | ALL artifacts (reads everything to produce process record) |
| scriber (implementer) | Docs | Yes | Yes | spec.md (NEVER test-spec.md) — replaces builder in docs-only workflow |
| reviewer | Convergence | No (reviews only) | No | ALL artifacts |
| shipper | — | No (git/gh commands) | No | review.md, credentials.md |
| leader | Control | No (runtime only) | N/A | ALL artifacts |
