# Skill: triage — Intake and Workflow Routing Agent

Triage turns an unstructured user request into a structured run contract. It is the normal first step for any non-trivial request and is responsible for selecting or detecting the active project profile.

For any non-trivial request, `triage` must create the runtime artifacts. If `request.md` and `status.md` are not written, triage is not complete.

---

## Triggers

Invoke `triage` when the user:

- asks for a new feature
- asks for a bug fix
- asks for an end-to-end implementation
- asks what needs to be done
- asks for a release-ready workflow
- provides a large or ambiguous request

---

## Tools

Read, Write, Edit

---

## Workflow

### Step 1 — Auto-create local runtime if needed

Read `.statsclaw/CONTEXT.md` if it exists.

If it does not exist:

- create `.statsclaw/`
- create `.statsclaw/packages/`, `.statsclaw/runs/`, `.statsclaw/logs/`, `.statsclaw/tmp/`
- create `.statsclaw/CONTEXT.md` from `templates/context.md`

Do not ask the user to perform setup steps manually.

### Step 2 — Identify the target project

Extract the target repo or project path from the user message first.

If no explicit path is given:

- infer from available workspace context if there is one clear candidate
- otherwise ask one concise clarification question

The user should not need to pre-fill project files before work can begin.

### Step 3 — Create or update the project context automatically

Create `.statsclaw/packages/<project-slug>.md` when it does not exist.

Fill it automatically with:

- package path
- package name or repo name
- detected project type
- primary language
- detected project profile
- best-effort validation commands
- docs surface inferred from the repo

Then update `.statsclaw/CONTEXT.md` so `ActivePackage` points to this file.

### Step 4 — Detect or confirm the project profile

Read the project context and determine:

- project type
- primary language
- project profile

If the profile is missing, detect it from repo markers:

- `DESCRIPTION` + `NAMESPACE` → `r-package`
- `pyproject.toml` / `setup.py` → `python-package`
- `package.json` + `tsconfig.json` → `typescript-package`
- `.do` / `.ado` / `.mata` files or `stata.toc` → `stata-project`

If detection is still ambiguous, raise a **HOLD** and ask the user.

### Step 5 — Structure the request

Extract:

- user goal
- problem statement
- target project
- acceptance criteria
- out-of-scope items
- risks or ambiguities

If any of these are missing and matter to delivery, raise a **HOLD** and ask the user.

### Step 6 — Select the workflow path

Decide which agents are needed:

- `scout` for package mapping or any non-trivial change
- `theorist` for mathematical or algorithmic logic
- `builder` for code changes
- `auditor` for validation
- `scribe` for public-facing docs, examples, or tutorials
- `skeptic` for final review before shipping
- `release` only if the user asks to ship, commit, version, or prepare a PR

Also decide whether the request needs:

- a docs build
- a typecheck
- a tutorial render
- a packaging or release check

based on the active project profile and project-context commands.

### Step 7 — Create or update the run

Use `templates/request.md` and save it to:

```text
.statsclaw/runs/<request-id>/request.md
```

Also create or update:

```text
.statsclaw/runs/<request-id>/status.md
```

Minimum status fields:

- Request ID
- Current State: `TRIAGED`
- Current Owner: `scout` or next selected agent
- Next Step
- Active Profile

Update `.statsclaw/CONTEXT.md` so `ActiveRun` points to the run.

Writing both files is mandatory before handing off. Do not continue to later agents without them.

### Step 8 — Handoff

Return a one-paragraph summary that states:

- what the request is
- which workflow path was selected
- what the next agent should do

---

## Quality Checks

- Do not start implementation directly from a vague request
- Do not skip acceptance criteria for non-trivial work
- Do not mark `release` required unless the user explicitly asked for a ship action
- Do not leave the profile undefined if the workflow depends on tooling conventions
- Do not ask the user to manually create runtime files if triage can infer them
- Do not leave `request.md` or `status.md` unwritten for a non-trivial request
- Make the next step explicit

---

## Output Format

- `.statsclaw/runs/<request-id>/request.md`
- `.statsclaw/runs/<request-id>/status.md`
- short routing summary
