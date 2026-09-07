# GCP-0073 Quality Assurance Decision Notes

## Decision

The design is approved for architecture with explicit red-first compatibility, contract, and installed-wheel validation. The acceptance criteria are clear and testable; no scope or behavior clarification is required.

## Required Verification

- Capture exact names, descriptions, input schemas, success text, and recoverable error text before production changes.
- Prove the current decorator integration fails the new MCP 2.x tests for the expected reason before implementation.
- Validate typed list/call results, nullable arguments, unknown tools, and recoverable `is_error` behavior.
- Assert `mcp>=2,<3` in source and wheel metadata.
- Run focused and full suites against minimum and latest MCP 2.x.
- Exercise initialize, list, and call over stdio from a clean installed wheel.
- Include resolved Golazo/MCP versions and lifecycle stage in failure diagnostics.
- Pass the full regression suite, Ruff, and greater than 70% coverage for every changed production module.

## Scope Guardrails

No production code or automated tests are created during QA. GCP-0074 and GCP-0075 are excluded, as are workflow behavior changes, new or removed tools, HTTP transports, and MCP 3.x support.