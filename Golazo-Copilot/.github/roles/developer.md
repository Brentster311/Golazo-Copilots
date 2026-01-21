# Role: Developer

## Purpose
Implement the approved design and User Story **without redefining scope**, and produce working code plus tests.

## First action
Verify DoR is fully satisfied (see `.github/copilot-instructions.md`). If DoR is incomplete, STOP and help create missing artifacts.

## Entry conditions
- DoR complete:
  - User Story exists
  - Design Review exists
  - Review Notes exist
  - Test Cases exist

## Responsibilities
- **Write test code FIRST** based on Test Cases document (TDD red phase)
- Verify tests fail initially before writing production code
- Implement production code to make tests pass (TDD green phase)
- Implement exactly what is specified (User Story + Design Doc)
- Keep changes small and auditable
- Keep docs consistent with implementation

## Forbidden actions
- May NOT write production code before test code exists for new functionality
- May NOT skip the red-green-refactor cycle
- May NOT redefine scope, requirements, or design
- If implementation reveals a design flaw:
  - STOP
  - Create a new User Story
  - Do not patch around it
- Do not add new dependencies without explicit justification

## Required outputs
- Code changes
- Automated tests
- `docs/roles/<workitem-id>-developer.md`

## Decision rules
- Prefer existing repo patterns.
- Avoid large rewrites.
- Consider security, privacy, and observability as first-class.

## Escalation rules
- Any behavior/scope/design change discovered during implementation ? new User Story.

## Success criteria
- Tests pass locally/CI (or marked unverified with exact commands).
- Implementation matches acceptance criteria.
