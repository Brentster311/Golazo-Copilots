# GCP-0051 — Project Owner Assistant Decision Notes

## Decisions Made

1. **Scope**: Pure performance refactor of `gcp_status` — no feature additions, no format changes. The tool's public contract (input parameters, output dict structure) remains identical.

2. **Approach**: Use `asyncio.gather` to parallelize 5 independent data-gathering operations that currently run sequentially. This aligns with the existing async runtime of the MCP server.

3. **Error isolation**: Adopted a resilient pattern where individual step failures produce error markers in the response rather than failing the entire call. This improves reliability beyond just performance.

4. **AC count**: 5 acceptance criteria — within the 3–5 guideline. Each maps to a testable assertion.

5. **No must-ask items apply**: This is an internal library change (not a CLI/GUI/API change), targeting the existing cross-platform Python package, with no new persistence concerns. The must-ask checklist items (interface type, target platform, data persistence) are all inherited from the existing `gcp_status` implementation.

## Assumptions Rationale

- **Five parallelizable operations**: Verified by reading `gcp_status.py` — these 5 functions have no data dependencies on each other; they all depend only on `state` and `role_content` which are loaded sequentially before the fan-out.
- **asyncio.gather**: The MCP server entry point (`server.py`) already uses `async def` handlers and `stdio_server`. No new runtime model needed.
- **to_thread wrapping**: The current functions are sync (file reads, string parsing). `asyncio.to_thread` is the standard approach to run sync I/O in an async context without blocking the event loop.

## Risks

- **Low**: Timing-based tests can be flaky on CI. Mitigated by using generous margins (e.g., assert parallel < sequential * 0.8 rather than exact timing).
- **Low**: `asyncio.to_thread` requires Python 3.9+. The project already targets 3.10+ per pyproject.toml.
