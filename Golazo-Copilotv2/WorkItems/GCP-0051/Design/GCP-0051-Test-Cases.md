# GCP-0051 — Test Cases

## Test File: `test_gcp_status_parallel.py`

All tests use `pytest-asyncio` and mock I/O to avoid filesystem dependencies.

---

### TC-1: Response structure unchanged (AC1)

**Category**: Regression  
**Setup**: Create a work item, transition to developer role, create required artifacts  
**Action**: Call `gcp_status`  
**Assert**: Response dict has all expected keys: `active`, `version`, `work_item_id`, `profile`, `current_phase`, `current_role`, `required_outputs`, `role_progress`, `deviations`, `missing_notes`, `version_warning`, `registry_hint`, `role_instructions`, `next_steps`  
**Note**: This is already covered by existing tests. Included here to confirm no regression.

---

### TC-2: Concurrent execution timing (AC2)

**Category**: Performance  
**Setup**: Mock `_get_stale_files`, `_get_registry_hint`, and `_async_check_missing_notes` to each call `asyncio.sleep(0.1)` (100ms). Mock output validation to sleep 100ms.  
**Action**: Measure wall-clock time of `gcp_status` call  
**Assert**: Total time < 250ms (parallel) rather than ≥ 400ms (sequential). Use margin: `assert elapsed < 0.25`  
**Failure message**: `"gcp_status took {elapsed:.2f}s — expected <0.25s if operations ran in parallel"`

---

### TC-3: Error isolation — stale files failure (AC3)

**Category**: Fault tolerance  
**Setup**: Mock `_get_stale_files` to raise `RuntimeError("disk read failed")`  
**Action**: Call `gcp_status`  
**Assert**:
- Response `active` is `True` (call succeeds overall)
- `version_warning` contains an error indicator or is `None` (graceful degradation)
- `required_outputs`, `registry_hint`, `role_progress` are populated normally
**Failure message**: `"gcp_status should not fail entirely when stale-file check fails"`

---

### TC-4: Error isolation — registry hint failure (AC3)

**Category**: Fault tolerance  
**Setup**: Mock `_get_registry_hint` to raise `yaml.YAMLError("parse fail")`  
**Action**: Call `gcp_status`  
**Assert**:
- Response `active` is `True`
- `registry_hint` contains an error string or is `None`
- Other fields populated normally
**Failure message**: `"Registry hint failure should not block other status operations"`

---

### TC-5: Error isolation — output validation failure (AC3)

**Category**: Fault tolerance  
**Setup**: Mock `validate_all_outputs` to raise `Exception("validator crash")`  
**Action**: Call `gcp_status`  
**Assert**:
- Response `active` is `True`
- `required_outputs` has a safe fallback (empty list or error marker)
- `next_steps` still generates (with empty output list)
**Failure message**: `"Output validation failure should not crash gcp_status"`

---

### TC-6: No new dependencies (AC5)

**Category**: Constraint  
**Action**: Parse `pyproject.toml` dependencies list  
**Assert**: No new entries added beyond current `mcp`, `pydantic`, `PyYAML`  
**Note**: This is a static check, not a runtime test. Can be a test or a CI lint step.

---

### TC-7: `_generate_next_steps` handles error in output_result gracefully

**Category**: Edge case (from Review Comments #1)  
**Setup**: Simulate output validation returning an exception (wrapped by `return_exceptions=True`)  
**Action**: Call `_generate_next_steps(state, required_outputs=[])` (empty list fallback)  
**Assert**: Returns a non-empty list of generic next steps, no crash  
**Failure message**: `"_generate_next_steps should handle empty/missing output data without crashing"`

---

### TC-8: Pure computation operations don't block on thread pool

**Category**: Correctness  
**Setup**: Normal work item state  
**Action**: Call `_compute_role_progress(state)` directly  
**Assert**: Returns dict with `roles`, `roles_completed`, `roles_total` keys; completes in < 1ms  
**Note**: Validates that even wrapped in `to_thread`, this function has negligible overhead.

---

## Existing Test Coverage (from `test_gcp_status.py`)

The following existing tests validate AC1 (response structure identity) and must continue to pass:

- `test_status_basic` — basic response structure
- `test_status_with_required_outputs` — output validation in response
- `test_status_stale_files` — stale file detection
- `test_status_registry_hint` — capability registry hint
- `test_status_role_progress` — role progress computation
- `test_status_missing_notes` — missing role notes detection
