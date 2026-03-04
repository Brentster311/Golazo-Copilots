**Status**: BACKLOG

**User Story**
- Title: Refactor MCP server dispatch into modular handlers without changing tool behavior
- As a: Golazo Copilot maintainer
- I want: `server.py` dispatch and registration logic split into focused modules
- So that: adding and maintaining tools is safer, faster, and less error-prone while preserving current runtime behavior
- Out of scope:
  - New end-user workflow features or new MCP tools
  - Changes to tool input/output contracts
  - Changes to workflow gate rules, role order, or state schema semantics
- Assumptions:
  - Assumption (explicit): This item addresses the maintainability follow-up identified in GCP-0060 closure notes.
  - Assumption (explicit): Existing MCP tool names and response shapes are backward-compatibility constraints and must remain stable.
  - Assumption (explicit): Refactor work remains internal to `golazo-copilot/src/golazo_copilot` and is validated by existing automated tests.
- Acceptance Criteria (bulleted, testable):
  - Given current `server.py` behavior, when refactor is complete, then tool registration and dispatch are organized in modular components with clear boundaries (routing/formatting/handlers) and `server.py` is materially reduced in responsibility.
  - Given existing registered tools, when MCP calls are executed after refactor, then tool names, required parameters, and success/error response contracts remain unchanged.
  - Given regression test suites for server dispatch and role/workflow tools, when executed after refactor, then all relevant tests pass without requiring test expectation changes for API behavior.
  - Given invalid or missing parameters for existing tools, when requests are processed after refactor, then deterministic validation/error messaging remains equivalent to pre-refactor intent.
  - Given maintainers onboarding to server internals, when reviewing the new structure, then module responsibilities and extension points are documented in concise developer-facing notes.
- Non-functional requirements:
  - No measurable regression in normal MCP request latency for existing tool calls.
  - Refactor changes are incremental and reviewable, minimizing cross-file churn outside server plumbing.
  - Code organization must preserve readability, testability, and deterministic error handling.
- Telemetry / metrics expected:
  - Number of dispatch pathways migrated out of `server.py`
  - Post-refactor pass rate for server and workflow regression tests
  - Count of contract regressions detected (target: zero)
- Rollout / rollback notes:
  - Rollout as an internal refactor release with focused regression coverage.
  - Rollback by restoring prior `server.py` dispatch wiring if contract regressions are detected.

## Closure

- Definition-phase closure complete for `project-owner-assistant`.
- User story is ready for orchestrator-managed transition to downstream roles.
- Implementation closure (code/test evidence) is deferred to technical roles and final closure mode.
