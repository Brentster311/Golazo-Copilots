# SFI-023 — QA Decision Notes

## Review Summary
- Design is clear and implementable. No blocking issues found.
- 5 edge cases identified and added to test cases (empty items, zero invalid, None SlaType, string SlaType, None EtaStatus).
- Recommended display-time SLA normalization over mutating source data.

## Test Coverage Decisions
- 18 test cases total: 8 for Story A, 5 for Story B, 10 for Story C
- Story C has the most test cases because SLA Status mapping has multiple data type variants
- Bulk regression test (TC-A08) explicitly included to verify no behavior change

## Deferred Items
- Concurrent modal editing not tested (not applicable in single-threaded tkinter)
- Performance testing with large datasets (100+ items) deferred — existing scroll behavior is sufficient
