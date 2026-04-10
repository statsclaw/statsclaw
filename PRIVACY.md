# Privacy Policy

**Last updated:** April 10, 2026

## Overview

StatsClaw is an open-source workflow framework for Claude Code. It runs entirely on your local machine and does not collect, transmit, or store any user data.

## What StatsClaw Does NOT Do

- **No data collection**: StatsClaw does not collect personal information, usage analytics, telemetry, or any other data from users.
- **No network requests**: The framework itself makes no outbound network requests. All network activity (GitHub API calls, git operations) is initiated by Claude Code on your behalf using your own credentials.
- **No tracking**: No cookies, fingerprinting, or any form of user tracking.
- **No third-party services**: StatsClaw does not integrate with or send data to any third-party analytics, advertising, or data processing services.

## What Runs Locally

- All orchestration logic (agent dispatch, state management, signal handling) runs in your Claude Code session.
- Runtime state (`.repos/workspace/`) is stored on your local filesystem.
- Credentials are detected from your local environment (GITHUB_TOKEN, SSH keys, credential helpers) and never stored or transmitted by StatsClaw.

## Brain System (Opt-In Only)

The optional Brain knowledge-sharing system allows users to contribute anonymized, genericized learnings to a shared repository (`statsclaw/brain`). This is:

- **Strictly opt-in**: Users must explicitly enable Brain mode and approve every contribution.
- **Privacy-scrubbed**: All contributions pass through automated PII removal (repository names, file paths, usernames, proprietary code, data column names, and identifying information are stripped).
- **User-controlled**: Users review the exact content before submission and can decline at any time.

## GitHub Interactions

When you use StatsClaw to work on GitHub repositories, all interactions (cloning, pushing, creating PRs, commenting on issues) use your own GitHub credentials and are governed by [GitHub's Privacy Policy](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).

## Claude Code

StatsClaw runs within Anthropic's Claude Code. Your interactions with Claude Code are governed by [Anthropic's Privacy Policy](https://www.anthropic.com/privacy).

## Changes to This Policy

Updates to this policy will be reflected in this file with an updated date. As an open-source project, all changes are tracked in version control.

## Contact

For privacy-related questions, open an issue at [github.com/statsclaw/statsclaw/issues](https://github.com/statsclaw/statsclaw/issues) or start a discussion in the [Discussions](https://github.com/statsclaw/statsclaw/discussions) section.
