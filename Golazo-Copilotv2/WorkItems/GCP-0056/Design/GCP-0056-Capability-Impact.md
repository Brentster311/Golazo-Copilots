# GCP-0056 Capability Impact Analysis

## Summary

GCP-0056 introduces a new MCP tool (`golazo_update`) and registers it in the server. This analysis identifies which capabilities in `capabilities.yaml` are affected and what contract changes result.

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `golazo-copilot/src/golazo_copilot/tools/golazo_update.py` | **NEW** | New tool module — check/install update logic |
| `golazo-copilot/src/golazo_copilot/tools/__init__.py` | **MODIFIED** | Add `golazo_update` to imports and `__all__` |
| `golazo-copilot/src/golazo_copilot/server.py` | **MODIFIED** | Import, Tool entry, dispatch case, formatter |
| `golazo-copilot/tests/test_golazo_update.py` | **NEW** | Test suite for the new tool |
| `capabilities.yaml` | **MODIFIED** | Add `tool-update` capability; update `mcp-server` |

## Directly Affected Capabilities

### 1. `mcp-server`

**Key files touched:** `server.py`

**Contract change:**
- `list_tools()` returns **8 tools** (was 7) — adds `golazo_update`
- `call_tool(name, arguments)` gains a new dispatch branch for `"golazo_update"`
- New formatter function: `format_update_result(result: dict) -> str`

**Risk:** Low. The change is purely additive — a new `elif` branch in `_dispatch_tool`, a new `Tool` in `list_tools`, and a new formatter function. No existing dispatch paths or formatters are modified.

**`depends_on` change:** Add `tool-update` to the `mcp-server` capability's `depends_on` list.

### 2. NEW: `tool-update` (to be added to registry)

**Description:** Check for and install updates to golazo-copilot from Azure Artifacts

**Key files:**
- `golazo-copilot/src/golazo_copilot/tools/golazo_update.py`

**Contracts:**
- `golazo_update(action, version?, workspace_path) -> dict`
- `action="check"` → `{action, current_version, latest_stable, latest_prerelease, update_available, message}`
- `action="install"` → `{action, version, previous_version, success, restart_required, message}` (success) or `{action, version, success, error}` (failure)
- Error → `{error, error_type}` where `error_type` ∈ `{network, auth, not_installed, validation, install_failed}`

**Depends on:** None (uses only stdlib + `packaging.version` transitive dep; does not read state files or call other Golazo tools)

## Transitively Affected Capabilities

**None.**

No other capability depends on `mcp-server` (it is a leaf in the dependency graph — everything flows *into* it, nothing flows *out*). Adding a new tool to the server does not change the behavior of any existing tool or capability.

Verification via dependency graph:
- `mcp-server` depends on: `tool-create-workitem`, `tool-transition`, `tool-status`, `tool-bootstrap`, `tool-consent`, `tool-capabilities`, `tool-role-context`
- No capability has `mcp-server` in its `depends_on` list → no transitive impact

## Required `capabilities.yaml` Changes

### Add new capability entry:

```yaml
  - name: tool-update
    description: "Check for and install updates to golazo-copilot from Azure Artifacts"
    key_files:
      - golazo-copilot/src/golazo_copilot/tools/golazo_update.py
    contracts:
      - "golazo_update(action, version?, workspace_path) -> dict"
      - "action='check' -> {current_version, latest_stable, latest_prerelease, update_available}"
      - "action='install' -> {version, success, restart_required, message} | {version, success, error}"
    depends_on: []
```

### Update `mcp-server` capability:

- Add `tool-update` to `depends_on`
- Update contract comment: `list_tools() -> list[Tool]  # 8 tools registered`

## Impact Summary Table

| Capability | Impact | Change |
|------------|--------|--------|
| `mcp-server` | **Direct** | New tool registration, dispatch, formatter |
| `tool-update` | **New** | Entirely new capability |
| `state-model` | None | Not touched |
| `persistence` | None | Not touched |
| `transitions` | None | Not touched |
| `output-validation` | None | Not touched |
| `role-loader` | None | Not touched |
| `tool-create-workitem` | None | Not touched |
| `tool-transition` | None | Not touched |
| `tool-status` | None | Not touched |
| `tool-bootstrap` | None | Not touched (called by user separately post-restart) |
| `tool-consent` | None | Not touched |
| `tool-capabilities` | None | Not touched |
| `tool-role-context` | None | Not touched |

## Risk Assessment

**Overall risk: LOW**

- Purely additive change — no existing behavior modified
- New tool is fully isolated (no state file access, no workflow side effects)
- Server dispatch uses `elif` chain — adding a new branch cannot affect existing branches
- Rollback is trivial: remove the import, tool entry, dispatch branch, and formatter
