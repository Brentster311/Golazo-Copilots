# GCP-0058 Test Cases

## Scope
Validate auto-creation of root `capabilities.yaml` in `golazo_create_workitem` while preserving existing-file immutability and create-workitem success semantics.

## Assumptions
- Workspace root is the `workspace_path` provided to the MCP tool.
- Template content source for newly created `capabilities.yaml` is deterministic for a given version.
- “First call” means first successful call in a workspace where root `capabilities.yaml` is absent.

## Acceptance Criteria Mapping
- **AC1**: Missing root `capabilities.yaml` is created during `golazo_create_workitem`.
  - Covered by: TC-01, TC-02
- **AC2**: Existing root `capabilities.yaml` is not overwritten or mutated.
  - Covered by: TC-03
- **AC3**: Work item creation succeeds with normal output in both branches.
  - Covered by: TC-02, TC-04
- **AC4**: Automated tests verify absent/present branches and idempotent existing-file behavior.
  - Covered by: TC-01, TC-03, TC-05

## Functional Tests

### TC-01 Create root capabilities file when absent (branch coverage)
- Precondition: Workspace root has no `capabilities.yaml`; valid `workspace_path`.
- Action: Call `golazo_create_workitem(work_item_id="TQ-1001", profile="complete", workspace_path=<root>)`.
- Expected outcome:
  - Root `capabilities.yaml` is created.
  - New work item folder and baseline files are created successfully.
- Failure message: "Expected root capabilities.yaml to be created when absent during golazo_create_workitem."

### TC-02 Success contract preserved when file is auto-created
- Precondition: Same setup as TC-01.
- Action: Capture tool response from the call.
- Expected outcome:
  - Response indicates successful work item creation.
  - Response structure/fields remain consistent with existing create-workitem contract.
- Failure message: "Expected normal create-workitem success response when capabilities.yaml is auto-created."

### TC-03 Existing root capabilities file remains unchanged (idempotent no-overwrite)
- Precondition:
  - Root `capabilities.yaml` exists with sentinel content.
  - Record original full file content and checksum/hash.
- Action: Call `golazo_create_workitem(work_item_id="TQ-1002", profile="complete", workspace_path=<root>)`.
- Expected outcome:
  - Work item creation succeeds.
  - `capabilities.yaml` content and checksum/hash are unchanged.
- Failure message: "Expected existing root capabilities.yaml to remain unchanged after golazo_create_workitem."

### TC-04 Success contract preserved when file already exists
- Precondition: Same as TC-03.
- Action: Capture tool response from the call.
- Expected outcome:
  - Response indicates successful work item creation.
  - No error/warning indicates mutation or regeneration of `capabilities.yaml`.
- Failure message: "Expected normal create-workitem success response when capabilities.yaml already exists."

### TC-05 Repeated calls remain idempotent for existing file
- Precondition: Root `capabilities.yaml` exists; baseline hash recorded.
- Action: Execute two or more sequential `golazo_create_workitem` calls with distinct IDs.
- Expected outcome:
  - All calls succeed.
  - Root `capabilities.yaml` hash remains constant across calls.
- Failure message: "Expected repeated create-workitem calls to preserve existing capabilities.yaml content."

## Negative / Reliability Tests

### TC-06 Initialization write failure is explicit and non-destructive
- Precondition: Root `capabilities.yaml` absent; simulate write failure (permission denied / mocked I/O failure).
- Action: Call `golazo_create_workitem`.
- Expected outcome:
  - Failure is surfaced with clear initialization context.
  - No partial/corrupt `capabilities.yaml` is left behind.
  - Existing unrelated files are not modified.
- Failure message: "Expected explicit initialization failure and no partial capabilities registry artifacts."

### TC-07 Workspace-root path correctness
- Precondition: Work item path and workspace root both writable; no root `capabilities.yaml`.
- Action: Call `golazo_create_workitem`.
- Expected outcome:
  - `capabilities.yaml` is created only at workspace root.
  - No duplicate file created under `WorkItems/<id>/`.
- Failure message: "Expected capabilities.yaml creation at workspace root only."

## Non-Functional Validation

### TC-08 Negligible overhead check
- Precondition: Representative local test environment.
- Action: Compare elapsed time for create-workitem path with and without file-creation branch over multiple runs.
- Expected outcome:
  - Additional overhead remains negligible and does not regress user-visible behavior.
- Failure message: "Expected capabilities initialization check to add negligible create-workitem overhead."

## Suggested Test File Targets
- `golazo-copilot/tests/test_gcp_create_workitem.py`
- `golazo-copilot/tests/test_gcp_capabilities.py`
- Optional integration coverage in `golazo-copilot/tests/test_output_integration.py` if response-contract assertions are centralized.
