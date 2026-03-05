# GCP-0019: Project Owner Assistant Decision Notes

## Request Analysis

User identified a process violation: role transitions were being made without creating required decision notes. In GCP-0014, 8 of 9 role notes were missing.

## Scope Decision

**Warning vs Blocking:**
- Chose **warning** approach over blocking because:
  1. Blocking could be too disruptive during learning/adoption
  2. Some roles genuinely have "No findings" which might not warrant a file
  3. Warning creates visibility without stopping work

**Why this is a single story:**
- One outcome: transition warns about missing notes
- Single verification point: file exists or not
- Clear acceptance criteria (5 items, within limit)

## Assumptions Made

1. **Naming convention**: `<workitem-id>-<role>.md` is already documented in role files
2. **Location**: `WorkItems/<id>/RoleDecisionNotes/` is the standard path
3. **Special cases**: `refactor-expert` uses `refactor.md` suffix (shorter name)

## Questions NOT Asked (implementation details)

- Specific file path construction (follows existing patterns)
- Warning message format (matches existing ICON_WARN style)

## Acceptance Criteria Validation

All 5 criteria are:
- ✅ Testable (can verify file check, warning, display)
- ✅ Independent (no dependencies on other stories)
- ✅ Demonstrable (user sees warning in output)
