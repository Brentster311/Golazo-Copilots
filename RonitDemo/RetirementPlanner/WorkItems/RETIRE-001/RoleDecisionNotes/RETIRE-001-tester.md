# Tester Decision Notes: RETIRE-001

## Work Item
RETIRE-001 - MVP Retirement Planner

## Decisions Made

### 1. Test Structure
**Decision**: Organize tests by component (Calculator, Repository, Validation) plus Integration.

**Rationale**:
- Matches proposed code structure
- Easy to run specific test suites
- Clear ownership of test failures

### 2. Validation Testing Approach
**Decision**: Test validation at model level (dataclass `__post_init__`).

**Rationale**:
- Validation errors caught early
- Single source of truth for valid data
- UI doesn't need to duplicate validation logic

### 3. Edge Cases from Review
**Decision**: Explicitly included edge cases identified by Reviewer:
- TC-04: Current age equals retirement age (0 years)
- TC-15: Surplus scenario (ahead of goal)
- TC-06: Large numbers handling

**Rationale**: Reviewer identified these; Tester ensures they're tested.

### 4. Manual vs Automated Tests
**Decision**: UI tests are manual; all business logic tests are automated.

**Rationale**:
- Tkinter UI testing is complex and brittle
- Business logic is where bugs are most costly
- Manual tests cover UX aspects automated tests can't

### 5. Error Handling Strategy
**Decision**: Repository can either return None OR raise `RepositoryError` on corruption.

**Rationale**:
- Both approaches are acceptable
- Test verifies app doesn't crash
- Developer can choose implementation

## Test Coverage Analysis

| Acceptance Criteria | Test Cases | Coverage |
|---------------------|------------|----------|
| AC-1 (Ages) | TC-01,02,03,04,21,22 | ? Full |
| AC-2 (Savings) | TC-05,06,23 | ? Full |
| AC-3 (Contribution) | TC-07,08,24 | ? Full |
| AC-4 (Desired income) | TC-09,10,25 | ? Full |
| AC-5 (Calculate) | TC-11,12,13 | ? Full |
| AC-6 (On-track status) | TC-14,15,16 | ? Full |
| AC-7 (Persistence) | TC-17,18,19,20,26,27 | ? Full |

## Alternatives Considered

### Alternative: UI Automation with pyautogui
**Deferred**: Adds complexity and flakiness. Manual tests sufficient for MVP.

### Alternative: Property-based testing (Hypothesis)
**Deferred**: Would increase test coverage but adds dependency. Consider for future.

### Alternative: Mutation testing
**Deferred**: Overkill for MVP. Good for ensuring test quality later.

## Tradeoffs Accepted
- Manual UI tests require human effort
- Float comparison uses tolerance (not exact equality)
- Some edge cases may be discovered in production

## Known Limitations
- No performance benchmarks (NFR-4 tested manually)
- No GUI automated tests
- No security-specific tests (RETIRE-001 has no encryption)

## Risks

| Risk | Mitigation |
|------|------------|
| Float precision issues | Tests use tolerance (abs() < threshold) |
| Test data coupling | Use explicit values, not magic numbers |
| Missed edge cases | Review coverage thoroughly |

## Open Items for Developer
- Implement validation in `UserProfile.__post_init__`
- Implement `RepositoryError` exception class
- Ensure UTF-8 encoding is explicit in file operations
