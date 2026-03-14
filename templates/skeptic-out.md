# Skeptic Output

Use this template to define what `skeptic` must produce.

## Required Outputs

- `.statsclaw/runs/<request-id>/review.md`
- append-only mailbox note for verdict and routing

## Required Content

- pipeline isolation verification (did builder see test-spec.md? did auditor see spec.md?)
- cross-specification comparison (spec.md vs test-spec.md consistency)
- convergence analysis (where both pipelines agree/disagree)
- verdict: `PASS`, `PASS WITH NOTE`, or `STOP`
- major risks
- reason for route-back when review fails

## Success Condition

`lead` and `github` can act on the review without reinterpretation. The verdict reflects confidence that BOTH pipelines independently arrived at a correct result.
