# GCP-0044 — Test Cases

## Mapping: Acceptance Criteria → Test Cases

| AC # | Acceptance Criterion | Test Case(s) |
|------|---------------------|--------------|
| AC1 | All 6 schemas include `workspace_path` in `required` | TC1.1 |
| AC2 | Missing `workspace_path` returns clear error | TC2.1–TC2.3 |
| AC3 | `resolve_work_items_dir(None)` raises ValueError | TC3.1 |
| AC4 | Existing tests pass | TC4.1 |

---

## TC1: Schema Validation

### TC1.1: All tool schemas require `workspace_path`
- **Verification**: Call `list_tools()`, iterate all 6 tools, assert `"workspace_path"` is in each tool's `inputSchema["required"]`
- **Failure message**: "Tool '{name}' does not include workspace_path in required params"

## TC2: Runtime Validation — Missing `workspace_path`

### TC2.1: `gcp_create_workitem` without `workspace_path` returns error
- **Input**: `call_tool("gcp_create_workitem", {"work_item_id": "TST-001"})`
- **Expected**: Error response containing "workspace_path is required"
- **Failure message**: "gcp_create_workitem should fail when workspace_path is missing"

### TC2.2: `gcp_transition` without `workspace_path` returns error
- **Input**: `call_tool("gcp_transition", {"work_item_id": "TST-001", "role": "program-manager"})`
- **Expected**: Error response containing "workspace_path is required"
- **Failure message**: "gcp_transition should fail when workspace_path is missing"

### TC2.3: `gcp_bootstrap` without `workspace_path` returns error
- **Input**: `call_tool("gcp_bootstrap", {})`
- **Expected**: Error response containing "workspace_path is required"
- **Failure message**: "gcp_bootstrap should fail when workspace_path is missing"

## TC3: `resolve_work_items_dir` Unit Tests

### TC3.1: `resolve_work_items_dir(None)` raises ValueError
- **Input**: `resolve_work_items_dir(None)`
- **Expected**: Raises `ValueError` with message containing "workspace_path"
- **Failure message**: "resolve_work_items_dir should not fall back to cwd when workspace_path is None"

### TC3.2: `resolve_work_items_dir("")` raises ValueError
- **Input**: `resolve_work_items_dir("")`
- **Expected**: Raises `ValueError`
- **Failure message**: "resolve_work_items_dir should not accept empty string"

### TC3.3: `resolve_work_items_dir` with valid path resolves correctly
- **Input**: `resolve_work_items_dir("C:\\my\\workspace")`
- **Expected**: Returns `Path("C:\\my\\workspace\\WorkItems")`
- **Failure message**: "Valid workspace_path should resolve to WorkItems subdirectory"

## TC4: Regression

### TC4.1: All existing tests pass
- **Verification**: `pytest tests/` — all previously passing tests still pass
- **Failure message**: "Existing tests must not be broken by this change"
