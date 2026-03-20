# [YYYY-MM-DD] — [Short Description]

> Run: `[request-id]` | Profile: [profile] | Verdict: [PASS / PASS WITH NOTE]

## What Changed

[Concise summary of what was done and why — 2-5 sentences covering the user's request and the approach taken.]

## Files Changed

| File | Action | Description |
| --- | --- | --- |
| [path] | [created / modified / deleted] | [one-line description] |

## Process Record

This section captures the full workflow history: what was proposed, what was tested, what problems arose, and how they were resolved. It provides a complete audit trail for traceability and post-mortem analysis.

### Proposal (from planner)

**Implementation spec summary** (from `spec.md`):
- [Key algorithm/approach proposed]
- [Critical design choices made in the spec]

**Test spec summary** (from `test-spec.md`):
- [Key test scenarios defined]
- [Tolerances and acceptance criteria specified]
- [Benchmarks or cross-references used]

### Implementation Notes (from builder)

- [Key implementation decisions]
- [Deviations from spec and why]
- [Unit tests written]

### Validation Results (from tester)

**Per-Test Result Table** (copy from `audit.md` — every test with its specific metrics):

| Test | Metric | Expected | Actual | Tolerance | Rel. Error | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| [test name] | [metric name] | [expected value] | [actual value] | [tolerance] | [rel. error %] | [PASS/FAIL] |

Summary: [N] tests executed, [N] passed, [N] failed.

**Before/After Comparison Table** (copy from `audit.md` — how key metrics changed):

| Metric | Before (old) | After (new) | Change | Interpretation |
| --- | --- | --- | --- | --- |
| [metric name] | [old value] | [new value] | [signed change] | [improvement / regression / neutral] |

[If no code changes or new feature with no baseline, note "N/A — [reason]".]

Additional notes:
- [Validation commands run and their outcomes]
- [Edge case results]
- [Any warnings or deferred items]

### Problems Encountered and Resolutions

[Record EVERY problem that occurred during the workflow, including BLOCK signals, HOLD signals, respawns, and how each was resolved. If no problems occurred, write "No problems encountered."]

| # | Problem | Signal | Routed To | Resolution |
| --- | --- | --- | --- | --- |
| 1 | [description of the problem] | [BLOCK / HOLD / STOP] | [teammate] | [how it was resolved] |

### Review Summary (from reviewer, if available)

[If `review.md` exists, fill in. If scriber runs before reviewer in the standard flow, write "Pending — reviewer review follows scriber." Shipper teammate will update this section before commit if needed.]

- **Pipeline isolation**: [verified / breach detected / pending]
- **Convergence**: [converged / diverged — details / pending]
- **Tolerance integrity**: [all tolerances match test-spec.md / discrepancies found / pending]
- **Verdict**: [PASS / PASS WITH NOTE — include notes / pending]

## Design Decisions

[Key decisions made during implementation and why. Include alternatives considered and reasons for the chosen approach. This section is the "design note" — it captures rationale that would otherwise be lost.]

1. **[Decision]**: [Rationale]
2. **[Decision]**: [Rationale]

## Handoff Notes

[What the next developer needs to know about these changes. Gotchas, edge cases, known limitations, areas that may need future attention.]
