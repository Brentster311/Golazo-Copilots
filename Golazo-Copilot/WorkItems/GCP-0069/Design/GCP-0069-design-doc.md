# GCP-0069 Design Document

## Summary
Add a `scope` parameter to `golazo_bootstrap` so orchestrator instructions can be installed either in the target workspace or in the active user Copilot directory. Keep workspace scope as the default. Update workflow preflight instruction resolution so operations like `golazo_create_workitem` accept orchestrator instructions from the active user scope when the running agent is installed there.

## Problem Statement
Current bootstrap behavior always writes `.github/agents/Golazo-Copilot.md` into the target workspace. Current workflow preflight logic also only checks for that workspace-local file. This breaks valid user setups where the active Golazo agent runs from a user Copilot directory such as `C:\Users\brentj\.copilot`, because workflow operations fail even when the orchestrator instructions exist in the place the agent is actually using.

## Business Case
- Removes a blocking failure for user-scope Golazo agent installations.
- Preserves backward compatibility for existing workspace-scoped installs.
- Reduces support churn caused by bootstrap succeeding but later workflow operations failing.

## Stakeholders
- Project Owner using Golazo Copilot from a user Copilot directory.
- Developers maintaining the Golazo MCP server.
- Existing workspace-scoped users who require unchanged behavior by default.

## Functional Requirements
- `golazo_bootstrap` accepts a new `scope` parameter.
- Supported `scope` values are `Workspace` and `User`.
- Omitted or empty `scope` behaves as `Workspace`.
- `scope="Workspace"` preserves current file placement behavior.
- `scope="User"` writes orchestrator instructions into the active user Copilot directory instead of the target workspace.
- Bootstrap output reports the resolved installation location.
- Workflow preflight instruction lookup accepts either workspace-scoped or active user-scoped orchestrator instructions.
- Invalid `scope` input returns a clear validation error.

## Non-Functional Requirements
- Preserve existing public behavior for callers that do not pass `scope`.
- Keep path handling based on `pathlib.Path`.
- Minimize duplication by centralizing instruction path resolution.
- Update automated tests for both modular dispatch code and legacy server code paths.

## Proposed Approach

### 1. Extend bootstrap API and schema
- Update the async tool implementation in `src/golazo_copilot/tools/golazo_bootstrap.py` to accept `scope: str | None = "Workspace"`.
- Normalize empty input to `Workspace`.
- Reject unsupported values before file writes.
- Update tool definitions in both dispatcher surfaces so the MCP schema advertises the new parameter.

### 2. Centralize scope-aware instruction resolution
- Add shared helpers in `src/golazo_copilot/dispatch/paths.py` for:
  - resolving the workspace instructions path,
  - resolving the active user Copilot instructions path,
  - resolving the effective bootstrap destination for a given scope,
  - checking whether orchestrator instructions exist in any valid effective location.
- Mirror legacy server usage by importing and reusing the same helper instead of maintaining separate workspace-only logic.

### 3. Determine user-scope base path
- Use a user Copilot directory derived from the runtime environment, anchored to the user home directory and `.copilot`.
- The orchestrator file path under user scope remains `.github/agents/Golazo-Copilot.md` beneath that user Copilot root.
- This keeps bootstrap and validation aligned with the user example while avoiding workspace-path misuse.

### 4. Update workflow preflight validation
- Replace workspace-only checks in `dispatch/router.py` and the legacy path in `server.py` with the shared scope-aware instruction existence helper.
- Preserve the current failure message shape, but update the recovery guidance when useful to mention `scope="User"` as an option.

### 5. Update result formatting
- Extend bootstrap result payload with the resolved target path and scope used.
- Include that location in formatted bootstrap output so users can verify where instructions were written.

## Alternatives Considered

### Alternative A: Bootstrap only, no preflight change
- Rejected because it would still leave `golazo_create_workitem` failing for user-scope installs.

### Alternative B: Infer scope solely from workspace path
- Rejected because bootstrap destination and workflow validation must reflect the active agent install location, not the target project workspace.

### Alternative C: Duplicate user-scope checks separately in bootstrap, router, and server
- Rejected because it increases drift risk across modular and legacy dispatch paths.

## Risks, Mitigations, Open Questions

### Risks
- User-scope path inference may diverge from the actual active agent location on some machines.
- Updating one dispatch path but not the other could leave inconsistent behavior.
- Output changes could break tests that assert exact bootstrap text.

### Mitigations
- Use one shared resolver in `dispatch/paths.py` and route all checks through it.
- Keep the user-scope convention explicit and covered by tests.
- Add focused tests for both modular router helpers and legacy server preflight behavior.

### Open Questions
- Whether the active user Copilot directory should later become configurable beyond the home-directory `.copilot` convention. This is not required for the current user story.

## Dependencies
- `src/golazo_copilot/tools/golazo_bootstrap.py`
- `src/golazo_copilot/dispatch/paths.py`
- `src/golazo_copilot/dispatch/router.py`
- `src/golazo_copilot/handlers/tools.py`
- `src/golazo_copilot/formatters/results.py`
- `src/golazo_copilot/server.py`
- Existing bootstrap and dispatch tests under `tests/`

## Migration / Rollout / Rollback Plan
- Rollout as a backward-compatible release with `Workspace` as the default behavior.
- Add tests first for user scope and unchanged workspace scope behavior.
- Roll back by reverting the `scope` parameter and scope-aware resolution if regressions appear.

## Observability Plan
- No external telemetry changes.
- Use bootstrap result messaging to expose the effective target scope and path.

## Test Strategy Summary
- Add bootstrap tests for omitted scope, explicit workspace scope, explicit user scope, and invalid scope.
- Add path/helper tests for instruction existence across workspace and user scope.
- Add workflow preflight tests so `golazo_create_workitem`-style checks pass when only user-scope instructions exist.
- Run the targeted bootstrap and dispatch test suites, then the broader relevant server tests.