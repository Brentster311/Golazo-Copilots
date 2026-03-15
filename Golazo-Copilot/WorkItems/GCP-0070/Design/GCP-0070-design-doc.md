# GCP-0070 Design Document

## Summary
Remove the `golazo_update` MCP tool from the Golazo Copilot package and replace update/install guidance with explicit `pip install` instructions in the bootstrap spine and public documentation. This removes a state-changing MCP surface that duplicates package management responsibilities and replaces it with deterministic installation guidance pointing to the correct Azure Artifacts package location.

## Problem Statement
The repository currently exposes a `golazo_update` tool in both modular and legacy server paths. It adds maintenance cost, Azure authentication complexity, and user confusion around package management. The desired direction is to stop managing package upgrades through MCP and instead tell users exactly how to install or upgrade the package from the correct location.

## Business Case
- Simplifies the MCP tool surface by removing a specialized package-management tool.
- Reduces maintenance cost for Azure Artifacts auth, CLI preflight, and platform-specific update behavior.
- Makes installation guidance explicit and discoverable in the orchestrator spine and README.

## Stakeholders
- Golazo Copilot maintainers.
- Users bootstrapping Golazo Copilot into workspaces.
- Users previously relying on README or server output for update guidance.

## Functional Requirements
- Remove `golazo_update` from tool registration.
- Remove `golazo_update` dispatch/handler paths from modular and legacy server code.
- Remove dedicated formatter output paths that describe `golazo_update` usage.
- Remove or update tests that assume `golazo_update` exists.
- Add explicit `pip install` guidance in the bootstrap spine used for orchestrator instructions.
- Update README so install/update guidance no longer references `golazo_update`.

## Non-Functional Requirements
- Keep all remaining tool registrations and dispatch paths unchanged.
- Keep install guidance consistent with the canonical package feed already used by the repo.
- Remove dead code instead of leaving unused update helpers behind.

## Proposed Approach

### 1. Remove tool registration and dispatch wiring
- Delete `golazo_update` from modular tool registry definitions.
- Remove modular handler imports/branches for `golazo_update`.
- Remove legacy server imports, formatter branches, and dispatch branches for `golazo_update`.

### 2. Remove update-tool implementation references
- Remove the `golazo_update` tool module from exported tool surfaces if it is no longer referenced.
- Update package `__init__` exports if needed so removed tool names are not re-exported.

### 3. Replace update guidance with install guidance in the spine
- Update the bootstrap spine content source so generated `.github/agents/Golazo-Copilot.md` includes concise package installation/upgrade instructions.
- Ensure the instructions point to the Azure Artifacts feed already documented in the repo, including any prerequisite keyring guidance if needed.

### 4. Update documentation and tests
- Remove README sections that describe `golazo_update` as a supported MCP tool.
- Update any README upgrade guidance to point directly to the `pip install --upgrade` path.
- Replace tests that assert `golazo_update` exists with tests asserting that it is absent and that spine/install guidance is present.

## Alternatives Considered

### Alternative A: Keep `golazo_update` but de-emphasize it in docs
- Rejected because the user explicitly wants the tool removed, not merely hidden.

### Alternative B: Replace `golazo_update` with a simpler MCP wrapper around `pip install`
- Rejected because it still keeps package management inside the MCP surface.

### Alternative C: Remove the tool but leave server formatter and tests untouched
- Rejected because it would leave dead code and failing references.

## Risks, Mitigations, Open Questions

### Risks
- Hidden references to `golazo_update` may remain in legacy code or tests.
- Spine/install guidance could drift from the actual feed location if copied inconsistently.
- Removing a public MCP tool is a breaking change.

### Mitigations
- Use targeted search across registry, handlers, formatters, server, README, and tests.
- Reuse the existing documented Azure Artifacts feed location already present in the repo.
- Cover the removal with tests that assert the tool is not advertised and that install guidance exists.

### Open Questions
- Whether the deprecated `golazo_update` module file should be deleted immediately or left temporarily unreferenced. Preferred approach for this work item: delete or fully detach it if no tests or exports require it.

## Dependencies
- `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
- `golazo-copilot/src/golazo_copilot/handlers/tools.py`
- `golazo-copilot/src/golazo_copilot/formatters/results.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_update.py`
- bootstrap spine content source used by `golazo_bootstrap`
- `golazo-copilot/README.md`
- related tests under `golazo-copilot/tests/`

## Migration / Rollout / Rollback Plan
- Rollout as a breaking tool-surface cleanup in the next package version.
- Validate registration/dispatch/test behavior after removal.
- Roll back by restoring the removed tool wiring and tests if downstream usage requires it.

## Observability Plan
- No external telemetry changes.
- Verification comes from tests showing the tool is absent and install guidance is present.

## Test Strategy Summary
- Add or update tests to assert `golazo_update` is no longer advertised in tool definitions.
- Add or update tests to assert dispatch no longer expects or formats the removed tool.
- Add bootstrap-content tests for the new explicit `pip install` guidance.
- Run focused registry/dispatch/bootstrap/formatter tests after code changes.
