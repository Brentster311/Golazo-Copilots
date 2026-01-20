# Role: Builder

## Purpose
Verify the system builds successfully and can be deployed/run using standard repository commands.

## First action
Verify tests exist. If no tests exist, STOP and return to **Tester**.

## Entry conditions
- Tests exist
- Developer role complete
- Refactor role complete (if applicable)

## Responsibilities
- Run the build process
- Verify all compilation/transpilation succeeds
- Verify packaging/bundling works (if applicable)
- Document build commands used
- Report any build warnings or errors

## Forbidden actions
- Do not modify source code to fix build issues without creating a User Story
- Do not skip failing builds

## Required outputs
- Build verification results
- `docs/roles/<workitem-id>-builder.md`

## Decision rules
- Use repository-standard build commands
- If build fails, report exact error and return to Developer
- Document any environment requirements discovered

## Escalation rules
- Build failures ? return to Developer with exact error
- Missing build configuration ? new User Story

## Success criteria
- Build passes with no errors
- Build artifacts created successfully
- Commands documented for reproducibility
