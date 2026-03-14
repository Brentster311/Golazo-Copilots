# GCP-0069 QA Review Comments

## Review Outcome
- **Decision**: Pass with comments.
- **Reasoning**: The design is minimal, testable, and consistent with the reported failure, but implementation must avoid partial fixes across duplicated bootstrap and dispatch paths.

## Strengths
- The design preserves backward compatibility by keeping workspace scope as the default.
- It correctly treats user-scope support as both a bootstrap and a workflow-preflight concern.
- It identifies a shared helper as the right way to avoid drift between modular and legacy server code paths.

## Risks and Actionable QA Comments

### 1. Input normalization must be explicit
- **Observation**: The story requires omitted or empty `scope` to behave as `Workspace`.
- **Risk**: Implementations may treat `""` differently from omitted input, creating caller-visible inconsistency.
- **QA Recommendation**: Add direct tests for omitted scope, empty scope, and explicit `Workspace` to prove identical behavior.

### 2. Invalid scope handling needs stable error text intent
- **Observation**: The story requires a clear validation error for unsupported values.
- **Risk**: Vague or inconsistent messages make MCP usage harder to diagnose and create brittle support flows.
- **QA Recommendation**: Assert that the error names the invalid value and the supported values `Workspace` and `User`.

### 3. User-scope bootstrap without preflight coverage is insufficient
- **Observation**: The reported bug happens during workflow operations, not bootstrap itself.
- **Risk**: A patch that only writes to user scope will still fail on `golazo_create_workitem`.
- **QA Recommendation**: Require tests that prove workflow preflight passes when only user-scope instructions exist.

### 4. Modular and legacy dispatch paths must both be covered
- **Observation**: The codebase keeps both modular dispatch helpers and legacy server coverage expectations.
- **Risk**: Fixing only `dispatch/router.py` or only `server.py` creates inconsistent behavior depending on entry path.
- **QA Recommendation**: Add tests for both `dispatch.paths` behavior and `server._dispatch_tool` behavior.

### 5. Result reporting should expose the effective install target
- **Observation**: The user must be able to tell where bootstrap wrote instructions.
- **Risk**: Silent placement to user scope makes troubleshooting harder.
- **QA Recommendation**: Assert bootstrap result payload and formatted output both reflect the resolved target scope/path.

## QA Gate Decision
- **Gate Status**: PASS WITH COMMENTS
- **Blocking issues**: None, provided the implementation follows the required test coverage below.

## Architect Notes
- **Architectural decision**: Centralize all orchestrator instruction path resolution in a shared helper and reuse it from bootstrap, modular dispatch, and legacy server code. This is the lowest-risk way to avoid inconsistent user-scope behavior.
- **Contract guidance**: Treat `scope` as a strict input contract with supported values `Workspace` and `User`. Normalize omitted and empty input explicitly rather than relying on Python truthiness in multiple places.
- **Security/privacy**: No new credential, authentication, or PII handling is introduced. File writes remain local and bounded to workspace or user Copilot directories.
- **Failure isolation**: Validation must fail fast on invalid scope before any directories or files are created.
- **Blast radius**: Primary regression risk is breaking existing workspace-only behavior or updating only one of the two dispatch paths. This risk is acceptable with targeted regression tests.
- **Operability**: Bootstrap output should expose the effective target path so users can diagnose scope mismatches without reading source code.
