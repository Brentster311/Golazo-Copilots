# GCP-0073 Capability Impact

## Analysis Input

Golazo capability impact was evaluated for:

- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
- `golazo-copilot/src/golazo_copilot/dispatch/router.py`
- `golazo-copilot/src/golazo_copilot/handlers/tools.py`
- `golazo-copilot/src/golazo_copilot/formatters/results.py`
- `golazo-copilot/pyproject.toml`

## Directly Affected

`bootstrap-skill-installation` is directly affected because its MCP schema, handler, and result formatter pass through the migrated server adapter. Its registered contract is:

- `golazo_bootstrap(install_ado_sync_skill, ado_sync_config_confirmed, ado_sync_config) -> dict`
- Workspace and user skill destinations remain unchanged.
- Bootstrap `skills[]` result fields remain unchanged.

The migration must preserve the exact advertised bootstrap schema and formatted response while changing only MCP registration and result wrapping.

## Transitively Affected

None. The registry declares no dependent capabilities.

## Contract Implications

No Golazo public tool is added, removed, or renamed. Names, descriptions, input schemas, required fields, text formatting, workflow behavior, stdio transport, and recoverable error text remain stable. The internal SDK-facing contract changes from MCP 1.x decorators and bare lists to MCP 2.x constructor handlers with typed params and `ListToolsResult`/`CallToolResult` results.

Package compatibility changes intentionally from unbounded `mcp>=1.0.0` to `mcp>=2,<3`. MCP 1.x and MCP 3.x are outside the supported package contract after this work item.

## Verification

Contract snapshots, modular dispatch regressions, and the clean installed-wheel stdio list/call exchange must include `golazo_bootstrap`. Any registry, handler, or formatter change requires rerunning the capability impact analysis; the preferred implementation leaves those files behaviorally unchanged.