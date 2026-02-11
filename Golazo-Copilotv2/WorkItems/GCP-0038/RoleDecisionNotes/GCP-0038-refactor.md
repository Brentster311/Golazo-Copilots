# Refactor Expert Notes — GCP-0038

## Changes Applied
| File | Refactoring | Rationale |
|------|------------|-----------|
| `tools/gcp_capabilities.py` | Replace `list`+`pop(0)` with `collections.deque`+`popleft()` | O(1) dequeue vs O(n) list pop from front in BFS traversal |

## Observations (No Change Made)
1. **`_match_files` suffix fallback**: `key.endswith(inp)` (without `/` prefix) could match partial filenames (e.g., `bar.py` matching `foobar.py`). The `key.endswith("/" + inp)` already handles proper suffix matching. The unconditional `endswith` is overly broad but removing it could change behavior — deferring to a future work item if it causes issues.
2. **`server.py` formatting**: The `call_tool` handler for `gcp_capabilities` has inline formatting logic (~40 lines). This is consistent with all other tool handlers in the same file. Extract-to-function would only be warranted if more tools are added or formatting becomes reusable.
3. **Overall code quality**: New code follows existing patterns, naming is clear, functions are small and focused. No further refactoring needed.

## Test Results
156 passed, 0 failed — no behavior changes.
