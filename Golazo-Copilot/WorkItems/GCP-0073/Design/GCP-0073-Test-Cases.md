# GCP-0073 Test Cases

## Test-First Sequence

1. Add the contract, MCP 2.x lifecycle, metadata, and installed-wheel tests before changing production code.
2. Run the focused tests against the current implementation and record red failures caused by removed MCP 1.x decorator behavior or missing MCP 2.x typed results.
3. Migrate production code only after the failures demonstrate the intended compatibility gap.
4. Run focused tests after each implementation step, then the minimum/latest matrix, full regression suite, Ruff, changed-module coverage, and installed-wheel smoke test.

## Acceptance Criteria Mapping

| ID | Acceptance criterion | Test coverage |
|---|---|---|
| AC1 | Supported MCP 2.x registration, listing, and dispatch | TC-01, TC-02, TC-03, TC-04 |
| AC2 | Exact Golazo tool contracts and workflow behavior | TC-02, TC-03, TC-04, TC-05 |
| AC3 | Clean built-wheel startup | TC-08, TC-09 |
| AC4 | Minimum/latest MCP 2.x and diagnostics | TC-06, TC-07, TC-09, TC-10 |

## Focused Contract And Handler Tests

### TC-01: Constructor Handler Registration

- **Given:** MCP 2.x is installed and the Golazo server module is imported.
- **When:** The canonical server is constructed.
- **Then:** It uses constructor-provided `on_list_tools` and `on_call_tool` handlers and does not access removed `Server.list_tools` or `Server.call_tool` decorators.
- **Red-first expectation:** The current implementation fails on the removed decorator API.
- **Failure message:** `Server must register MCP 2.x constructor handlers without MCP 1.x decorators.`

### TC-02: Exact Tool Listing Contract

- **Given:** The pre-migration tool contract is captured from the canonical registry.
- **When:** The typed list handler is invoked with a `ServerRequestContext` and list parameters.
- **Then:** It returns `ListToolsResult`; tool names, descriptions, and `input_schema` values exactly match the captured contract, and every schema has top-level `type: object`.
- **Failure message:** `MCP 2.x list response changed the advertised Golazo tool contract.`

### TC-03: Successful Typed Tool Call

- **Given:** A representative read-only tool and valid arguments.
- **When:** The typed call handler receives `CallToolRequestParams`.
- **Then:** It reads `params.name` and `params.arguments or {}`, dispatches once through the canonical handler, and returns `CallToolResult` with the exact existing text formatting and `is_error` false.
- **Failure message:** `MCP 2.x call response changed successful dispatch or result formatting.`

### TC-04: Omitted Arguments And Recoverable Errors

- **Given:** Calls with omitted/null arguments, invalid input, and an unknown tool name.
- **When:** Each call passes through the MCP 2.x handler.
- **Then:** Omitted/null arguments become `{}`; recoverable failures return the existing user-visible text in `CallToolResult(is_error=True, ...)`; they do not escape as JSON-RPC exceptions.
- **Failure message:** `Recoverable Golazo tool errors must remain tool results under MCP 2.x.`

### TC-05: Registry, Handler, And Formatter Regression

- **Given:** The complete existing registry and representative success/error dispatch cases.
- **When:** Existing contract, dispatch, formatter, status, transition, and validation tests run.
- **Then:** No tools are added or removed, no schema or text formatting drifts, and workflow state behavior is unchanged.
- **Failure message:** `MCP migration introduced a Golazo workflow or tool-contract regression.`

## Dependency And Compatibility Tests

### TC-06: Dependency Metadata Boundary

- **Given:** Source and built-wheel metadata.
- **When:** Requirements are inspected with a packaging-aware parser.
- **Then:** MCP is constrained by the valid PEP 440 specifier `>=2,<3`; there is no direct `mcp-types` pin; MCP 1.x and 3.x do not satisfy the requirement.
- **Failure message:** `Package metadata must declare the supported MCP range as mcp>=2,<3.`

### TC-07: Minimum And Latest MCP 2.x Matrix

- **Given:** Isolated environments for the minimum supported MCP 2.x version and latest available MCP 2.x version below 3.
- **When:** Focused compatibility tests and the full regression suite run in each environment.
- **Then:** Both environments pass with no conditional legacy registration path.
- **Failure message:** `Golazo must pass against both minimum and latest supported MCP 2.x.`

## Built-Wheel Stdio Tests

### TC-08: Clean Installed-Wheel List/Call Exchange

- **Given:** A wheel built from the repository and installed with MCP 2.x into a clean environment with no source-tree import path.
- **When:** A protocol client starts the installed console/server entry point over stdio, initializes it, lists tools, and calls a deterministic credential-free tool.
- **Then:** Initialization completes, the exact expected tools are listed, the call returns the expected formatted result, and the process shuts down cleanly.
- **Failure message:** `Installed wheel failed the clean MCP 2.x stdio initialize/list/call exchange.`

### TC-09: Installed-Wheel Failure Diagnostics

- **Given:** A deliberately failing startup or exchange stage in the clean environment.
- **When:** The smoke-test harness reports the failure.
- **Then:** Output includes resolved Golazo and MCP versions, the lifecycle stage, and exception type; it excludes credentials and tool arguments.
- **Failure message:** `Startup failure diagnostics must identify resolved versions and lifecycle stage without sensitive data.`

## Quality Gates

### TC-10: Full Regression And Static Analysis

- **Given:** The completed migration.
- **When:** The complete test suite and Ruff checks run.
- **Then:** All existing and new tests pass and Ruff reports no violations.
- **Failure message:** `MCP 2.x migration must pass the full regression suite and Ruff.`

### TC-11: Changed-Module Coverage

- **Given:** The set of production modules changed by GCP-0073.
- **When:** Coverage is measured for each changed module using the focused and full suites.
- **Then:** Every changed production module has greater than 70% statement coverage.
- **Failure message:** `Each changed production module must exceed 70% coverage.`

## Reliability And Scope Checks

- The smoke exchange must have bounded startup and shutdown timeouts so a hung stdio process fails deterministically.
- Tests must use credential-free calls and must not make network calls after package installation.
- Raw request snapshots may normalize MCP 2.x `_meta`; semantic Golazo contracts must remain exact.
- Tests must not exercise or implement GCP-0074 or GCP-0075 behavior.