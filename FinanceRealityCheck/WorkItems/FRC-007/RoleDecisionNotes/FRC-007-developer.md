# FRC-007 Developer Notes

## TDD execution
### Red phase
- Added direct-connector tests for:
  - non-test authentication for First Tech and Fidelity
  - run_sync 90-day ingestion through direct connector path
  - direct connector error-category/actionable-guidance mapping
  - duplicate-safe retry behavior after transient failure
- Verified failure before implementation:
  - pytest tests/test_finance_planner_service.py -k direct_connector -q
  - Result: import error for missing direct connector symbols (expected red phase)

### Green phase
- Implemented connector abstractions and direct connector classes:
  - DirectInstitutionConnector
  - FirstTechDirectConnector
  - FidelityDirectConnector
- Added provider-level error typing and mapping to stable categories:
  - connectivity_error, auth_error, provider_error
- Preserved fixture connector behavior and existing planner sync contract.
- Generalized planner connector typing to support fixture and direct connectors.

## Verification
- pytest tests/test_finance_planner_service.py -k direct_connector -q -> 6 passed
- pytest tests/test_finance_planner_service.py tests/test_finance_planner_api.py -q -> 24 passed

## AC traceability
- AC1: direct non-test auth validated by direct connector tests.
- AC2: run_sync 90-day direct path validated by direct ingestion test.
- AC3: categorized actionable error mapping validated by parametrized tests.
- AC4: duplicate-safe retry validated by transient failure/retry test.
- AC5: existing fixture suite remains green in full service test run.
