# GCP-0068 Developer Decision Notes

## Scope Implemented
- Implemented a Windows Azure CLI preflight fix in `golazo_update` so install preflight resolves Azure CLI as `az` with `az.cmd` fallback on Windows.
- Preserved existing non-Windows behavior by continuing to resolve `az` on other platforms.
- Kept install flow and target semantics unchanged (`active`/`global` behavior is untouched).

## TDD Evidence
- Red phase (tests added before production code):
  - `pytest tests/test_golazo_update.py -k "gcp0068 or windows_uses_az_cmd_fallback_when_az_missing or windows_missing_cli_fails_before_subprocess_execution"`
  - Result: `2 failed` (expected red) due missing Windows resolver implementation.
- Green phase (after implementation):
  - `pytest tests/test_golazo_update.py -k "gcp0068 or tc15_az_login_active or tc16_az_login_not_active or tc17_az_cli_not_on_path or tc18_pip_command_correct"`
  - Result: `6 passed`.

## Implementation Decisions
- Added `_resolve_az_executable()` in `golazo-copilot/src/golazo_copilot/tools/golazo_update.py`:
  - Windows: `shutil.which("az")` then `shutil.which("az.cmd")` fallback.
  - Non-Windows: `shutil.which("az")`.
- Updated `_check_auth_prerequisites()` to:
  - Fail with a clear missing-CLI error when no executable resolves.
  - Execute `az account show` using the resolved executable path.
  - Keep distinct and actionable errors for:
    - CLI missing
    - CLI found but not logged in (`az login` required)
    - timeout
    - execution failure (`OSError` details)
- Added tests in `golazo-copilot/tests/test_golazo_update.py`:
  - `TestGcp0068WindowsAzPreflight::test_windows_uses_az_cmd_fallback_when_az_missing`
  - `TestGcp0068WindowsAzPreflight::test_windows_missing_cli_fails_before_subprocess_execution`
- Added an autouse resolver fixture in tests to avoid host PATH variability for legacy install tests.

## Documentation Updates
- Updated `golazo-copilot/README.md` update section with explicit Windows preflight behavior (`az` + `az.cmd` fallback).
- Added changelog bullet under `v4.3.4` for GCP-0068.

## Validation
- Regression run:
  - `pytest tests/test_golazo_update.py tests/test_server_formatters.py`
  - Result: `76 passed`.
- Additional transitive-capability regression run:
  - `pytest tests/test_server_dispatch.py`
  - Result: `4 passed`.
- Coverage note:
  - `pytest-cov` emitted `module-not-measured/no-data-collected` warning for `golazo_update` due the test module importing the tool via `importlib.spec_from_file_location`; pass/fail regression evidence is valid.

## Capability Impact
- Ran `golazo_capabilities(action="impact")` for changed code/test files.
- Directly affected capability: `tool-update`.
- Transitively affected capability: `mcp-server`.

## Assumptions
- Existing install command execution and package feed/auth model remain intentionally unchanged.
- No new dependencies were introduced.
