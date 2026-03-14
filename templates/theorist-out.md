# Theorist Output

Use this template to define what `theorist` must produce.

## Required Outputs

- `.statsclaw/runs/<request-id>/spec.md` (for code pipeline / builder)
- `.statsclaw/runs/<request-id>/test-spec.md` (for test pipeline / auditor)
- append-only mailbox note with handoff summaries for both pipelines

## Required Content in spec.md

- notation
- mathematical statement or algorithmic description
- computational steps
- assumptions
- numerical constraints
- input validation requirements
- output contract
- API surface
- explicit `HOLD` if implementation would require invention

## Required Content in test-spec.md

- behavioral contracts (observable behaviors)
- concrete test scenarios (inputs, expected outputs, tolerances)
- edge case scenarios (boundary conditions, invalid inputs)
- regression scenarios (if fixing a bug)
- property-based invariants (mathematical properties)
- cross-reference benchmarks (if applicable)
- suggested validation commands

## Pipeline Isolation Rules

- spec.md MUST NOT contain test cases, expected outputs, or verification strategies
- test-spec.md MUST NOT contain implementation details, algorithm steps, or code structure guidance
- Each spec must be independently sufficient — neither requires reading the other

## Success Condition

- `builder` can implement the method from spec.md without guessing missing math or needing test-spec.md
- `auditor` can design and run validation from test-spec.md without needing to know how the code works
