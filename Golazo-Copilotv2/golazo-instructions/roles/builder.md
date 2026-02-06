<!-- Golazo Version: 2.8.0 -->
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

### Version Management (before Commit)
Determine appropriate version bump based on changes in this work item:

| Change Type | Bump | Example |
|-------------|------|---------|
| Breaking/incompatible API changes | MAJOR | 2.x.x → 3.0.0 |
| New features, backwards compatible | MINOR | 2.8.x → 2.9.0 |
| Bug fixes, backwards compatible | PATCH | 2.8.0 → 2.8.1 |

**Version update process:**
1. Review changes to determine bump type (ask PO if unclear)
2. Locate ALL version declarations in the project (search for current version string)
3. Update ALL locations consistently - never update just one
4. Verify version consistency before committing

**Common version locations** (language-dependent):
- Package manifests (package.json, pyproject.toml, *.csproj, pom.xml, Cargo.toml)
- Source code version constants (__version__, VERSION, version.h)
- Documentation headers, README badges
- API response headers or metadata endpoints

**Version update is REQUIRED when:**
- New features are added (MINOR)
- Breaking changes are made (MAJOR)
- Bug fixes are released (PATCH)

**Version update is SKIPPED when:**
- Changes are documentation-only with no code changes
- Changes are internal refactoring with no user-visible impact
- Work item explicitly states "no version bump"

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
- `WorkItems/<workitem-id>/RoleDecisionNotes/<workitem-id>-builder.md`

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
