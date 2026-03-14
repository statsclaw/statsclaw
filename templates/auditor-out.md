# Auditor Output

Use this template to define what `auditor` must produce.

## Required Outputs

- `.statsclaw/runs/<request-id>/audit.md`
- append-only mailbox note for failing checks, routes, or handoff

## Required Content

- test scenarios executed (from test-spec.md) with exact results
- commands run (exact commands, not paraphrased)
- exact evidence (full output, not summaries)
- edge case results
- benchmark comparison results (if applicable)
- failures and routes
- validation verdict (PASS or BLOCK)
- environment info

## Pipeline Isolation Rules

- audit.md MUST NOT reference spec.md or implementation.md
- validation is based on test-spec.md scenarios and profile commands only
- auditor verifies WHAT the code does, not HOW it does it

## Success Condition

`skeptic` can cross-compare audit results against both spec.md and test-spec.md to verify convergence between the two pipelines.
