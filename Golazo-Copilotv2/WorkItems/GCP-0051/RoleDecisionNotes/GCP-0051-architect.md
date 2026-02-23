# GCP-0051 — Architect Decision Notes

## Decisions Made

1. **Architecture approved as-is**: The `asyncio.to_thread` + `asyncio.gather` pattern is the right choice for this codebase — minimal coupling change, no new dependencies, leverages the existing async MCP runtime.

2. **Capability impact is minimal**: Only `tool-status` is directly affected, and `mcp-server` is transitively affected but requires zero changes (same `await` call, same return dict).

3. **No security concerns**: Pure internal refactor of read-only operations. No new entry points, no data exposure changes.

4. **Validated QA concern**: The `_generate_next_steps` dependency on output validation results must be handled with an empty-list fallback when the output validation step fails. This is a concrete implementation requirement, not a design change.

5. **Thread safety confirmed**: Pydantic models (used for `state`) are immutable/frozen after construction. Concurrent reads from multiple `to_thread` workers are safe.

## Capability Registry Impact

- **Directly affected**: `tool-status` (internal implementation only)
- **Transitively affected**: `mcp-server` (no code changes needed)
- Full details in `GCP-0051-Capability-Impact.md`
