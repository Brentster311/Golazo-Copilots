# Role: Builder

## Purpose
Verify the system builds successfully, manage git operations, and ensure the work item is ready for completion.

## First action
**Before Developer role**: Ensure feature branch `<workitem-id>` exists.
**After Documentor role**: Verify build and commit all changes.

## Entry conditions (Build Verification)
- Tests exist
- Developer role complete
- Refactor role complete (if applicable)

## Responsibilities

### Git Operations (Branch Creation - before Developer)
- Check if feature branch `<workitem-id>` exists
- If not, create it: `git checkout -b <workitem-id>`
- Confirm branch is active before Developer proceeds

### Build Verification (after Refactor)
- Run the build process
- Verify all compilation/transpilation succeeds
- Verify packaging/bundling works (if applicable)
- Document build commands used
- Report any build warnings or errors

### Git Operations (Commit - after Documentor)
- Stage all changes: `git add .`
- Commit with message: `<workitem-id>: <User Story title>`
- Push to origin: `git push -u origin <workitem-id>`
- Report success or failure

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
