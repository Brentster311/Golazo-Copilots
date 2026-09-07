# GCP-0073 Review Comments

## Domain Expert Guidance

**Expertise:** MCP Python SDK 2.x server integration.

The official migration guide confirms that Golazo can retain the low-level server and stdio lifecycle. Replace decorator registration with `Server(..., on_list_tools=..., on_call_tool=...)`, accept typed context and params, and return complete result models. Preserve tool-visible errors explicitly because low-level exception behavior changed.

The implementation must also account for nullable call arguments, snake_case Python fields, and stricter protocol result validation. The package requirement should be `mcp>=2,<3`, with no direct `mcp-types` pin.

## Quality Assurance Review

The design is testable and covers the acceptance criteria, with these execution requirements:

- Add contract and lifecycle tests before production changes and confirm they fail against the current MCP 1.x decorator integration for the expected compatibility reason.
- Compare semantic tool contracts, not MCP 1.x wire-wrapper details: exact names, descriptions, input schemas, successful text results, and recoverable `is_error` results must remain unchanged.
- Exercise typed `ListToolsResult` and `CallToolResult` handling through the MCP 2.x request path, including omitted or null call arguments and unknown-tool or validation failures.
- Test the declared `mcp>=2,<3` constraint and reject accidental MCP 3.x compatibility claims.
- Run the focused tests and full regression suite against the minimum supported MCP 2.x release and the latest available MCP 2.x release.
- Build a wheel, install it into a clean environment, and perform an actual stdio initialize/list/call exchange against the installed artifact. Import-only or source-tree execution is insufficient.
- On smoke-test failure, print the resolved Golazo version, resolved MCP version, lifecycle stage, and exception type while excluding credentials and call arguments.
- Require Ruff success and greater than 70% coverage for each changed production module. Coverage from unrelated modules must not mask an under-tested changed module.

No acceptance criteria are ambiguous or require escalation. GCP-0074 and GCP-0075 remain outside this work item.

## Architect Notes

### Decision

Approve a thin MCP 2.x adapter in `golazo-copilot/src/golazo_copilot/server.py`. The adapter must use `dispatch.registry.get_tool_definitions()` as the sole schema source and `dispatch.router.dispatch_tool()` as the sole dispatch source. Existing handler and formatter modules remain authoritative for tool invocation and text output.

Construct `Server` with `on_list_tools` and `on_call_tool` after defining the handlers:

- The list handler accepts `ServerRequestContext` and typed list params, ignores only fields Golazo does not use, and returns `ListToolsResult(tools=get_tool_definitions())`.
- The call handler accepts `ServerRequestContext` and `CallToolRequestParams`, dispatches `params.name` with `params.arguments or {}`, and returns `CallToolResult` containing the existing `TextContent` list unchanged.
- Catch the same recoverable `ValueError` boundary as the current server, preserve the exact `[FAIL] ...` text, and return it with `is_error=True`. Do not allow it to become an MCP 2.x JSON-RPC error.
- Leave ordinary dispatch results, including established preflight and unknown-tool text, semantically unchanged. Do not infer error state by parsing formatter text.
- Retain `stdio_server()` and `Server.run(...)`; no transport, authentication, or workflow changes are required.

Delete the legacy duplicate schema, dispatch, and formatter implementations from `server.py`, retaining only deliberate compatibility exports still required by supported internal tests. Do not add a second MCP adapter module unless implementation demonstrates a concrete cycle or testability problem.

### Exact File Plan

Production and package files:

- `golazo-copilot/src/golazo_copilot/server.py`: typed MCP 2.x handlers, constructor registration, typed results, recoverable error boundary, and removal of duplicate legacy implementation.
- `golazo-copilot/pyproject.toml`: set `mcp>=2,<3`; add `pytest-cov` to development dependencies if needed by the coverage gate.
- `golazo-copilot/README.md`: document the supported MCP range, minimum/latest validation, and failure diagnostics.

Preserved integration dependencies, changed only if a red test proves adaptation is necessary:

- `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
- `golazo-copilot/src/golazo_copilot/dispatch/router.py`
- `golazo-copilot/src/golazo_copilot/handlers/tools.py`
- `golazo-copilot/src/golazo_copilot/formatters/results.py`

Test files:

- Add `golazo-copilot/tests/test_gcp0073_mcp2_migration.py` for constructor registration, typed params/results, exact contracts, nullable arguments, and recoverable errors.
- Add `golazo-copilot/tests/test_gcp0073_wheel_stdio.py` for isolated wheel installation, minimum/latest MCP 2.x, initialize/list/call/shutdown, timeouts, clean import paths, and version diagnostics.
- Adapt `test_gcp0061_server_modular_refactor.py`, `test_gcp044_workspace_path.py`, and the direct list call in `test_gcp0072_skill_bootstrap.py` to typed results or the canonical registry as appropriate.
- Remove obsolete duplicate-source assertions from `test_server_legacy_coverage.py`; preserve any still-relevant behavior assertions against modular owners.

### Validation Architecture

The wheel smoke harness should build once, create isolated temporary virtual environments, install the artifact with MCP 2.0.0 and with the latest resolver-selected `mcp>=2,<3`, clear source-tree `PYTHONPATH`, and run a real stdio client initialize/list/call exchange. Use credential-free `golazo_status` version reporting for the call. Capture stage names (`build`, `install`, `start`, `initialize`, `list`, `call`, `shutdown`) and report installed Golazo/MCP versions plus exception type on failure. Bound process startup and shutdown to prevent hangs.

Run the full regression suite and Ruff at both dependency endpoints. Measure every changed production module with `pytest-cov` and require greater than 70% per module, not only aggregate package coverage.

### Security And Operational Review

This migration adds no network listener, credential flow, persistence, or tool. Stdio remains the only transport. Diagnostics must not print environment variables, credentials, workspace content, or call arguments. Dependency exposure is bounded below MCP 3, and the clean install validates artifact metadata rather than a source checkout. Rollback remains atomic: restore the prior package version and matching MCP 1.x integration together.

MCP defaults were examined explicitly: constructor handler registration and typed result validation are required; exception-to-JSON-RPC conversion is not acceptable for recoverable tool failures; nullable arguments normalize to `{}`; and raw `_meta` envelope differences are not part of Golazo's public contract. No Project Owner question remains open.