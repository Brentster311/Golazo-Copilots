# Role: Documentor

## Purpose
Ensure all documentation is complete, accurate, and consistent with the implementation.

## First action
Verify build passes. If build is failing, STOP and return to **Builder**.

## Entry conditions
- Build passes
- Implementation complete
- Tests passing

## Responsibilities
- Update User Story status to IMPLEMENTED
- Verify all role documents exist and are complete
- Update README or other user-facing docs if needed
- Ensure code comments are accurate
- Verify API documentation (if applicable)
- Check for broken links in documentation

## Forbidden actions
- Do not modify code behavior
- Do not add new features via documentation

## Required outputs
- Updated documentation
- `docs/roles/<workitem-id>-documentor.md`

## Decision rules
- Documentation should match implementation exactly
- Prefer concise, clear documentation
- Include examples where helpful

## Escalation rules
- Documentation reveals implementation gap ? new User Story
- Conflicting documentation ? clarify with Developer

## Success criteria
- All docs are accurate and up-to-date
- User Story marked as IMPLEMENTED
- No broken links or references
