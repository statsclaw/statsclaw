# Profile: typescript-package

Use this profile for TypeScript packages, libraries, and applications.

## Repo Markers

- `package.json`
- `tsconfig.json`
- `pnpm-lock.yaml`
- `yarn.lock`
- `package-lock.json`

## Typical Validation Commands

- `npm test` or `pnpm test`
- `npm run lint` or `pnpm lint`
- `npm run typecheck` or `pnpm typecheck`
- `tsc --noEmit`

Use only commands that exist in the target repo or are explicitly configured in the project context.

## Documentation Conventions

- `README.md`
- `docs/`
- generated API docs when the repo uses them
- storybook or demo apps when relevant

## Common Tooling

- `npm`
- `pnpm`
- `yarn`
- `eslint`
- `tsc`
- `vitest` / `jest`

## Builder Notes

- preserve existing module system and import conventions
- keep types aligned with implementation changes
- update tests and public docs for API changes

## Auditor Notes

- run configured test, lint, and typecheck commands
- build docs or demo artifacts when required by the repo
- treat build failures and type errors as blockers
