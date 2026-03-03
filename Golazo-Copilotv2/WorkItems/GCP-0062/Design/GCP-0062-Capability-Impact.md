# GCP-0062 Capability Impact Analysis

## Analysis Context
- Work item: `GCP-0062`
- Story intent: enforce branch naming format `<useralias>/<workitemid>` in Golazo workflow branch-creation path.
- Capability registry source: `capabilities.yaml` found at project root.
- Impact tool execution: `golazo_capabilities(action="impact", files=[...])`.

## Assumptions Used for Impact Mapping
1. Design doc describes workflow-tooling branch-creation enforcement but does not pin final implementation file paths.
2. Current repository surfaces branch-related validation via output validation and transition gate wiring.
3. Impact input files selected as nearest implementation surfaces for this story:
   - `golazo-copilot/src/golazo_copilot/core/output_validator.py`
   - `golazo-copilot/src/golazo_copilot/core/state.py`
   - `golazo-copilot/src/golazo_copilot/tools/golazo_transition.py`

## Directly Affected Capabilities

### 1) `output-validation`
- Description: Parses required outputs and validates file/dir/git outputs.
- Key contract(s):
  - `parse_required_outputs(role_content, work_item_id) -> list[OutputSpec]`
  - `validate_all_outputs(specs, workspace_path) -> ValidationResult`
  - `OutputSpec.type` includes `git-branch`.
- Why direct: this capability currently owns `git-branch` validation semantics and is the closest existing enforcement surface for branch-name policy.

### 2) `tool-transition`
- Description: Enforces role transitions and output gates.
- Key contract(s):
  - `golazo_transition(work_item_id, role, work_items_dir, project_root, force, force_without_notes) -> dict`
- Why direct: transition gate behavior depends on output validation outcomes; stricter branch contract behavior can influence transition readiness and error reporting.

## Transitively Affected Capabilities (Downstream Dependents)

### 1) `tool-status`
- Depends on `output-validation` and `tool-transition`.
- Impact: status reporting and required-output checks may reflect new/stricter branch validation outcomes.

### 2) `mcp-server`
- Depends on `tool-transition` and `tool-status` (among others).
- Impact: end-user MCP responses and surfaced errors may change when branch naming validation contracts tighten.

### 3) `tool-role-context`
- Depends on `tool-transition`.
- Impact: role-context assembly can be indirectly affected if transition gating behavior changes around required outputs.

### 4) `tool-golazo-update`
- Registry indicates dependency relationship through `mcp-server`.
- Impact: no branch-policy logic impact expected, but capability graph marks it as transitive due to server dependency chain.

## Contract Implications

### New or Changed Public Interfaces
- No new MCP tool is required by current design.
- No mandatory signature changes are required for existing public contracts if branch policy is implemented within existing validation paths.

### Behavioral Contract Tightening
- `git-branch` validation semantics should be treated as a stricter behavioral contract where applicable to workflow branch creation:
  - enforce exact `<useralias>/<workitemid>` match,
  - return deterministic categorized failures,
  - include actionable remediation and valid example.

### Compatibility and Risk Notes
- Backward compatibility risk is behavioral (stricter rejection), not API shape.
- To reduce blast radius, enforcement should remain scoped to workflow-managed branch creation and avoid altering unrelated git-branch checks.
- Error taxonomy must remain stable to preserve telemetry and operator runbook expectations.

## Architectural Conclusion
- Capability impact is moderate and centered on validation/gating pathways.
- Primary contract concern is deterministic, centralized branch-validation behavior.
- No capability-registry schema change is required for this work item.