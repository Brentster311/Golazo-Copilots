# Retrospective

Work Item: AGL-001
Role: retrospective

## What went well
- End-to-end workflow executed with all role artifacts created.
- Requirements were clarified early (interface/platform/persistence), reducing rework.
- TDD cycle was followed (red -> green) with high coverage (99%).
- Capability impact analysis was consulted in QA, Architect, and Developer phases.

## What didn't go well
- Builder phase encountered packaging failure due setuptools auto-discovery including WorkItems.
- Branch context drift occurred: initial commit landed on FRC-001 before being applied to AGL-001.
- DoR verification reference file (.github/copilot-instructions.md) was missing, requiring manual artifact validation.

## Action items
- Add explicit setuptools package discovery configuration to Python starter templates used with Golazo workflows.
- Add a pre-commit/Builder check to assert current branch equals work item id before commit.
- Add a lightweight DoR fallback checklist in role instructions for cases where referenced policy file is missing.
- Add builder guidance to exclude generated artifacts via .gitignore defaults in new workspaces.

## Metrics
- Workflow quality metric:
  - Number of role-transition failures due missing required outputs (target: 0)
- Build reliability metric:
  - Number of packaging failures due discovery/config issues (target: 0)
- Branch hygiene metric:
  - Number of commits made on non-workitem branch during active work item (target: 0)
- Validation metric:
  - Test pass rate and coverage threshold compliance (target: 100% pass, >=70% per module)
