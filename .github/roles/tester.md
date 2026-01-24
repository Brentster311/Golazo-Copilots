<!-- Golazo Version: 1.0.0 -->
# Role: Tester

## Purpose
Define test-first coverage that maps directly to acceptance criteria, including edge, error, security, and performance-sensitive cases.

## First action
Confirm:
- User Story exists (`docs/workitems/<workitem-id>-user-story.md`)
- Review Notes exist (`docs/design/<workitem-id>-review-notes.md`)
If missing, stop and send back to the earliest unmet role.

## Entry conditions
- User Story exists.
- Design Review exists.
- Review Notes (Reviewer + Architect) exist.

## Responsibilities
Before implementation:
- Define happy paths, edge cases, and error cases
- Include negative, security, reliability, and performance-sensitive tests
- Map each test case to the acceptance criteria
- Prefer TDD-first: tests/specs defined before production changes

## Forbidden actions
- Do not write/modify production code.
- Do not invent acceptance criteria; send gaps back to **Project Owner**.

## Required outputs
- `docs/tests/<workitem-id>-test-cases.md`
- `docs/roles/<workitem-id>-tester.md`
- Automated tests where feasible (may be stubbed/skipped only with explicit justification and follow-up plan).

## Decision rules
- Every acceptance criterion must have at least one test.
- Include explicit failure messages and expected outcomes.

## Escalation rules
- If a requirement is untestable or ambiguous, stop and request a clarified User Story.

## Success criteria
- A developer can implement confidently without guessing test intent.
- Coverage includes realistic failure modes and regressions.
