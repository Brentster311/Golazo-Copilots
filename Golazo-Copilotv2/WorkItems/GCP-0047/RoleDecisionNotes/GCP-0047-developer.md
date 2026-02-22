# GCP-0047 Developer Decision Notes

## Approach
TDD red-green-refactor cycle. Wrote 31 tests first (red), then implemented all changes (green).

## Changes Made

### Python code
- **transitions.py**: Added `"project-owner-assistant"` to `TRANSITIONS["retrospective"]` — enables retro→POA closure transition

### Role files (× 3 copies: source defaults, `.github/roles/`, `golazo-copilot/.github/roles/`)
1. **documenter.md**: Removed build check from First Action/Entry Conditions; removed IMPLEMENTED status from Responsibilities/Success Criteria
2. **developer.md**: Added `git checkout -b <workitem-id>` branch creation as step 1 of First Action
3. **builder.md**: Removed "Before Developer" branch creation section and Git Operations (Branch Creation) subsection
4. **project-owner-assistant.md**: Added `## Closure` section (final commit, AC validation, pending work items, terminal instruction); added `closure.md` to Required Outputs
5. **quality-assurance.md**: Removed design-quality bullets (risk coverage, operability, cost/performance, naming clarity, folder structure); removed Capability Registry section
6. **architect.md**: Added design-quality bullets from QA; added `### Security Review` subsection (data exposure, auth, attack surface, dependency risk)
7. **domain-expert.md**: Added scope boundary statement distinguishing domain knowledge from architectural decisions

### Tests
- **test_gcp047_role_improvements.py**: 31 new tests covering all 17 test cases from the design phase
- **test_best_practices.py**: Removed `"quality-assurance"` from `ROLES_WITH_REGISTRY` (capability registry removed from QA)

## Test Results
- **Before**: 252 passed, 6 skipped (baseline)
- **After**: 281 passed, 6 skipped (31 new - 2 removed from ROLES_WITH_REGISTRY)
- **0 regressions**

## Key Decisions
- Used `importlib.resources.files` to read role files from package defaults (consistent with existing test patterns)
- Needed to re-install editable package (`pip install -e`) because data files aren't live-linked in the venv — they copy on install
- Boundary test for domain-expert checks for "scope boundary" OR ("structural" AND "architectural" AND "not") to allow natural phrasing
