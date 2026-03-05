# Design Doc — GCP-0042: gcp_status — Surface Capability Registry Hints

## Summary
Add a `_get_registry_hint()` function to `gcp_status.py` that checks for `capabilities.yaml` in the workspace root. If found, parse it and return a hint with the capability count. If malformed, return a warning. If absent, return `None` (silent).

## Proposed Approach

### 1. New function in `gcp_status.py`
```python
def _get_registry_hint(workspace_root: Path) -> str | None:
    """Return a registry hint string, or None if no capabilities.yaml."""
```

Logic:
- If `capabilities.yaml` doesn't exist → return `None`
- If it exists but is malformed YAML → return `"Capability Registry: capabilities.yaml exists but failed to parse: <error>"`
- If it exists and is valid → count capabilities list length → return `"Capability Registry: N capability(ies) found. Use gcp_capabilities(action='impact', files=[...]) to check affected features."`

### 2. Add to `gcp_status()` return dict
Add `"registry_hint": _get_registry_hint(workspace_root)` to the return dict, after `version_warning`.

### 3. Format in `server.py`
After the role progress section and before the outputs section, add:
```python
registry_hint = ""
if result.get("registry_hint"):
    registry_hint = f"\n- {result['registry_hint']}"
```
Include `{registry_hint}` in the content template.

## Test Strategy
1. `_get_registry_hint` returns `None` when no `capabilities.yaml`
2. Returns count hint when valid YAML with capabilities list
3. Returns warning when malformed YAML
4. Returns correct count for different list lengths
5. Status dict includes `registry_hint` key
6. Server formatter includes hint in output when present
7. Server formatter omits hint when absent
