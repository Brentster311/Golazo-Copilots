# SFI-037 — Quality Assurance Decision Notes

## Design Review Summary

Design is clean and well-scoped. Raised 4 minor recommendations (RC-1 through RC-4) documented in Review Comments. No blockers.

## Capability Impact

7 capabilities affected (3 direct, 4 transitive). All directly affected capabilities have corresponding test coverage in the test cases:
- **reporter-data**: TC-037-01 through TC-037-04 (fetch logic)
- **reporter-tk-app**: TC-037-05 through TC-037-13 (row cost computation, display formatting)
- **reporter-cache**: No new tests needed — `kpi_cost_map` is a plain dict, serializes with existing JSON cache infrastructure

Transitive impacts:
- **reporter-eta-logic**: Not affected (cost is independent of ETA logic)
- **reporter-query-builder**: Cost column not added as a filterable field (documented in RC-4)
- **reporter-build**: No new hidden imports needed
- **reporter-tests**: New test file `test_sfi_037.py` covers the feature

## Test Strategy

13 test cases covering all 7 acceptance criteria plus edge cases. Tests follow existing patterns in `test_data.py` (mock S360Client, assert on computed values). All tests can be implemented before production code (TDD).
