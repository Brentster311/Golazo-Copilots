# GCP-0059 Developer Notes

## Scope Implemented
Implemented the approved bootstrap output contract change only:
- Orchestrator/spine output path is now `.github/agents/golazo-copilot/orchestrator.md`.
- Default copied roles output directory is now `.github/agents/golazo-copilot/roles/`.

Additional developer-scope completion for this work item:
- Resolved the remaining failing status test `tests/test_gcp_status.py::TestRegistryHint::test_status_registry_hint_none_when_absent`.
- Applied a minimal, test-only fix to enforce the "capabilities.yaml absent" precondition deterministically.

## TDD Execution
1. Updated path-sensitive tests first (red phase) to assert the new contract paths.
2. Ran targeted tests and confirmed expected failures against pre-change implementation.
3. Updated production code and related source messaging/docs.
4. Re-ran targeted and broader relevant tests to confirm green.

## Files Changed
### Source
- `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_status.py`
- `golazo-copilot/src/golazo_copilot/roles/loader.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_role_context.py`
- `golazo-copilot/src/golazo_copilot/roles/defaults/project-owner-assistant.md`
- `golazo-copilot/src/golazo_copilot/roles/defaults/architect.md`
- `golazo-copilot/src/golazo_copilot/roles/defaults/developer.md`
- `golazo-copilot/src/golazo_copilot/roles/defaults/refactor-expert.md`
- `golazo-copilot/src/golazo_copilot/roles/defaults/documenter.md`
- `golazo-copilot/src/golazo_copilot/roles/defaults/retrospective.md`

### Tests
- `golazo-copilot/tests/test_gcp_bootstrap.py`
- `golazo-copilot/tests/test_server_dispatch.py`
- `golazo-copilot/tests/test_server_formatters.py`
- `golazo-copilot/tests/test_gcp_status.py`
- `golazo-copilot/tests/test_role_self_contained.py`

## Test Runs
- `Q:/src/Golazo-Copilots/Golazo-Copilotv2/.venv/Scripts/python.exe -m pytest tests/test_gcp_status.py::TestRegistryHint::test_status_registry_hint_none_when_absent -q`
  - Result: **1 passed in 0.27s**.
- `Q:/src/Golazo-Copilots/Golazo-Copilotv2/.venv/Scripts/python.exe -m pytest tests/test_gcp_status.py -q`
  - Result: **30 passed in 0.81s**.
- `Q:/src/Golazo-Copilots/Golazo-Copilotv2/.venv/Scripts/python.exe -m pytest tests/test_gcp_bootstrap.py tests/test_server_dispatch.py tests/test_server_formatters.py tests/test_role_self_contained.py -q`
  - Result: **131 passed in 1.66s**.

## Capability Impact Check
Ran `golazo_capabilities(action="impact")` for changed source files.
- Result: **0 capabilities affected**.

## Compatibility Notes
- Role loader now prefers `.github/agents/golazo-copilot/roles/{role}.md`.
- Legacy read fallback for `.github/roles/{role}.md` is retained to avoid breaking existing local overrides.

## Blockers / Follow-up
- No blockers for the approved scope.
- No remaining known failing tests in the validated relevant suite for this work item.
