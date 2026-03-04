# GCP-0060 Developer Decision Notes

## Role Execution Summary
- Implemented `golazo_git_propose` as a proposal-only MCP tool for git intent capture (`add`, `commit`, `push`, `branch`).
- Executed TDD-first workflow: added GCP-0060 tests before production code, confirmed red failure, then implemented and validated green.
- Preserved scope boundaries: no git execution behavior, no external approval workflows, no new dependencies.

## Assumptions Made (No Questions Asked)
1. Deterministic validation should be machine-assertable using stable semantic fields (`error_code`, `parameter`, `action`) in addition to human-readable `error` text.
2. Proposal `status` should use a single creation value (`proposed`) in this work item.
3. Optional action payload fields should be omitted when not applicable (no `null` serialization) for cleaner audit records.
4. `golazo_git_propose` should be treated as a workflow operation and require orchestrator instructions preflight.

## TDD Evidence (Red -> Green)
1. Added tests first:
   - `golazo-copilot/tests/test_gcp_git_propose.py` (TC-001 .. TC-010 coverage)
   - `golazo-copilot/tests/test_server_dispatch.py` preflight coverage for `golazo_git_propose`
2. Red-phase verification command:
   - `Q:/src/Golazo-Copilots/Golazo-Copilotv2/.venv/Scripts/python.exe -m pytest tests/test_gcp_git_propose.py tests/test_server_dispatch.py -q`
   - Result: collection failed with `ModuleNotFoundError: golazo_copilot.tools.golazo_git_propose` (expected pre-implementation failure)
3. Green-phase verification command:
   - `Q:/src/Golazo-Copilots/Golazo-Copilotv2/.venv/Scripts/python.exe -m pytest tests/test_gcp_git_propose.py tests/test_server_dispatch.py -q`
   - Result: **14 passed in 1.12s**

## Implementation Decisions
### 1) State model compatibility and persistence
- Added `git_actions` to `WorkItemState` with `default_factory=list` to preserve backward compatibility and prevent field loss during load/save round-trips.
- Legacy states missing `git_actions` are safely initialized on first proposal write.

### 2) Deterministic validation contract
- Missing required parameters return stable payloads:
  - `error_code="parameter_required"`
  - `parameter="message"` for `commit`
  - `parameter="branch"` for `push|branch`
  - `parameter="files"` for `add`
- Missing work item returns:
  - `error_code="workitem_not_found"`
  - explicit guidance to run `golazo_create_workitem`.

### 3) Proposal record normalization
- Each appended entry includes:
  - `action`
  - `status` (`proposed`)
  - `timestamp` (UTC ISO-8601 with trailing `Z`)
  - action payload (`files` | `message` | `branch`)
- Append-only behavior is enforced by always appending to list tail; no in-place edit/remove logic exists in this scope.

### 4) Failure handling
- Persistence errors are hard-fail and return `error_code="persistence_failure"`; no success response is returned when save fails.

## Files Changed
### Source
- `golazo-copilot/src/golazo_copilot/core/types.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_git_propose.py`
- `golazo-copilot/src/golazo_copilot/tools/__init__.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/README.md`

### Tests
- `golazo-copilot/tests/test_gcp_git_propose.py`
- `golazo-copilot/tests/test_server_dispatch.py`

## Additional Regression Validation
- Command:
  - `Q:/src/Golazo-Copilots/Golazo-Copilotv2/.venv/Scripts/python.exe -m pytest tests/test_gcp_create_workitem.py tests/test_gcp_transition.py tests/test_gcp_status.py -q`
- Result: **97 passed in 2.13s**

## Capability Impact Analysis (Required)
Executed `golazo_capabilities(action="impact")` for changed source files:
- Directly affected: `state-model`, `mcp-server`
- Transitively affected: `tool-golazo-update`, `persistence`, `tool-create-workitem`, `tool-consent`, `tool-transition`, `tool-status`, `tool-role-context`
- Assessment: changes are additive, scoped, and compatible with existing workflows.

## First-Action Compliance
- Created feature branch: `GCP-0060`.

## Scope/Escalation Check
- No scope/design redefinition introduced.
- No architectural escalation triggered during implementation.
- No new user story created in this role pass.
