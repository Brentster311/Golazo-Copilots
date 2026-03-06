# GCP-0066 Test Cases

## Acceptance Criteria Mapping
- AC1: Documenter role requires changelog maintenance at end of `README.md`.
- AC2: Version update requirement precedes changelog update requirement.
- AC3: Tests enforce policy semantics and sequencing.
- AC4: Existing workflows remain compatible except new policy expectations.

## Test Matrix

### TC1 Documenter Role Includes Changelog Requirement
- Type: Unit
- Setup: Load default documenter role instructions.
- Steps: Assert role content requires changelog maintenance and specifies end-of-README placement.
- Expected: Requirement text/semantic markers present.
- Failure message: "Expected Documenter role to require changelog maintenance at end of README."

### TC2 Builder/Documenter Sequence Requires Version First
- Type: Unit
- Setup: Load default builder and documenter role instructions.
- Steps: Assert version bump/update requirement exists and changelog update language depends on version being defined.
- Expected: Version-first policy semantics present.
- Failure message: "Expected version update requirement before changelog maintenance."

### TC3 Regression: Existing Role Transition Behavior Intact
- Type: Integration
- Setup: Execute representative role transitions unaffected by new policy.
- Steps: Run existing transition tests suite focused on role progression.
- Expected: No new failures unrelated to changelog/version policy.
- Failure message: "Unexpected transition regression after changelog/version policy update."

### TC4 README Changelog Section Placement Preserved
- Type: Unit/Doc consistency
- Setup: Read `golazo-copilot/README.md`.
- Steps: Assert changelog header remains in trailing section and new entries append in expected region.
- Expected: Changelog remains at end-area of README without structural drift.
- Failure message: "Expected changelog section to remain at end of README."

## Non-Functional Checks
- Ensure tests use resilient matching for semantics (not exact full-line string equality where unnecessary).
- Keep runtime overhead minimal by focusing on role-text and targeted regression tests.
