# GCP-0073 Design: Migrate Golazo Copilot to MCP SDK 2.x

## Summary

Migrate Golazo Copilot from removed MCP 1.x server decorators to supported MCP 2.x APIs, preserve every existing Golazo tool contract, constrain the package to `mcp>=2,<3`, and add built-wheel startup validation against the minimum and latest MCP 2.x releases.

## Problem Statement

Golazo currently declares `mcp>=1.0.0` while its server uses MCP 1.x decorator methods. A normal installation selected MCP 2.1.1 and crashed at import with `Server.list_tools` missing. Pinning MCP 1.x would defer the incompatibility but would not move the product onto the current SDK.

## Business Case

Users must be able to install the latest Golazo package without manually repairing dependencies. A bounded MCP 2.x range also prevents an unvalidated future MCP 3.x release from recreating this failure.

Success is measured by preserved tool schemas and behavior, full regression success, protocol startup from an installed wheel, and matrix validation at both supported ends of MCP 2.x.

## Stakeholders

- Golazo Copilot users and package installers.
- Maintainers of the MCP server, dispatch layer, and release pipeline.
- Consumers relying on stable Golazo tool names and schemas.

## Functional Requirements

1. Replace MCP 1.x registration and request handling with supported MCP 2.x APIs.
2. Preserve all advertised Golazo tool names, descriptions, schemas, dispatch behavior, and text formatting.
3. Declare `mcp>=2,<3` in package metadata.
4. Validate the built wheel in a clean environment against the minimum supported and latest available MCP 2.x versions.
5. Report resolved Golazo and MCP versions when startup validation fails.

## Non-Functional Requirements

- Preserve cross-platform support and stdio transport.
- Maintain one canonical registration/dispatch implementation where practical.
- Add no unrelated workflow behavior changes.
- Keep startup deterministic and free of network calls after installation.
- Maintain focused module coverage above 70%.

## Proposed Approach

1. Inspect MCP 2.x public server APIs and map the existing list/call/run lifecycle to supported equivalents.
2. Capture the current tool contract in tests before production changes.
3. Migrate the canonical server entry point and remove or delegate obsolete duplicated registration paths.
4. Update dependency metadata to `mcp>=2,<3`.
5. Run unit, integration, stdio startup, full regression, built-wheel, and dependency-matrix validation.
6. Document the supported MCP range and upgrade policy.

## Alternatives Considered

- **Pin MCP below 2:** Rejected as the final solution because the Project Owner requested MCP 2.x migration.
- **Allow unbounded MCP versions:** Rejected because a future major version may break the API again.
- **Maintain separate MCP 1.x and 2.x implementations:** Rejected unless architecture proves compatibility cannot be achieved through one clear MCP 2.x surface.

## Risks And Mitigations

- **Protocol/API misunderstanding:** Validate against installed MCP 2.x public APIs and protocol-level tests.
- **Tool contract drift:** Snapshot/assert exact names and schemas before migration.
- **Import-only false confidence:** Start the built-wheel server through stdio in a clean environment.
- **Minimum/latest divergence:** Exercise both dependency endpoints.
- **MCP 3.x breakage:** Enforce `<3` in package metadata and tests.

## Dependencies

- MCP SDK 2.x public server APIs.
- Existing modular registry, handlers, and formatters.
- Python build and isolated environment tooling.

## Migration, Rollout, And Rollback

- Migrate in one release so package metadata and server API remain aligned.
- Do not publish until both MCP 2.x endpoints and the installed wheel pass.
- Roll back to the last MCP 1.x-compatible Golazo release as a complete package; never mix MCP 1.x code with MCP 2.x metadata.

## Observability Plan

No external telemetry. CI and smoke-test failures print the resolved Golazo and MCP versions, failing lifecycle stage, and exception type without credentials.

## Test Strategy Summary

- Contract tests for exact tool names and schemas.
- Handler tests for representative and error dispatch paths.
- MCP 2.x lifecycle and stdio startup tests.
- Full existing suite under MCP 2.x.
- Built-wheel clean-environment tests with minimum and latest MCP 2.x.
- Metadata assertion for `mcp>=2,<3`.