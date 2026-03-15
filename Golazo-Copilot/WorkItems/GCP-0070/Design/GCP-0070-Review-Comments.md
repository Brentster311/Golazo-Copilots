# GCP-0070 QA Review Comments

## Review Outcome
- **Decision**: Pass with comments.
- **Reasoning**: The design is narrow, testable, and feasible, but implementation must remove all visible and hidden `golazo_update` references across modular and legacy code paths.

## Strengths
- The scope is explicit and limited to one behavior change: removing a single MCP tool and replacing it with package install guidance.
- The design correctly includes registry, dispatch, formatter, README, bootstrap spine, and tests rather than treating tool removal as registration-only cleanup.
- The replacement guidance reuses the repository's existing package feed instead of inventing a new source.

## Risks and Actionable QA Comments

### 1. Hidden references may survive outside registration
- **Observation**: `golazo_update` currently appears in registry, handlers, formatters, legacy server code, README, and multiple tests.
- **Risk**: Partial removal could leave stale help text, imports, or failing formatter assumptions.
- **QA Recommendation**: Treat repository-wide reference cleanup as required verification, not optional cleanup.

### 2. Install guidance must be validated at the source used by bootstrap
- **Observation**: The user asked specifically for guidance in the spine.
- **Risk**: Updating README alone would satisfy discoverability but not generated bootstrap instructions.
- **QA Recommendation**: Add a bootstrap-content assertion that generated orchestrator instructions contain the new `pip install` guidance.

### 3. Tool-surface removal is a breaking change
- **Observation**: Removing an advertised MCP tool changes the public interface.
- **Risk**: Tests may still assume the tool exists, and docs may understate the change.
- **QA Recommendation**: Ensure versioning and release notes/documentation clearly reflect the removed tool surface.

## QA Gate Decision
- **Gate Status**: PASS WITH COMMENTS
- **Blocking issues**: None.
- **Required implementation discipline**: remove all tool references and replace them with test-backed install guidance.

## Architect Notes

### Architectural assessment
- The change is architecturally sound because it reduces the public MCP surface and removes a high-maintenance package-management path from the server.
- The work should be treated as a contract removal across modular registry, modular handlers, legacy server wiring, output formatting, and documentation.

### Key constraints
- Do not leave the `golazo_update` implementation reachable through any import/export path after removal.
- Keep the replacement install guidance sourced from the canonical package feed already documented by the repository.
- Remove dead formatter/help text so runtime messaging cannot advertise a removed tool.

### Security and operability
- Security posture improves because the MCP surface no longer exposes a state-changing install path with Azure authentication behavior.
- No new secrets, auth boundaries, or external network dependencies are introduced by the replacement guidance.

### Architectural decision
- Proceed with full removal and documentation replacement. No additional architecture work item is required.
