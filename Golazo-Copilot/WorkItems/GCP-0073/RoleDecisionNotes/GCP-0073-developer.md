# GCP-0073 Developer Decision Notes

## Implementation

- Replaced MCP 1.x low-level decorators with MCP 2.x `Server` constructor handlers.
- Added typed `ListToolsResult` and `CallToolResult` adapters over the canonical registry and dispatcher.
- Normalized omitted call arguments to `{}` and preserved recoverable errors as error-marked tool results.
- Declared `mcp>=2,<3` and added a Python 3.10-only `tomli` development fallback.
- Updated tests to use MCP 2.x snake_case model attributes while preserving camelCase wire aliases.
- Added focused MCP 2.x contract tests and a standalone installed-wheel stdio smoke harness.

## TDD Evidence

- Red: 5 failures for missing typed handlers, missing method registration, and the old dependency range.
- Green focused suite: 34 passed after the adapter migration and legacy assertion updates.
- Added stdio lifecycle test passed through initialize, list, call, and shutdown.

## Compatibility Matrix

- MCP 2.0.0: 6 migration tests passed.
- MCP 2.1.1, latest available from the configured package feed: 6 migration tests passed.
- Built wheel metadata: `Requires-Dist: mcp<3,>=2`.
- MCP 1.29.1 and 3.0.0 are outside the declared range.

## Final Validation

- Full suite under MCP 2.1.1: 528 passed, 3 skipped.
- Scoped Ruff: no findings.
- Changed server module coverage: 91%.
- Clean wheel `golazo_copilot-5.1.0-py3-none-any.whl`: installed with MCP 2.1.1 and passed stdio initialize/list/call/shutdown from outside the source tree.
- Capability impact: no registered capabilities affected.

## Scope

No release was published and the package version was not changed because publishing is explicitly out of scope. GCP-0074 and GCP-0075 were not modified.