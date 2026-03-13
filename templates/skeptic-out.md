# Skeptic Output

Use this template to define what `skeptic` must produce.

## Required Outputs

- `.statsclaw/runs/<request-id>/review.md`
- append-only mailbox note for verdict and routing

## Required Content

- verdict: `PASS`, `PASS WITH NOTE`, or `STOP`
- major risks
- reason for route-back when review fails

## Success Condition

`lead` and `github` can act on the review without reinterpretation.
