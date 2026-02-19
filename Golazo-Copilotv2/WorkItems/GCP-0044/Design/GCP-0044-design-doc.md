# GCP-0044 — Design Doc: Make `workspace_path` Required on All MCP Tools

## Summary
Change `workspace_path` from optional to required on all 6 MCP tool schemas, and remove the `Path.cwd()` fallback in `resolve_work_items_dir()`. This prevents work items from being silently created in the wrong directory.

## Problem Statement
The MCP server process's `Path.cwd()` is the MCP server's working directory (typically `C:\Users\<user>`), not the VS Code workspace the user has open. When `workspace_path` is omitted, `resolve_work_items_dir()` falls back to `cwd`, causing:
- `state.json` created at `C:\Users\Brent\WorkItems\<id>\` instead of the project
- Output files written to the correct project workspace by the agent (using absolute paths)
- `gcp_status` finds state.json at `cwd` but not the output files → reports 0/2 outputs
- `gcp_transition` with explicit `workspace_path` can't find state.json → "does not exist"

This was observed in production with work item `capacity-denial-viz`.

## Business Case
- **Why now**: Active user hit this bug. It creates a confusing, unrecoverable state.
- **Impact**: Any user whose VS Code workspace differs from the MCP server cwd (which is most users) will hit this if they or the agent omit `workspace_path`.
- **KPI**: Zero work items created outside the intended workspace.

## Stakeholders
- Golazo Copilot users (all affected)
- MCP clients (must now always pass `workspace_path`)

## Functional Requirements
1. All 6 tool schemas must list `workspace_path` in their `required` array.
2. `resolve_work_items_dir(workspace_path=None)` must return an error, not fall back to `cwd`.
3. `gcp_bootstrap` and `gcp_capabilities` (which resolve workspace internally) must also fail clearly when `workspace_path` is `None`.
4. Error messages must be actionable.

## Non-Functional Requirements
- No changes to tool function signatures (they already accept explicit paths).
- All existing tests pass unchanged (they call functions directly with explicit paths).

## Proposed Approach

### Step 1: Update `resolve_work_items_dir()` in `server.py`
Remove `Path.cwd()` fallback. If `workspace_path` is `None` or empty, return an error or raise.

```python
def resolve_work_items_dir(workspace_path: str | None) -> Path:
    if not workspace_path:
        raise ValueError("workspace_path is required")
    return (Path(workspace_path) / "WorkItems").resolve()
```

### Step 2: Update `call_tool()` handlers in `server.py`
Add early validation in each handler that uses `resolve_work_items_dir`. Catch `ValueError` and return a user-friendly error.

### Step 3: Update all 6 tool schemas in `list_tools()`
Add `"workspace_path"` to each tool's `required` array.

### Step 4: Update `gcp_bootstrap` handler
The bootstrap handler passes `workspace_path` directly to the function. Add validation that it's not None before calling.

### Step 5: Update `gcp_capabilities` handler
Same — validate `workspace_path` is provided before calling.

## Alternatives Considered
| Alternative | Pros | Cons | Decision |
|---|---|---|---|
| Make workspace_path required (chosen) | Simple, correct, no heuristics | Breaking change for callers omitting it | **Chosen** |
| Persist workspace at bootstrap | Auto-resolution after first use | New config file, bootstrap dependency, stale path risk | Rejected |
| Walk upward from cwd for markers | No breaking change | Fragile in monorepos, can match wrong project | Rejected |

## Risks, Mitigations, Open Questions
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Breaking change for existing callers | Medium | Medium | MCP schema enforcement means clients get a clear error before the tool runs |
| Agent doesn't pass workspace_path | Low | Low | Error message instructs what to provide; MCP clients typically auto-populate required params |

**Open Questions**: None.

## Dependencies
None.

## Affected Capabilities
- **Directly**: `mcp-server` (server.py is the only file changing)
- **Transitively**: All tools route through server.py, but their function signatures don't change

## Migration / Rollout / Rollback Plan
- **Migration**: MCP client configurations that omit `workspace_path` must be updated. The schema marks it required, so MCP-compliant clients will prompt for it.
- **Rollback**: Revert `required` arrays and restore `Path.cwd()` fallback.

## Observability Plan
None needed — errors are returned directly to the caller.

## Test Strategy Summary
- **Unit tests**: Existing tests call tool functions directly with explicit paths — unaffected.
- **Server-layer test**: Verify `resolve_work_items_dir(None)` raises `ValueError`.
- **Schema test**: Verify all 6 tools include `workspace_path` in `required`.
