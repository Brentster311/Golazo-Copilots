# GCP-008 - Tester Decision Notes

## Work Item
GCP-008: Extract Technical Guides from Spine for Improved Copilot Interop

## Decisions Made

1. **Manual verification tests**: This is documentation refactoring, not code; automated tests not applicable
2. **8 test cases defined**: 7 positive, 1 negative
3. **Focus on structure and content**: Tests verify file existence, version headers, content migration, and references

## Alternatives Considered

| Alternative | Decision | Rationale |
|-------------|----------|-----------|
| Automated file content tests | Rejected | Overkill for markdown refactor; manual verification sufficient |
| Skip testing (docs only) | Rejected | Upgrade process changes could break users |

## Tradeoffs Accepted

- Manual tests require human execution
- No CI/CD integration for these tests

## Known Limitations

- Cannot automatically verify "Copilot loads guides when relevant" - requires human observation
- Workflow behavior test (TC-006) is subjective

## Test Coverage Mapping

| Acceptance Criteria | Test Case(s) |
|---------------------|--------------|
| PowerShell guide exists | TC-001 |
| Update guide exists | TC-002 |
| Guides have version headers | TC-001, TC-002 |
| Spine reduced with references | TC-003 |
| Workflow unchanged | TC-006 |
| VERSION updated | TC-004 |
| CHANGELOG updated | TC-004 |

## Risks

| Risk | Mitigation |
|------|------------|
| Tests missed edge case | Negative test TC-N01 covers missing guide scenario |
| Version drift between files | TC-001, TC-002, TC-003 all check 1.1.0 |
