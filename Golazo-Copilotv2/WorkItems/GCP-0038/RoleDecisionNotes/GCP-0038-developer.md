# Developer Notes — GCP-0038

## Implementation Summary

### New Files
| File | Purpose |
|------|---------|
| `tools/gcp_capabilities.py` | Core implementation — registry loading, dependency graph, 4 actions |
| `tests/test_gcp_capabilities.py` | 19 tests across 7 classes covering all 6 ACs |

### Modified Files
| File | Change |
|------|--------|
| `server.py` | Added Tool schema (action enum, capability, files, workspace_path), call_tool handler with formatted markdown output |
| `tools/__init__.py` | Export `gcp_capabilities` |
| `pyproject.toml` | Added `PyYAML>=6.0` dependency |
| `tests/test_gcp_bootstrap.py` | Fixed 2 tests that still expected dynamic version stamping (changed to verify format exists, not specific version) |

## TDD Execution
1. **Red**: Wrote 19 tests first — all failed (no implementation)
2. **Green**: Implemented `gcp_capabilities.py` + server integration — 19/19 pass
3. **Refactor**: Fixed 2 pre-existing test failures from stale version assertions

## Design Decisions

### File Matching Strategy
- **Exact match first** (normalized path comparison)
- **Suffix fallback** (matches `src/foo.py` when capability declares `foo.py`)
- **Multiple capability matches** returned for ambiguous files

### Cycle Detection
- BFS with visited set in `_get_transitive_dependents()`
- Circular dependencies don't cause infinite loops
- `validate` action explicitly detects and reports cycles

### Path Normalization
- Forward slashes, lowercase, no leading `./`
- Cross-platform (Windows backslash handling)

### Security
- `yaml.safe_load()` as recommended by Architect review

## Test Results
- **156 passed, 0 failed** (full suite)
- **19 new tests** for gcp_capabilities
- Coverage: list, show, impact, validate, missing registry, depended_on_by computation, cycle handling, diamond dependencies, suffix matching, unknown capability/action errors

## Deviations from Design
None. Implementation matches design doc exactly.
