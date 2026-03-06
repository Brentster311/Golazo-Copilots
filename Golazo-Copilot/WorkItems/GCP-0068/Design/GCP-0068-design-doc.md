# GCP-0068 Design Doc

## Summary
Fix Windows-specific Azure CLI preflight detection in `golazo_update` so install actions do not fail falsely when Azure CLI is present and authenticated.

## Problem Statement
`golazo_update(action="install")` currently may return a false "az not installed" error on Windows due to executable resolution differences between shell invocation and Python subprocess lookup.

## Business Case
- Why now: observed real runtime failure despite valid Azure CLI installation/login.
- Impact: restores trust in the update tool and reduces manual workaround steps.
- KPIs:
  - 0 false `az`-missing errors on Windows when CLI exists.
  - Distinct error messaging for missing CLI vs not logged in vs execution failure.

## Stakeholders
- Golazo Copilot users on Windows
- Maintainers of update tooling

## Functional Requirements
- Preflight must resolve Azure CLI robustly on Windows (`az`/`az.cmd` handling).
- Preflight must preserve existing behavior on non-Windows platforms.
- Error output must clearly differentiate missing CLI, login failure, and timeout/execution errors.
- Existing install path behavior (version/target handling) remains unchanged.

## Non-Functional Requirements
- Deterministic error messages.
- No regression to security/auth checks.
- Minimal code-surface change.

## Proposed Approach
- Add CLI resolution helper using `shutil.which` with Windows-aware fallback (`az.cmd`).
- Use resolved executable path in `subprocess.run` for preflight auth check.
- Keep existing timeout and return-code checks.
- Add/update tests for:
  - Windows resolution success path
  - Missing CLI path
  - Logged-out/non-zero return path
  - Timeout path
- Update README/tool docs only if user-facing prerequisite behavior text needs clarification.

## Alternatives Considered
- Remove Azure CLI preflight check: rejected (weakens prerequisite validation).
- Shelling through `cmd /c az`: rejected (adds brittle indirection).

## Risks, Mitigations, Open Questions
- Risk: platform-specific edge cases in executable lookup.
  - Mitigation: unit tests with patched `platform.system` and `shutil.which`.
- Risk: changing error text could break strict tests.
  - Mitigation: use semantic assertions where possible.
- Open question: whether to include `azure-cli` path hint in non-Windows messages.

## Dependencies
- `golazo-copilot/src/golazo_copilot/tools/golazo_update.py`
- `golazo-copilot/tests/test_golazo_update.py`
- Optional docs updates in `golazo-copilot/README.md`

## Migration / Rollout / Rollback Plan
- Rollout: ship code/tests/docs together in patch release.
- Migration: none.
- Rollback: revert helper + tests if cross-platform regressions appear.

## Observability Plan
- Preserve actionable error strings for support diagnostics.
- Validate via automated tests and live command check on Windows environment.

## Test Strategy Summary
- Unit tests for CLI resolution and error branching.
- Regression tests for existing install/check behavior.
