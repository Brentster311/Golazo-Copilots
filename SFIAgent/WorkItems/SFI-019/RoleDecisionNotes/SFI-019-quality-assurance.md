# SFI-019 Quality Assurance Notes

## Review Summary

6 review comments raised:
- 1 Blocker (RC-1: payload format mismatch)
- 5 Recommendations (RC-2 through RC-6)

The blocker is already acknowledged in the design doc and user story assumptions. The architect must bind the payload format decision before development.

## Test Strategy

15 test cases covering all 6 acceptance criteria plus 2 review comments.

Test breakdown:
- 5 unit tests for `eta_logic.py` (TC-01 through TC-05)
- 1 unit test for `EtaUpdate.to_api_payload()` format (TC-06)
- 2 unit tests for `save_etas()` success/failure (TC-07, TC-08)
- 4 integration tests for bulk/manual/single flows (TC-09 through TC-12)
- 3 validation tests for edge cases (TC-13 through TC-15)

All tests can be written with `unittest.mock` — no real API calls needed.

## Risk Items for Architect

1. Payload format (RC-1) — must be resolved before any code
2. AssignedTo source (RC-2) — needs binding decision
3. SLAType mapping (RC-3) — needs confirmation
