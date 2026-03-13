# Profile: TypeScript Package

## Repo Markers

Detect this profile when the target repository contains:

- `package.json` (required)
- `tsconfig.json` (required)
- `src/` directory

## Validation Commands

| Stage | Command | Notes |
| --- | --- | --- |
| Type check | `tsc --noEmit` | Compile without output to verify types |
| Unit tests | `npm test` | Runs the project's test script |
| Lint | `npx eslint .` | Code quality and style |
| Build | `npm run build` | Compile to output (dist/) |
| Format check | `npx prettier --check .` | When Prettier is configured |

If the project uses `pnpm`, substitute `pnpm` for `npm` in all commands.

## Documentation

- **API docs**: TSDoc comments (`/** */`) on all exported functions, classes, and types
- **Types**: TypeScript declarations serve as living documentation; prefer explicit types over `any`
- **README**: `README.md` at the repo root
- **CHANGELOG**: `CHANGELOG.md` for user-visible changelog

## Common Tooling

- `npm` or `pnpm` — package manager
- `typescript` — compiler and type checker
- `vitest` or `jest` — test framework
- `eslint` — linter
- `prettier` — formatter (when configured)
- `tsup` or `tsc` — bundler / build tool

## Builder Notes

- Use strict TypeScript: do not use `any` unless absolutely necessary and justified in a comment.
- Respect the existing `tsconfig.json` strictness settings; do not relax them.
- Export types alongside runtime values so consumers get full type information.
- Place tests adjacent to source (`*.test.ts`) or under `tests/` depending on project convention.
- Do not add new dependencies to `package.json` without noting it in the mailbox for lead review.
- Prefer `const` over `let`; avoid `var`.
- Use async/await over raw Promises; handle errors explicitly.

## Auditor Notes

- `tsc --noEmit` must pass with zero errors; type check failures are always blockers.
- `npm test` must pass with zero failures.
- `eslint` must pass with zero errors; warnings should be reviewed and reported.
- If the project has a build step, confirm `npm run build` succeeds.
- Check that all new exported symbols have TSDoc comments.
- Report test coverage when the project has coverage tooling configured.
