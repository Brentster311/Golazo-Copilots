# GCP-0020: Developer Notes

## Overview
Implemented blocking mode for role notes enforcement, replacing the warning-only approach from GCP-0019.

## Implementation Decisions

### 1. Parameter Addition
Added `force_without_notes: bool = False` parameter to `gcp_transition()` function signature.

**Rationale**: Provides explicit escape hatch for edge cases while making the blocking behavior clear in the API.

### 2. Consent Integration
Reused existing `skip_role` consent action for the force mechanism.

**Rationale**: No new consent actions needed - `skip_role` semantically covers "skipping the requirement to write role notes."

### 3. Error Response Structure
Enhanced error response with:
- `missing_file`: Expected path for the role notes file
- `hint`: Actionable instruction for the AI

**Example**:
```python
{
    "success": False,
    "error": "Role notes required before transitioning from project-owner-assistant. Create file: GCP-0020-project-owner-assistant.md in RoleDecisionNotes/",
    "missing_file": "GCP-0020/RoleDecisionNotes/GCP-0020-project-owner-assistant.md",
    "hint": "Create role notes file before transition, or use force_without_notes=True after gcp_consent(action='skip_role')"
}
```

### 4. Backward Transition Handling
Blocking check applies to backward transitions too - checks the OUTGOING role (the one being left).

**Rationale**: Ensures decisions made in current role are documented before moving to any other role, regardless of direction.

### 5. Test File Updates
Updated 4 test files with helper function and role note creation:
- `test_gcp_transition.py`: 23 tests updated + 6 new blocking tests
- `test_gcp_consent.py`: 3 tests updated
- `test_gcp012_backward.py`: 4 tests updated
- `test_gcp_status.py`: 2 tests updated

## Test Results
**102 tests passing** - all existing functionality preserved, new blocking behavior verified.

## New Tests Added
1. `test_transition_blocked_when_notes_missing` - Verifies transition fails without notes
2. `test_transition_allowed_when_notes_exist` - Verifies transition succeeds with notes
3. `test_force_without_notes_requires_consent` - Verifies force requires prior consent
4. `test_force_with_consent_succeeds` - Verifies force works after consent
5. `test_error_includes_expected_file_path` - Verifies actionable error message
6. `test_backward_transition_checks_outgoing_role` - Verifies backward transitions also blocked

## Why Blocking Instead of Warning
Evidence from this session:
- GCP-0019 implemented warning-only approach
- 127 retroactive role notes had to be created because warnings were ignored
- AI assistants don't self-enforce warnings - they need blocking gates
- This proves "blocking > warning" for AI workflow enforcement

## Files Modified
- `src/golazo_copilot/tools/gcp_transition.py` - Added blocking logic
- `tests/test_gcp_transition.py` - Added helpers and 6 new tests
- `tests/test_gcp_consent.py` - Added helpers and role note creation
- `tests/test_gcp012_backward.py` - Added helpers and role note creation
- `tests/test_gcp_status.py` - Added helpers and role note creation

## Implementation Complete
- ✅ Blocking logic implemented
- ✅ Force mechanism with consent
- ✅ All 102 tests passing
- ✅ TDD approach followed (tests written before implementation)
