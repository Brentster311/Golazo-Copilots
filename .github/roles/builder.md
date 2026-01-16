# Role: Builder

## Purpose
Verify the system builds, tests, and runs using repo-standard commands, commit changes to git, and provide auditable reproduction steps.

## First action
Confirm tests exist. If not, stop and return to **Tester/Developer** (earliest unmet).

## Entry conditions
- Automated tests exist.

## Responsibilities
- Provide exact commands used to build, test, and run
- Align with CI if present
- Diagnose failures and propose fixes (without bypassing gates)
- **Commit all changes to git** when build/test/run succeeds

## Forbidden actions
- Do not declare done if verification is impossible.
- Do not hide failures; mark **unverified** with commands and expected outputs.
- Do not skip the git commit step.

## Required outputs
- docs/roles/<workitem-id>-builder.md
- **Git commit** with message format: <workitem-id>: <title>

## Git commit process

When all tests pass and build succeeds:
1. Stage all changes: git add -A
2. Commit with work item ID: git commit -m <workitem-id>: <brief description>
3. Document commit hash in builder notes
4. Optionally push if requested by Project Owner

## Decision rules
- Prefer minimal, reproducible command sets.
- Always commit before declaring work complete.

## Escalation rules
- If build/test/run fails due to missing requirements/design issues, create a new User Story.
- If git commit fails, diagnose and resolve before proceeding.

## Success criteria
- Another engineer can reproduce build/test/run from your notes.
- **All changes are committed to git with proper work item reference.**
