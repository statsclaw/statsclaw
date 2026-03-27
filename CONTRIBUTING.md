# Contributing to StatsClaw

Thank you for your interest in StatsClaw! We welcome contributions of all kinds — from bug reports and feature ideas to code and documentation.

## Ways to Contribute

### 1. Submit Ideas and Requests

No coding required! You can help by:

- **Feature requests** — [Open a feature request issue](../../issues/new?template=feature-request.yml)
- **Paper-to-Package requests** — Have a paper with a statistical method? [Submit it](../../issues/new?template=paper-to-package.yml) and we'll work on turning it into a package
- **Bug reports** — [Report a bug](../../issues/new?template=bug-report.yml)
- **Discussions** — Join [Discussions](../../discussions) to brainstorm ideas, ask questions, or share use cases

### 2. Contribute Code

#### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/statsclaw.git
   cd statsclaw
   ```
3. Create a branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes
5. Push and open a Pull Request

#### What Can You Work On?

- **Agent definitions** (`agents/`) — Improve agent behavior, add new capabilities
- **Language profiles** (`profiles/`) — Add or improve language-specific rules
- **Skills** (`skills/`) — Add new workflow skills
- **Templates** (`templates/`) — Improve runtime artifact templates
- **Documentation** — Improve README, add examples, fix typos

Check [issues labeled `good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) for beginner-friendly tasks.

#### Code Guidelines

- Keep changes focused — one PR per feature or fix
- Follow existing patterns in the codebase
- Agent definitions use Markdown — keep them clear and structured
- Test your changes with Claude Code before submitting

### 3. Add a Language Profile

StatsClaw supports multiple languages through profiles. To add a new one:

1. Create `profiles/<language>.md` following the pattern in existing profiles
2. Include: file patterns, build commands, test commands, packaging conventions
3. Open a PR with example usage

### 4. Share Use Cases

Tried StatsClaw on your research? We'd love to hear about it:

- Share your experience in [Discussions > Show and Tell](../../discussions/categories/show-and-tell)
- Include what worked well and what could be improved
- This directly influences our [Roadmap](ROADMAP.md)

## Development Setup

StatsClaw is a framework for Claude Code. To develop:

1. Install [Claude Code](https://claude.ai/code)
2. Clone this repository
3. Open it in Claude Code
4. Test changes by running workflows against a target repository

## Pull Request Process

1. Describe what your PR does and why
2. Reference any related issues
3. Keep the diff minimal — don't include unrelated changes
4. Be responsive to review feedback

## Community Guidelines

- Be respectful and constructive
- Focus on the idea, not the person
- Help newcomers get oriented
- Write in English or Chinese — both are welcome

## Questions?

- Open a [Discussion](../../discussions) for general questions
- File an [Issue](../../issues) for bugs or specific feature requests
- Visit [statsclaw.ai](https://statsclaw.ai) for project overview

---

Thank you for helping StatsClaw grow!
