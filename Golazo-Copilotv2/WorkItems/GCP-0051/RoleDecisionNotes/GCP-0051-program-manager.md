# GCP-0051 — Program Manager Decision Notes

## Decisions Made

1. **Approach**: Chose `asyncio.to_thread` wrappers over native async refactoring. The sync helper functions are small and well-tested — wrapping them preserves their testability and minimizes the diff.

2. **Parallel grouping**: All five operations fan out together. Although `_generate_next_steps` depends on output validation results, it runs *after* the gather — it's not part of the parallel group. This keeps the dependency chain clean.

3. **Error isolation via `return_exceptions=True`**: This is the standard `asyncio.gather` pattern. Each failed operation becomes an error marker in the response dict. The alternative (letting one failure crash the whole call) would make `gcp_status` less reliable than it is today.

4. **No new dependencies**: Confirmed the project is on Python 3.10+ and already uses `asyncio` in the MCP server. `asyncio.to_thread` is stdlib.

5. **Test strategy**: Timing tests use mocked delays rather than real I/O to avoid CI flakiness. Error isolation is tested by injecting exceptions via mocks.

## Open Questions

None — this is a well-bounded internal refactor with no external-facing changes.

## Risk Assessment

Low risk overall. The only non-trivial concern is timing-based test flakiness, mitigated by generous margins and mock-based delays rather than real filesystem latency.
