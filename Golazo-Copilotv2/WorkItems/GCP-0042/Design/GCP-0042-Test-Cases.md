# Test Cases — GCP-0042

## TC1: No capabilities.yaml → returns None
- **Setup**: Workspace with no `capabilities.yaml`
- **Action**: `_get_registry_hint(workspace_root)`
- **Assert**: Returns `None`

## TC2: Valid capabilities.yaml → returns count hint
- **Setup**: Workspace with valid `capabilities.yaml` containing 2 capabilities
- **Action**: `_get_registry_hint(workspace_root)`
- **Assert**: Returns string containing "2" and "gcp_capabilities"

## TC3: Malformed YAML → returns warning (no crash)
- **Setup**: Workspace with `capabilities.yaml` containing invalid YAML
- **Action**: `_get_registry_hint(workspace_root)`
- **Assert**: Returns string containing "failed to parse" (not None, not exception)

## TC4: Valid YAML but no capabilities key → returns warning
- **Setup**: Workspace with `capabilities.yaml` containing `{other: stuff}`
- **Action**: `_get_registry_hint(workspace_root)`
- **Assert**: Returns string containing warning about missing key

## TC5: Empty capabilities list → returns "0"
- **Setup**: Workspace with `capabilities.yaml` containing `capabilities: []`
- **Action**: `_get_registry_hint(workspace_root)`
- **Assert**: Returns string containing "0"

## TC6: gcp_status includes registry_hint key
- **Setup**: Active work item + valid `capabilities.yaml`
- **Action**: `await gcp_status(...)`
- **Assert**: Result dict has `registry_hint` key

## TC7: gcp_status registry_hint is None when no capabilities.yaml
- **Setup**: Active work item, no `capabilities.yaml`
- **Action**: `await gcp_status(...)`
- **Assert**: `result["registry_hint"] is None`
