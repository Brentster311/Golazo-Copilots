# GCP-0069 QA Test Cases

## Test Strategy
- Write tests before production changes where practical.
- Cover bootstrap behavior and workflow preflight behavior together.
- Validate both modular dispatch helpers and the legacy server dispatch path.

## Traceability Matrix
| Acceptance Criterion | Covered Test IDs |
|---|---|
| AC1: default/empty/workspace scope preserves workspace behavior | TC-AC1-001, TC-AC1-002 |
| AC2: user scope writes to active user Copilot directory | TC-AC2-001, TC-AC2-002 |
| AC3: workflow preflight succeeds with user-scope instructions | TC-AC3-001, TC-AC3-002 |
| AC4: invalid scope rejected clearly | TC-AC4-001 |
| AC5: automated coverage spans bootstrap and instruction resolution paths | TC-AC5-001, TC-AC5-002, TC-REL-001 |

## Functional Acceptance Tests

### TC-AC1-001 — Omitted scope preserves current workspace bootstrap behavior
- **Type**: Automated async unit/integration
- **Priority**: P0
- **Steps**:
  1. Call `golazo_bootstrap(workspace_path=<workspace>)` with no `scope` argument.
  2. Inspect created files and result payload.
- **Expected Outcome**:
  - `.github/agents/Golazo-Copilot.md` is created under the workspace.
  - No user-scope instructions file is created.
  - Result indicates workspace scope/effective target.
- **Failure Message**:
  - `AC1_FAIL_DEFAULT_SCOPE: Omitted scope did not preserve workspace bootstrap behavior.`

### TC-AC1-002 — Empty scope and explicit Workspace behave identically
- **Type**: Automated async unit/integration
- **Priority**: P0
- **Steps**:
  1. Call bootstrap once with `scope=""`.
  2. Call bootstrap once with `scope="Workspace"` in a clean workspace.
  3. Compare destination behavior and result metadata.
- **Expected Outcome**:
  - Both calls create the same workspace-scoped instructions path.
  - Both calls produce equivalent success semantics.
- **Failure Message**:
  - `AC1_FAIL_SCOPE_NORMALIZATION: Empty scope and explicit Workspace produced different bootstrap behavior.`

### TC-AC2-001 — User scope writes orchestrator instructions outside the workspace
- **Type**: Automated async unit/integration
- **Priority**: P0
- **Steps**:
  1. Override the effective home/user Copilot root for test isolation.
  2. Call `golazo_bootstrap(workspace_path=<workspace>, scope="User")`.
  3. Inspect workspace and user target directories.
- **Expected Outcome**:
  - Orchestrator instructions are created under the effective user Copilot directory.
  - Workspace `.github/agents/Golazo-Copilot.md` is not created by this call.
  - Result payload includes the resolved user target path.
- **Failure Message**:
  - `AC2_FAIL_USER_SCOPE_DESTINATION: User scope did not write instructions to the effective user Copilot directory.`

### TC-AC2-002 — Formatted bootstrap output reports effective target
- **Type**: Automated unit
- **Priority**: P1
- **Steps**:
  1. Format a successful bootstrap result for user scope.
  2. Inspect returned text.
- **Expected Outcome**:
  - Output names the effective scope or install target path clearly enough for troubleshooting.
- **Failure Message**:
  - `AC2_FAIL_BOOTSTRAP_OUTPUT_VISIBILITY: Formatted bootstrap output did not expose the effective install target.`

### TC-AC3-001 — Shared instruction lookup recognizes workspace scope
- **Type**: Automated unit
- **Priority**: P0
- **Steps**:
  1. Create only workspace-scoped instructions.
  2. Call the shared instruction existence helper.
- **Expected Outcome**:
  - Helper returns `True`.
- **Failure Message**:
  - `AC3_FAIL_WORKSPACE_LOOKUP: Shared instruction lookup did not recognize workspace-scoped instructions.`

### TC-AC3-002 — Workflow preflight succeeds with only user-scope instructions present
- **Type**: Automated async integration
- **Priority**: P0
- **Steps**:
  1. Create a valid workspace with no workspace-scoped instructions.
  2. Create only user-scoped instructions in the effective user Copilot directory.
  3. Call workflow preflight through `server._dispatch_tool` for `golazo_create_workitem`.
- **Expected Outcome**:
  - Preflight does not return the missing-instructions failure.
  - Work item creation proceeds successfully.
- **Failure Message**:
  - `AC3_FAIL_USER_SCOPE_PREFLIGHT: Workflow preflight did not accept valid user-scope orchestrator instructions.`

### TC-AC4-001 — Invalid scope is rejected with clear validation error
- **Type**: Automated async unit
- **Priority**: P0
- **Steps**:
  1. Call `golazo_bootstrap(..., scope="Team")`.
- **Expected Outcome**:
  - Result is unsuccessful.
  - Error text identifies the invalid value and supported values.
- **Failure Message**:
  - `AC4_FAIL_INVALID_SCOPE_VALIDATION: Invalid scope was accepted or returned an unclear validation error.`

### TC-AC5-001 — Tool schema advertises new scope parameter
- **Type**: Automated contract test
- **Priority**: P1
- **Steps**:
  1. Inspect the advertised bootstrap tool schema.
- **Expected Outcome**:
  - `scope` appears in the input schema with supported values documented.
- **Failure Message**:
  - `AC5_FAIL_TOOL_SCHEMA_SCOPE: Bootstrap tool schema did not expose the new scope parameter.`

### TC-AC5-002 — Legacy coverage remains consistent
- **Type**: Automated regression
- **Priority**: P1
- **Steps**:
  1. Run legacy server coverage tests that exercise helper and formatter branches.
  2. Add or update assertions where scope-aware behavior changes expected output.
- **Expected Outcome**:
  - Legacy coverage remains green and matches new behavior.
- **Failure Message**:
  - `AC5_FAIL_LEGACY_PARITY: Legacy server coverage diverged from modular scope-aware behavior.`

## Reliability / Regression Test

### TC-REL-001 — No regression for existing workspace-only callers
- **Type**: Automated regression
- **Priority**: P0
- **Steps**:
  1. Run existing bootstrap tests that cover standard workspace behavior.
  2. Run existing server dispatch tests that expect workspace-scoped preflight behavior.
- **Expected Outcome**:
  - Existing workspace-scope behavior remains unchanged unless explicitly updated for richer output text.
- **Failure Message**:
  - `REL_FAIL_WORKSPACE_REGRESSION: User-scope support regressed existing workspace-only bootstrap or preflight behavior.`
