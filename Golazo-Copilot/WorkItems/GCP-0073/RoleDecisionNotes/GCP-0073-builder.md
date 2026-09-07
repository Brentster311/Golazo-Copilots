# GCP-0073 Builder Decision Notes

## Version

- Previous version: `5.1.0`.
- Release version: `6.0.0`.
- Rationale: requiring MCP 2.x and dropping MCP 1.x compatibility is a breaking dependency change, despite preserving Golazo's tool contract.
- `6.0.0` is valid PEP 440 and monotonically greater than `5.1.0`.

## Build Verification

- Source tests under MCP 2.1.1: 528 passed, 3 skipped.
- Server module coverage: 91%.
- Scoped Ruff: no findings.
- MCP 2.0.0 migration tests: 6 passed.
- MCP 2.1.1 migration tests: 6 passed.
- Final wheel built: `dist/golazo_copilot-6.0.0-py3-none-any.whl`.
- Final wheel metadata: `Requires-Dist: mcp<3,>=2`.
- Clean installed-wheel smoke passed with `golazo-copilot=6.0.0`, `mcp=2.1.1`, and stdio initialize/list/call/shutdown complete.

## Capability Registry

Impact analysis found no affected registered capabilities. Registry validation passed: all `bootstrap-skill-installation` key files exist.

## Git Operations

Work is on `brentj/GCP-0073`. The user explicitly authorized commit and push; operations proceed after these notes are finalized.