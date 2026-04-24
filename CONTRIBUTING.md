# Contributing to StatsClaw

Thank you for your interest in StatsClaw! We welcome contributions of all kinds — from bug reports and feature ideas to code and documentation.

## Two Runtime Distributions, One Project

StatsClaw ships in two interchangeable runtime distributions that follow the same protocol, the same 9-agent architecture, and the same shared brain:

| Repo | Runtime |
| --- | --- |
| [`statsclaw/statsclaw`](https://github.com/statsclaw/statsclaw) | Anthropic [Claude Code](https://claude.ai/code) |
| [`statsclaw/statsclaw-codex`](https://github.com/statsclaw/statsclaw-codex) | OpenAI [Codex CLI](https://github.com/openai/codex) |

The contribution flow is identical on both repos. File issues and PRs on whichever repo matches the runtime you use. Protocol-level changes (agents, skills, profiles, templates, brain entry schemas) are mirrored between the two — open a paired PR or note the cross-distribution implication in the PR description.

## Ways to Contribute

### 1. Submit Ideas and Requests

No coding required! You can help by:

- **Feature requests** — [Open a feature request issue](../../issues/new?template=feature-request.yml)
- **Paper-to-Package requests** — Have a paper with a statistical method? [Submit it](../../issues/new?template=paper-to-package.yml) and we'll work on turning it into a package
- **Bug reports** — [Report a bug](../../issues/new?template=bug-report.yml)
- **Discussions** — Join [Discussions](https://github.com/statsclaw/statsclaw/discussions) (hosted on the upstream repo, used by both distributions) to brainstorm ideas, ask questions, or share use cases

### 2. Contribute Code

#### Getting Started

1. Fork the repository (whichever of the two matches your runtime)
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   ```
3. Switch to the `dev` branch (all development happens here):
   ```bash
   git checkout dev
   ```
4. Make your changes
5. Push and open a Pull Request against `dev`

#### What Can You Work On?

Areas shared by both distributions:

- **Agent definitions** (`agents/`) — Improve agent behavior, add new capabilities
- **Language profiles** (`profiles/`) — Add or improve language-specific rules (shared verbatim — open a paired PR on the other repo)
- **Skills** (`skills/`) — Add new workflow skills or improve existing ones
- **Templates** (`templates/`) — Improve runtime artifact templates (shared verbatim — open a paired PR on the other repo)
- **Brain system** (`agents/distiller.md`, `skills/brain-sync/`, `skills/privacy-scrub/`) — Improve knowledge extraction and privacy scrubbing
- **Documentation** — Improve README, AGENTS.md / CLAUDE.md, add examples, fix typos

Areas specific to the Codex distribution (`statsclaw/statsclaw-codex` only):

- **Dispatch & wrapper scripts** (`scripts/`) — Improve `dispatch.sh`, `worktree.sh`, `detect-credentials.sh`, `loop.sh`
- **Slash command prompts** (`prompts/`) — Improve `/contribute`, `/loop`, `/ship-it`, `/review`, `/patrol`, `/simulate`, `/brain`
- **Installer** (`install.sh`, `uninstall.sh`) — Improve installation UX on Codex CLI
- **Codex profile config** (`codex-config.example.toml`) — Tune sandboxing, approval policies, and model choices per agent

Check [issues labeled `good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) for beginner-friendly tasks.

#### Code Guidelines

- Keep changes focused — one PR per feature or fix
- Follow existing patterns in the codebase
- Agent definitions use Markdown — keep them clear and structured
- Test your changes with **Claude Code or Codex CLI** (whichever the repo targets) before submitting
- All PRs must pass CI checks (cross-reference integrity, markdown lint, YAML validation, structure validation)

#### Keeping Parity Across Distributions

When a change to the protocol, an agent, a skill, a profile, a template, or a brain entry schema lands on one repo, the same change should land on the other. The Codex repo also re-applies the Codex-equivalent substitutions (`Agent` tool → `scripts/dispatch.sh`, `AskUserQuestion` → numbered-options markdown question, `Skill` tool → file-reference load, `${CLAUDE_PLUGIN_ROOT}` → `${STATSCLAW_CODEX_ROOT}`, etc.).

When you open a PR that touches a shared file, please:

1. Note the cross-repo implication in the PR description.
2. Either open the paired PR yourself, or flag it so a maintainer can.
3. For protocol/agent/skill changes that originate on one repo, the maintainers will sync them to the other and bump the appropriate semver component.

#### Branching & Merge Rules

- **Two branches**: `main` (stable) and `dev` (active development)
- All contributions go to `dev` — never push directly to `main`
- When `dev` is stable, maintainers merge `dev` → `main` via squash PR
- Releases are tagged on `main`
- See [Branch Protection](.github/BRANCH_PROTECTION.md) for full details

### 3. Add a Language Profile

StatsClaw supports multiple languages through profiles. To add a new one:

1. Create `profiles/<language>.md` following the pattern in existing profiles
2. Include: file patterns, build commands, test commands, packaging conventions
3. Open a PR with example usage
4. **Open a paired PR on the other distribution** so the profile lands on both `statsclaw/statsclaw` and `statsclaw/statsclaw-codex`

### 4. Share Use Cases

Tried StatsClaw on your research? We'd love to hear about it:

- Share your experience in [Discussions > Show and Tell](https://github.com/statsclaw/statsclaw/discussions/categories/show-and-tell)
- Include what worked well and what could be improved
- Mention which runtime you used (Claude Code or Codex CLI)
- This directly influences our [Roadmap](ROADMAP.md)

### 5. Contribute Knowledge to the Brain

StatsClaw has a shared knowledge system where techniques, methods, and patterns discovered during workflows are extracted and shared with all users. The brain is **shared across both distributions** — a contribution from a Codex session benefits Claude Code users and vice-versa.

You can contribute in two ways:

**Automatic** — When you use StatsClaw with Brain mode enabled, after noteworthy workflows the **distiller agent** automatically extracts reusable knowledge and asks for your consent.

**Manual** — Run the built-in `/contribute` command at any time during a session. It summarizes what you learned — what worked, what required manual intervention, and what domain-specific patterns emerged — into a structured report.

Either way, the flow is the same:

1. The distiller agent extracts reusable knowledge from your session
2. You review the extracted entries and **approve or decline** — nothing is shared without your explicit consent
3. Approved entries are submitted as a PR to [`statsclaw/brain-seedbank`](https://github.com/statsclaw/brain-seedbank)
4. Admin reviews and transfers accepted entries to [`statsclaw/brain`](https://github.com/statsclaw/brain)

Every accepted contribution earns a virtual badge on the [Contributors leaderboard](https://github.com/statsclaw/brain/blob/main/CONTRIBUTORS.md).

**What gets shared**: Mathematical methods, coding patterns, validation strategies, simulation designs — all genericized with no project-specific information.

**What never gets shared**: Repo names, file paths, usernames, proprietary code, data column names, or any identifying information.

See [Brain System Documentation](.github/BRAIN.md) for full details.

## Development Setup

StatsClaw is a framework for AI coding CLIs. To develop, install at least one of the supported runtimes:

- [Claude Code](https://claude.ai/code) — for contributions to `statsclaw/statsclaw`
- [Codex CLI](https://github.com/openai/codex) — for contributions to `statsclaw/statsclaw-codex`

Then:

1. Clone the repo you're contributing to
2. Open it in your CLI of choice
3. Test changes by running workflows against a target repository

## Pull Request Process

1. Describe what your PR does and why
2. Reference any related issues
3. Keep the diff minimal — don't include unrelated changes
4. If your change touches a file shared across both distributions, flag the cross-repo implication
5. Be responsive to review feedback

## Community Guidelines

- Be respectful and constructive
- Focus on the idea, not the person
- Help newcomers get oriented
- Write in English or Chinese — both are welcome

## Questions?

- Open a [Discussion](https://github.com/statsclaw/statsclaw/discussions) for general questions
- File an [Issue](../../issues) for bugs or specific feature requests
- Visit [statsclaw.ai](https://statsclaw.ai) for project overview

---

Thank you for helping StatsClaw grow!
