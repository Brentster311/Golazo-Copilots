# GCP-0054 Test Cases — Rename MCP Tools from `gcp_` to `golazo_`

## Test Cases

### TC-01: All existing tests pass (zero regressions)
- **Type**: Regression
- **Method**: `pytest` full suite
- **Expected**: 409 tests pass, 0 failures
- **Failure message**: "Test regression detected after rename — {N} test(s) failed"

### TC-02: No remaining `gcp_` references in operational Python files
- **Type**: Grep verification
- **Method**: `grep -r "gcp_status\|gcp_transition\|gcp_create_workitem\|gcp_bootstrap\|gcp_consent\|gcp_capabilities\|gcp_role_context" --include="*.py" src/`
- **Expected**: Zero matches
- **Failure message**: "Stale gcp_ reference found in Python source: {file}:{line}"

### TC-03: No remaining `gcp_` references in role markdown files
- **Type**: Grep verification
- **Method**: `grep -r "gcp_status\|gcp_transition\|gcp_create_workitem\|gcp_bootstrap\|gcp_consent\|gcp_capabilities\|gcp_role_context" --include="*.md" src/golazo_copilot/roles/`
- **Expected**: Zero matches
- **Failure message**: "Stale gcp_ reference found in role markdown: {file}:{line}"

### TC-04: No remaining `gcp_` references in capabilities.yaml files
- **Type**: Grep verification
- **Method**: `grep -r "gcp_status\|gcp_transition\|gcp_create_workitem\|gcp_bootstrap\|gcp_consent\|gcp_capabilities\|gcp_role_context" --include="*.yaml" .`
- **Expected**: Zero matches
- **Failure message**: "Stale gcp_ reference found in capabilities.yaml: {file}:{line}"

### TC-05: No remaining `gcp_` references in .github/ files
- **Type**: Grep verification
- **Method**: `grep -r "gcp_status\|gcp_transition\|gcp_create_workitem\|gcp_bootstrap\|gcp_consent\|gcp_capabilities\|gcp_role_context" .github/`
- **Expected**: Zero matches
- **Failure message**: "Stale gcp_ reference found in .github/: {file}:{line}"

### TC-06: Tool files renamed correctly
- **Type**: File existence check
- **Method**: Verify old `gcp_*.py` files do NOT exist in `src/golazo_copilot/tools/` and new `golazo_*.py` files DO exist
- **Expected**: 7 old files absent, 7 new files present
- **Failure message**: "Tool file rename incomplete — old file still exists: {file}" or "New tool file missing: {file}"

### TC-07: Server registers all 7 tools with `golazo_` prefix
- **Type**: Registration verification
- **Method**: Inspect server tool registration (existing tests cover this) — confirm tool names are `golazo_status`, `golazo_transition`, `golazo_create_workitem`, `golazo_bootstrap`, `golazo_consent`, `golazo_capabilities`, `golazo_role_context`
- **Expected**: All 7 tools registered with `golazo_` prefix
- **Failure message**: "Server tool registration mismatch — expected golazo_ prefix, found: {name}"

## AC Coverage Matrix

| AC | Test Cases |
|----|------------|
| AC1 | TC-07 |
| AC2 | TC-06, TC-02 |
| AC3 | TC-03, TC-05 |
| AC4 | TC-01 |
| AC5 | TC-02, TC-03, TC-04, TC-05 |
