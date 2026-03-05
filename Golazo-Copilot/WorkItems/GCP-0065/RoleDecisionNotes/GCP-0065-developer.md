# GCP-0065 Developer Notes

## Scope Implemented
- Implemented canonical capability registry path handling in `golazo-copilot/src/golazo_copilot/tools/golazo_capabilities.py`.
- Updated tests in `golazo-copilot/tests/test_gcp_capabilities.py` to enforce canonical-path behavior and migration logic.

## Key Decisions
- Canonical registry path is `WorkItems/capabilities.yaml`.
- Resolver checks canonical path first; if present, it is always used.
- If canonical is missing and legacy root `capabilities.yaml` exists, the legacy file is moved to canonical path.
- If both canonical and legacy files exist, canonical wins and legacy remains untouched.
- Missing-registry errors now return `success: false` and include canonical path guidance.
- Parse/schema errors reference canonical path (`WorkItems/capabilities.yaml`) for consistent diagnostics.

## TDD Evidence
- Red phase: added canonical/migration/conflict/missing-file tests first in `test_gcp_capabilities.py`, then ran the file and observed failures against existing root-only behavior.
- Green phase: implemented resolver + migration code and re-ran the same suite.

## Test Execution
- Command:
  - `C:/Users/Brent/source/repos/Brentster311/Golazo-Copilots/Golazo-Copilot/.venv/Scripts/python.exe -m pytest C:/Users/Brent/source/repos/Brentster311/Golazo-Copilots/Golazo-Copilot/golazo-copilot/tests/test_gcp_capabilities.py -q`
- Result:
  - `21 passed in 0.28s`

## Capability Impact Check
- Ran `golazo_capabilities(action="impact")` for changed files.
- Directly affected capability: `tool-capabilities`.
- Transitively affected capability: `mcp-server`.

## Assumptions
- Returning `success: false` for missing registry is acceptable for the new canonical-path error contract.
- Migration uses filesystem move semantics and should remain deterministic across supported OSes.
