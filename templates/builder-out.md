# Builder Output (Code Pipeline)

Use this template to define what `builder` must produce after implementation.

## Required Outputs

- target source and test changes inside the assigned write surface
- `.statsclaw/runs/<request-id>/implementation.md`
- append-only mailbox note for interface changes, blockers, or handoff

## Required Content

- changed files and why
- behavior changes
- unit tests written (based on spec.md, NOT test-spec.md)
- design choices and rationale
- unresolved implementation risks

## Pipeline Isolation Rules

- implementation.md MUST NOT reference test-spec.md
- unit tests are based on spec.md only — they complement (not duplicate) auditor's independent validation

## Success Condition

`skeptic` can cross-compare implementation.md against audit.md to verify that the code pipeline and test pipeline converged independently.
