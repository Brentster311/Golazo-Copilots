# GCP-0073 Project Owner Assistant Decision Notes

## Origin

Created from the GCP-0072 retrospective after a clean installation of Golazo Copilot `5.0.2` selected MCP `2.1.1` and crashed because the server uses the MCP 1.x decorator API.

## Scope

- Migrate server registration, tool advertisement, and dispatch from removed MCP 1.x APIs to supported MCP 2.x APIs.
- Preserve all existing Golazo tool names, schemas, formatting, and workflow behavior.
- Update the package dependency contract to `mcp>=2,<3`, preventing unvalidated MCP 3.x adoption.
- Validate both the minimum supported and latest available MCP 2.x releases.
- Add installed-wheel startup validation in a clean environment and report resolved versions when compatibility validation fails.
- Treat pinning MCP 1.x only as a rollback option, not the delivered solution.

## Project Owner Clarification

The Project Owner explicitly requested that GCP-0073 move Golazo Copilot to MCP 2.x and guard against an automatic MCP 3.x upgrade. This replaces the original proposal to constrain installation to MCP 1.x.

## Backlog State

This revised work item remains at Project Owner Assistant only. No design, implementation, dependency, version, build, or release change has been started.

## Closure Validation

- AC1 passed: `Server` uses `on_list_tools` and `on_call_tool`; the final wheel contains no `@server.list_tools()` registration.
- AC2 passed: 528 tests passed and 3 skipped under MCP 2.1.1; exact registry/schema and representative formatting assertions passed.
- AC3 passed: clean-installed `golazo-copilot-6.0.0-py3-none-any.whl` completed stdio initialize/list/call/shutdown.
- AC4 passed: MCP 2.0.0 and MCP 2.1.1 each passed all migration tests; smoke diagnostics include package versions, stage, and exception type.
- Dependency guard passed: wheel metadata is `Requires-Dist: mcp<3,>=2`.
- Quality gates passed: server coverage 91%, scoped Ruff clean, capability registry valid.
- Initial implementation commit `fd806a700b90d482eba27c2d0ca5d8eaeaee11f9` was pushed to `origin/brentj/GCP-0073`.

The story is accepted as IMPLEMENTED. GCP-0074 and GCP-0075 remain backlog follow-ups and were not implemented here.