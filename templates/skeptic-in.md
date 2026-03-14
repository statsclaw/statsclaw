# Skeptic Input

Use this template to define what `skeptic` may consume.

## Required Inputs (ALL artifacts from BOTH pipelines)

### Code Pipeline artifacts:
- `.statsclaw/runs/<request-id>/spec.md` (theorist → builder input)
- `.statsclaw/runs/<request-id>/implementation.md` (builder output)

### Test Pipeline artifacts:
- `.statsclaw/runs/<request-id>/test-spec.md` (theorist → auditor input)
- `.statsclaw/runs/<request-id>/audit.md` (auditor output)

### Shared artifacts:
- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md`
- `.statsclaw/runs/<request-id>/mailbox.md`

## Optional Inputs

- `.statsclaw/runs/<request-id>/docs.md`
- actual diff from target repo

## Required Decisions

- whether pipeline isolation was maintained (no cross-contamination)
- whether the two pipelines converge on consistent results
- whether the evidence chain is strong enough to externalize the change
