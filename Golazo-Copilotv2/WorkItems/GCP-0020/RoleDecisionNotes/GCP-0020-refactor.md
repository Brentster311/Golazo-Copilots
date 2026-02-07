# GCP-0020: Refactor Expert Notes

## Code Review Summary
Code quality is good. Minimal refactoring needed.

## Changes Made
1. **Whitespace cleanup**: Removed double blank line in `gcp_transition.py` (line 119)

## Refactoring Considered but Deferred

### 1. Consolidate Test Helper Functions
**Observation**: `create_role_notes()` helper is duplicated in 4 test files:
- `test_gcp_transition.py`
- `test_gcp_consent.py`
- `test_gcp012_backward.py`
- `test_gcp_status.py`

**Decision**: Defer to future work item. Would require:
- Creating `tests/conftest.py` with shared fixtures
- Potentially creating `tests/helpers.py` for utility functions
- This is test organization, not source code quality

### 2. Extract Consent Handling Logic
**Observation**: Similar pattern for checking/consuming consent appears in DoR gate and role notes checks.

**Decision**: Keep as-is. The two cases have different:
- Actions (`skip_dor` vs `skip_role`)
- Error messages
- Return structures

Abstracting would add complexity without benefit.

### 3. Role Notes Path Construction
**Observation**: `ROLE_SUFFIX_MAP` and path construction could be encapsulated in a class.

**Decision**: Keep as-is. Current functional approach is clear and simple. No need to introduce abstraction for 2 small functions.

## Conclusion
Code is clean and readable. Only cosmetic whitespace cleanup applied. All 102 tests passing.

## No Behavior Changes
✅ Confirmed - all tests pass before and after refactoring
