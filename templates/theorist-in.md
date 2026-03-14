# Theorist Input

Use this template to define what `theorist` may consume.

## Required Inputs

- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/impact.md`
- `.statsclaw/runs/<request-id>/mailbox.md`

## Optional Inputs

- user-provided paper, PDF, appendix, LaTeX, or notes
- active package context
- target repo source files (read-only, for understanding current behavior)

## Required Decisions

- whether the method/requirement is specified clearly enough to implement without invention
- how to decompose the requirement into an implementation spec and a test spec
- what edge cases and invariants to include in the test spec
- whether the two specs are independently sufficient
