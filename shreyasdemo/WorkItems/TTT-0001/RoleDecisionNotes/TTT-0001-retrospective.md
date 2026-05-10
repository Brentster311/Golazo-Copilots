# TTT-0001 Retrospective

## What went well
- Scope was kept intentionally small (single MVP user story), which enabled quick delivery.
- Acceptance criteria were concrete and directly mappable to automated tests.
- Test-first implementation for core game logic produced a stable rules engine quickly.
- Capability registry was consulted and updated to reflect real project files.

## What didn't go well
- Bootstrap created a placeholder capability that failed registry validation (`src/example.py` missing).
- Express profile sequencing excluded some roles, but QA still expected a design-doc input, causing a temporary workflow mismatch.
- `pytest` was unavailable in the environment, requiring fallback to `unittest`.

## Action items
- Update bootstrap template so `capabilities.yaml` is either empty by default or points to existing files.
- Align express-profile role gates with role input requirements (or auto-generate minimal design-doc when required).
- Add an explicit environment prerequisites checklist in builder notes template (e.g., testing tool availability).
- Add a profile-specific transition helper to avoid trial-and-error on next allowed roles.

## Metrics
- Workflow friction count per work item (missing-input or invalid-transition incidents).
- Time-to-first-passing-test after developer role starts.
- Capability validation pass rate on first builder attempt.
- Percentage of work items that complete without manual prerequisite artifact remediation.
