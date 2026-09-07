# GCP-0073 Domain Expert Decision Notes

## Expertise Consulted

MCP Python SDK 2.x integration guidance was required because this work crosses a major-version protocol SDK boundary. Guidance was taken from the official MCP Python SDK v1-to-v2 migration guide and current server documentation.

## Verified Guidance

- Keep the low-level `Server` approach and replace decorators with constructor handlers: `on_list_tools` and `on_call_tool`.
- Use `(ServerRequestContext, typed params)` handler signatures.
- Return `ListToolsResult` and `CallToolResult`; MCP 2.x no longer wraps bare lists automatically.
- Read calls from `CallToolRequestParams.name` and `params.arguments or {}`.
- Preserve model imports through `mcp.types`; use snake_case attributes such as `input_schema` and `is_error`.
- Preserve recoverable tool errors by explicitly returning `CallToolResult(is_error=True, ...)`; unhandled low-level exceptions become JSON-RPC errors in MCP 2.x.
- Ensure every advertised input schema has `"type": "object"` because MCP 2.x validates handler results against the protocol schema.
- Keep the existing `stdio_server()` and `Server.run(...)` lifecycle, which remain supported.
- Declare `mcp>=2,<3`; do not independently pin the new transitive `mcp-types` package.

## Constraints And Risks

- Raw-wire snapshots may change because MCP 2.x adds a `_meta` envelope to requests.
- Tests must validate semantic tool contracts rather than expecting MCP 1.x wrapper internals.
- The installed-wheel test must exercise a real list and call exchange, not only import the module.
- Golazo does not use server-initiated sampling, elicitation, roots, resources, or HTTP transports in this migration, so their MCP 2.x changes are out of scope.

## Recommended Design Adjustment

Make the modular registry and handler adapter the only sources used by the two MCP handlers. This reduces the migrated MCP-facing code to typed request/result translation and prevents legacy duplicated registration from drifting.