**Status**: BACKLOG (Deferred until spend-safety MVP goals are met)

**User Story**
- Title: Enforce planner-to-POA requirement conversion in workflow
- As a: project owner
- I want: planner direction items converted into explicit POA acceptance criteria before development
- So that: critical product requirements cannot be lost as assumptions
- Out of scope:
  - Replacing Golazo workflow engine
  - Rewriting historical completed work items
  - Custom external policy services
- Assumptions:
  - Assumption (explicit): Interface type is workflow/documentation contract enforcement.
  - Assumption (explicit): Enforcement occurs via role guidance and required-output checks.
  - Assumption (explicit): Existing work item lifecycle remains intact.
- Acceptance Criteria (bulleted, testable):
  - POA checklist includes mandatory mapping of planner in-scope themes to acceptance criteria or deferred stories.
  - Work item role notes include a requirement-coverage section with pass/defer status.
  - Missing mapping is detectable during QA review and blocks forward transition until addressed.
  - Documentation includes explicit example converting architecture direction into testable story criteria.
  - New work items created after this change demonstrate mapped coverage.
- Non-functional requirements:
  - Enforcement adds minimal overhead to story creation.
  - Guidance remains clear and concise for repeatability.
- Telemetry / metrics expected:
  - Count of planner requirements mapped vs deferred per initiative.
  - Number of QA blocks due to missing requirement mapping.
- Rollout / rollback notes:
  - Rollout as process hardening update for new initiatives.
  - Rollback by making mapping advisory-only if flow is excessively burdensome.

## Reprioritization Note (2026-05-12)
- This work item is intentionally deferred until spend-safety MVP goals are shipped.
- Priority sequence ahead of this item: FRC-005, FRC-006, FRC-007, FRC-014, FRC-015.
- Scope remains valid and will be resumed after those items.
