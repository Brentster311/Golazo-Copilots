# GCP-0068 Test Cases

## Acceptance Criteria Mapping
- AC1: Windows preflight resolves Azure CLI reliably.
- AC2: Error messages differentiate missing CLI, not logged in, and execution timeout/failure.
- AC3: Non-Windows behavior remains compatible.
- AC4: Automated tests cover resolution and messaging branches.
- AC5: Docs updated where needed.

## Test Matrix

### TC1 Windows Resolver Finds `az.cmd`
- Type: Unit
- Setup: Patch platform to Windows and mock `shutil.which` results.
- Steps: Ensure resolver returns an executable path when only `az.cmd` is present.
- Expected: resolver returns non-empty path; preflight does not emit missing-CLI error.
- Failure message: "Expected Windows resolver to detect Azure CLI via az.cmd."

### TC2 Missing CLI Returns Missing-Tool Error
- Type: Unit
- Setup: Mock resolver to return no executable.
- Steps: Call preflight/install path.
- Expected: error indicates CLI missing/not on PATH.
- Failure message: "Expected missing Azure CLI error when resolver finds no executable."

### TC3 Logged-Out CLI Returns Auth Error
- Type: Unit
- Setup: Resolver returns executable; subprocess returns non-zero.
- Steps: Call preflight/install path.
- Expected: error indicates `az login` required.
- Failure message: "Expected not-logged-in message when az account show fails."

### TC4 CLI Timeout Returns Timeout Error
- Type: Unit
- Setup: Resolver returns executable; subprocess raises timeout.
- Steps: Call preflight/install path.
- Expected: timeout-specific error.
- Failure message: "Expected Azure CLI timeout message when account check times out."

### TC5 Regression Install Path Still Works
- Type: Regression
- Setup: Existing successful install mocks.
- Steps: Run existing install success tests.
- Expected: unchanged success behavior.
- Failure message: "Unexpected regression in golazo_update install success path."
