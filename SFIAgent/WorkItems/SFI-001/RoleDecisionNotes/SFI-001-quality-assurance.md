# SFI-001 Quality Assurance Decision Notes

## Date: 2026-02-03

### Design Review Summary

**Verdict**: APPROVED with recommendations

The design is solid and implementable. Key strengths:
- Clear separation of concerns
- Proven authentication approach
- Sensible phased rollout

### Recommendations Made

| ID | Recommendation | Rationale |
|----|----------------|-----------|
| R1 | Custom exception classes | Better error handling for consumers |
| R2 | Cache key strategy | Ensure unique, debuggable cache files |
| R3 | Optional discovery module | Keep core lightweight |
| R4 | Token refresh handling | Prevent failures in long operations |
| R5 | Cache file locking | Prevent corruption with concurrent use |
| R6 | Connection test utility | Simplify debugging |

None are blockers - can be addressed during development.

### Test Strategy Decisions

#### 1. Framework Choice
**Decision**: pytest + pytest-mock + responses
**Rationale**: Industry standard, good async support if needed later, excellent mocking.

#### 2. Integration Test Handling
**Decision**: Mark with `@pytest.mark.integration`, skip if no az login
**Rationale**: Allow full test suite to run in CI without Azure credentials.

#### 3. Coverage Target
**Decision**: 80% line coverage
**Rationale**: Achievable without excessive mocking, catches major gaps.

#### 4. Test Organization
**Decision**: Mirror source structure
```
tests/
├── test_auth.py
├── test_client.py
├── test_cache.py
├── test_endpoints/
│   ├── test_action_items.py
│   └── test_discovery.py
└── conftest.py
```

### Edge Cases Identified

1. Empty API responses
2. Malformed JSON
3. Token expiration mid-operation
4. Cache corruption
5. Concurrent cache access
6. Network interruption
7. Rate limiting (429)
8. Partial batch success

### Test Data Requirements

- Mock JWT tokens (don't use real tokens in tests)
- Sample ETA history responses
- Sample user info responses
- Invalid JSON samples for error testing

### Questions Resolved

Q: What constitutes successful API discovery?
A: Discovery should return at least the 2 known endpoints. Additional endpoints are bonus.

Q: Cache corruption handling?
A: Delete corrupted file and fetch fresh. Log warning but don't raise exception.

### Handoff Notes for Architect

1. Consider implementing R1 (custom exceptions) early - affects all modules
2. Cache module should be designed for testability (injectable path)
3. Discovery module can be simpler initially - expand based on findings
