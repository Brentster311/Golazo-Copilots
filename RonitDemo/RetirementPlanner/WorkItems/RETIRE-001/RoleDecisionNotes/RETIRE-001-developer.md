# Developer Decision Notes: RETIRE-001

## Work Item
RETIRE-001 - MVP Retirement Planner

## Implementation Summary

### TDD Approach Followed
1. **Red Phase**: Created 30 test cases before any production code
2. **Green Phase**: Implemented production code to make tests pass
3. **Refactor Phase**: Code reviewed, no refactoring needed (clean implementation)

### Files Created

#### Source Files
| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point |
| `src/models/user_profile.py` | `UserProfile` and `ProjectionResult` dataclasses |
| `src/repository/base_repository.py` | `IDataRepository` interface and `RepositoryError` |
| `src/repository/json_file_repository.py` | JSON file persistence implementation |
| `src/services/retirement_calculator.py` | Business logic for projections |
| `src/ui/main_window.py` | Tkinter GUI implementation |

#### Test Files
| File | Tests |
|------|-------|
| `tests/test_retirement_calculator.py` | 16 calculator tests |
| `tests/test_json_file_repository.py` | 6 repository tests |
| `tests/test_user_profile_validation.py` | 8 validation tests |

### Decisions Made

#### 1. Validation Location
**Decision**: Implemented validation in `UserProfile.__post_init__`.

**Rationale**:
- Single source of truth for valid data
- Catches invalid data at construction time
- Tester recommended this approach

#### 2. Repository Error Handling
**Decision**: Return `None` for corrupted/missing files, don't raise.

**Rationale**:
- Graceful degradation (app starts fresh if file is corrupt)
- Test cases allowed either approach
- Simpler user experience

#### 3. Save Strategy
**Decision**: Save on explicit button click + auto-save on window close.

**Rationale**:
- Per Reviewer recommendation
- Prevents accidental data loss
- Gives user control

#### 4. UI Layout
**Decision**: Simple form-based layout with clear sections.

**Rationale**:
- MVP focus - functionality over aesthetics
- All acceptance criteria visible
- Clear status indication (on-track vs gap)

#### 5. Encoding Fix
**Decision**: Recreated `retirement_calculator.py` with ASCII-only characters.

**Rationale**:
- Original file had Unicode multiplication symbols (x) causing encoding errors
- Replaced with ASCII `*` for cross-platform compatibility

## Test Results
- **30 tests passing**
- All acceptance criteria covered
- Edge cases from Reviewer handled

## Known Deviations from Design
None - implementation matches design exactly.

## Technical Debt
None introduced. Code is clean and well-structured.
