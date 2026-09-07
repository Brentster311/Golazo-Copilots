# GCP-0073 Architect Decision Notes

## Decision

Approved to proceed to Developer with one canonical MCP 2.x integration surface. `server.py` will be a thin typed adapter over the existing modular registry and router; handlers and formatters continue to own Golazo behavior and text contracts.

## Integration Strategy

- Register typed list/call handlers through the MCP `Server` constructor.
- Return complete `ListToolsResult` and `CallToolResult` models.
- Normalize nullable call arguments to `{}`.
- Preserve dispatch content exactly and convert caught recoverable `ValueError` failures to `CallToolResult(is_error=True)` with unchanged text.
- Remove duplicated legacy schemas, dispatch branches, and formatter bodies from `server.py`.
- Keep stdio lifecycle and startup self-check behavior.
- Bound dependency metadata to `mcp>=2,<3` without directly pinning `mcp-types`.

## Test And Release Gates

Tests are red-first. Validation covers exact tool contracts, typed handlers/results, minimum MCP 2.0.0, latest MCP 2.x, built-wheel clean stdio initialize/list/call/shutdown, resolved-version diagnostics, full regression, Ruff, and greater than 70% coverage for every changed production module.

## Risks And Mitigations

- **Contract drift:** Registry, handlers, and formatters remain canonical and are snapshot/regression tested.
- **MCP exception drift:** Recoverable errors are caught at the adapter and returned as typed error results.
- **Source-tree false positive:** Wheel tests clear source imports and execute the installed entry point.
- **Resolver drift:** Validate both the minimum and latest allowed MCP 2.x versions; reject MCP 3.x through metadata.
- **Sensitive diagnostics:** Log versions, stage, and exception type only, never arguments or environment contents.

## Scope

No implementation or automated test changes were made during architecture. GCP-0074 and GCP-0075 remain excluded. No new user story is needed because the architecture implements the approved design without changing behavior or scope.