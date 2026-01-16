# Tester Role Notes: WIP-001

## Work Item
WIP-001 - Organize Photos by Date/Time

## Decisions Made

1. **Created 15 test cases covering all acceptance criteria**
   - Each AC has at least one test case
   - Mix of happy path, edge case, error case, performance, and security

2. **Test case naming convention**
   - TC-XX format for easy reference
   - Each case maps to specific acceptance criteria

3. **TDD approach**
   - Test cases defined before implementation
   - Developer can implement tests first

4. **Test data strategy**
   - Sample photos needed with known EXIF dates
   - Photos without EXIF for fallback testing
   - Mix of supported and unsupported file types

## Alternatives Considered

| Decision | Alternative | Why Rejected |
|----------|-------------|--------------|
| Unit + Integration tests | Only integration | Unit tests catch bugs earlier |
| Manual test data | Generated test data | Real photos more realistic |

## Tradeoffs Accepted
- Performance test (TC-14) may need adjustment based on hardware
- Some tests require manual setup of test fixtures

## Known Limitations
- TC-05 (permission test) may be difficult on Windows
- TC-14 (1000 photos) requires test data generation

## Risks
- LOW: Test data maintenance as features evolve

## Coverage Summary

| Category | Count |
|----------|-------|
| Happy Path | 7 |
| Edge Case | 4 |
| Error Case | 2 |
| Performance | 1 |
| Security | 1 |
| **Total** | **15** |

## Acceptance Criteria Coverage

| AC | Test Cases | Covered |
|----|------------|---------|
| AC-1 | TC-01, TC-02, TC-03 | ? |
| AC-2 | TC-04, TC-05 | ? |
| AC-3 | TC-06, TC-07, TC-08 | ? |
| AC-4 | TC-09, TC-10 | ? |
| AC-5 | TC-11, TC-12 | ? |
| AC-6 | TC-13 | ? |
