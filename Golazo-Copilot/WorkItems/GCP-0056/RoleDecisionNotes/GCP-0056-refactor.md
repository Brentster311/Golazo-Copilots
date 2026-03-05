# GCP-0056 Refactor Decision Notes

## Pre-Refactoring Verification

- **30/30** `test_golazo_update.py` tests passing
- **178/178** full non-broken suite tests passing

---

## Modularity Audit

| File | Lines (before) | Lines (after) | Funcs/Classes (before) | Funcs/Classes (after) | Action |
|------|---------------|--------------|----------------------|---------------------|--------|
| `golazo_update.py` | 267 | 260 | 8 | 12 | **Refactored** — Extract Method on `_action_install` |
| `server.py` | 553 | 553 (unchanged) | 14 | 14 | No action — pre-existing file, GCP-0056 changes were minimal (import, schema, dispatch, formatter) |
| `tools/__init__.py` | 10 | 10 (unchanged) | 0 | 0 | No action — trivially small barrel file |
| `test_golazo_update.py` | 492 | 492 (unchanged) | 52 | 52 | No action — test file with 30 test methods across 10 classes; high count is expected |

### golazo_update.py — Detailed Analysis

- **Lines**: 267 → 260 (under 300 ✓, flagged for review at >200)
- **Functions/classes**: 8 → 12. The increase is justified:
  - `_action_install` was ~80 lines with 6 sequential responsibilities (version validation, 3 pre-flight checks, pip execution, success response)
  - Extracted 4 focused helpers: `_install_error`, `_validate_install_version`, `_check_auth_prerequisites`, `_run_pip_install`
  - `_action_install` reduced from ~80 lines to 8 lines (pure orchestration)
  - All extracted functions are private (`_` prefix); the single public function `golazo_update()` is unchanged
  - 12 total defs includes 2 methods on the private `_AnchorParser` class — effective standalone function count is 9 + 1 class
- **Single responsibility**: ✓ — file handles update tool (check + install). The two actions share constants and the feed URL.
- **Code smells addressed**:
  - **Long Method**: `_action_install` was a sequential chain of validation → pre-flight → execution → result construction. Now each concern is isolated.
  - **Repeated dict literal**: Error dicts all shared `{"status": "error", "action": "install", ...}`. Extracted to `_install_error()` factory.

### server.py — Detailed Analysis

- **Lines**: 553 (exceeds 300-line threshold)
- **Functions/classes**: 14 (exceeds 10-function threshold)
- **Action**: No refactoring in this work item scope. This file is pre-existing and already exceeded thresholds before GCP-0056. The GCP-0056 additions were:
  - 1 import line
  - 1 tool schema entry in `list_tools` (~20 lines, consistent with existing pattern)
  - 1 dispatch case in `_dispatch_tool` (~8 lines, consistent with existing pattern)
  - 1 formatter function `format_update_result` (~35 lines)
- Splitting `server.py` would be a cross-cutting refactoring affecting all capabilities, not scoped to GCP-0056.

### test_golazo_update.py — Detailed Analysis

- **Lines**: 492 (exceeds 300-line threshold)
- **Functions/classes**: 52 (30 test methods + 10 test classes + 12 helper functions/fixtures)
- **Action**: No refactoring. Test files are expected to be longer. The file is well-organized with test classes mapping to acceptance criteria groups. Helper functions at the top (mock factories) are reused across classes.

---

## Refactoring Applied

### Extract Method — `_action_install` decomposition

**Pattern**: Extract Method (Fowler)

**Before**: `_action_install` was a single 80-line async function with 6 sequential concerns:
1. Version presence check
2. Version format validation  
3. keyring availability check
4. artifacts-keyring availability check
5. Azure CLI login check
6. pip install execution + result construction

**After**: 4 extracted helpers + a 8-line orchestrator:
- `_install_error(error, **kwargs)` — standardised error dict factory
- `_validate_install_version(version)` → error dict | None
- `_check_auth_prerequisites()` → error dict | None  
- `_run_pip_install(version)` → full result dict
- `_action_install(version, workspace_path)` — orchestrates the above

**Rationale**: Each function now does exactly one thing. The orchestrator reads as a simple pipeline. Error construction is DRY via `_install_error`.

**Risk**: Low — all existing tests exercise the same code paths through the unchanged public API `golazo_update()`. Mock patches target module-level imports (`importlib.util.find_spec`, `subprocess.run`) which work identically regardless of which internal function calls them.

---

## Linter Check

- **pyproject.toml**: No linter configured (no `[tool.ruff]`, `[tool.flake8]`, or `[tool.pylint]` sections)
- **Runtime**: `ruff`, `flake8`, and `pylint` are not installed in the environment
- **Action**: None possible. Recommend adding `ruff` to `[project.optional-dependencies].dev` in a future work item.

---

## Capability Registry Impact

```
golazo_capabilities(action="impact", files=[...])
```

- **Directly affected**: `mcp-server` — MCP server entry point
- **Transitively affected**: None
- **Assessment**: Safe. The refactoring is internal to `golazo_update.py` (private function decomposition). The public API (`golazo_update()`) signature and return value contracts are unchanged. The `mcp-server` capability's dispatch and formatting code was not modified.

---

## Post-Refactoring Verification

- **30/30** `test_golazo_update.py` tests passing ✓
- **178/178** full non-broken suite tests passing ✓
- No behavior changes introduced ✓

---

## Assumptions

- `server.py` refactoring (553 lines, 14 functions) is out of scope — it's a pre-existing file and splitting it would affect all capabilities, not just GCP-0056.
- Test file line count (492) is acceptable for 30 test cases with well-organized test classes.
- The function count increase (8 → 12) in `golazo_update.py` is a net positive — smaller focused functions over fewer large ones.
