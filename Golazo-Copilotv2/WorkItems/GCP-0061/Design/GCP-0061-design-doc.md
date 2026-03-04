# GCP-0061 Design Document — Modular MCP Server Dispatch Refactor (Behavior Preserving)

## Summary
This work item refactors MCP server dispatch and tool registration internals by decomposing `server.py` into focused modules (routing, handlers, formatting/response utilities) while preserving existing tool behavior. The objective is maintainability and safer extension velocity with zero contract drift for currently registered tools.

## Problem Statement
- `server.py` currently carries multiple responsibilities (registration, dispatch, validation/error shaping), increasing coupling and change risk.
- Adding or modifying tools in a highly centralized file makes regressions more likely and review quality harder to sustain.
- Maintainers need clear boundaries so dispatch-path changes are testable and reasoned about independently.

## Business Case
### Why now
- The item is an explicit maintainability follow-up from GCP-0060 closure notes.
- Existing tool surface area is large enough that centralized dispatch logic now creates avoidable operational risk.

### Impact
- Reduces regression risk for future tool additions by isolating routing/handler/formatting responsibilities.
- Improves onboarding speed by making extension points explicit and localized.
- Maintains runtime behavior and external contracts for existing automations and downstream roles.

### KPIs
- Number/percentage of dispatch pathways migrated out of `server.py`.
- Regression test pass rate for server/workflow/tool suites after refactor.
- Contract regression count for tool names, required params, and success/error shapes (target: zero).
- Optional maintainability proxy: `server.py` net reduction in orchestration complexity (qualitative review gate).

## Stakeholders
- Golazo Copilot maintainers (primary): implement and evolve MCP tools safely.
- Architect and reviewer roles: need inspectable module boundaries and low-risk sequencing.
- QA/on-call maintainers: require deterministic failure behavior and rollback clarity.
- Downstream automation/users of existing tools: depend on stable contracts.

## Requirements
### Functional Requirements
1. Split `server.py` dispatch/registration concerns into focused modules with clear boundaries:
   - routing/dispatch path selection
   - tool handler implementations/adapters
   - response formatting/error normalization utilities
2. Preserve all existing MCP tool names and tool registration outcomes.
3. Preserve required parameter semantics and validation behavior for existing tools.
4. Preserve success/error contract shapes and deterministic messaging intent for existing tools.
5. Keep a thin orchestration layer in `server.py` after extraction.
6. Add concise developer-facing notes documenting boundaries and extension points.

### Non-Functional Requirements
1. No measurable regression in normal MCP request latency.
2. Refactor is incremental and reviewable, minimizing broad churn outside server plumbing.
3. Readability/testability improve through module cohesion and lower coupling.
4. Error handling remains deterministic and operationally actionable.

## Proposed Approach
### High-Level Plan
1. Establish target module boundaries and ownership (dispatch routing, handler groups, response/format utilities).
2. Extract pure utility logic first (format/validation helpers) with behavior-parity tests.
3. Extract handler groups behind stable function interfaces consumed by dispatch.
4. Move registration map/wiring into dedicated registration module while preserving exact tool names/signatures.
5. Reduce `server.py` to bootstrap/orchestration only.
6. Add/refresh tests focused on contract parity and deterministic error behavior.
7. Add concise maintainers’ notes for extension flow (where to register and where to implement).

### Implementation Shape (Conceptual)
- `server.py`: startup/bootstrap, module wiring, minimal orchestration.
- `dispatch/*`: route selection and dispatch table composition.
- `handlers/*`: grouped tool handling logic with narrow interfaces.
- `formatters/*` (or equivalent): success/error response construction and normalization.
- Shared validation utilities reused to prevent drift in required-parameter checks.

## Alternatives Considered
1. Keep monolithic `server.py` and add comments only.
   - Rejected: documentation alone does not reduce coupling or regression risk.
2. Full rewrite of dispatch architecture in one large change.
   - Rejected: high blast radius and poor rollback/review ergonomics.
3. Introduce new tool abstraction layer and contract changes during refactor.
   - Rejected: violates explicit out-of-scope and compatibility constraints.

## Risks, Mitigations, Open Questions
### Risks
1. Hidden behavior drift during extraction (especially error messaging/validation order).
2. Registration mismatches causing missing/renamed tools at runtime.
3. Latency regressions from added indirection.
4. Large diff complexity reducing review confidence.

### Mitigations
1. Contract-parity tests before/after extraction for representative tools and failure paths.
2. Snapshot/explicit assertions for registered tool names and required parameters.
3. Stage extraction in small PR slices with clear module-by-module acceptance checks.
4. Keep rollback path simple by preserving previous wiring until parity is verified.

### Open Questions
- Non-blocking: Should future work centralize shared parameter-validation schema to further reduce drift risk across handlers?

## Dependencies
- Existing MCP server registration/dispatch infrastructure in `golazo-copilot/src/golazo_copilot`.
- Existing regression tests for server dispatch, workflow tools, and contract/error handling.
- Developer documentation surfaces for concise internal architecture notes.

## Migration / Rollout / Rollback Plan
### Migration
- No user-facing migration required.
- Internal code organization migration only; runtime tool contracts remain stable.

### Rollout
1. Land refactor in incremental slices (utilities → handlers → registration wiring → server orchestration reduction).
2. Run targeted regression suite after each slice.
3. Run full relevant server/workflow regression suite before merge.
4. Publish concise internal notes on new extension points.

### Rollback
1. Revert to prior `server.py` dispatch wiring if any contract regression is detected.
2. Use git-level rollback per slice to minimize downtime and isolate faulty extraction step.
3. Maintain deterministic error behavior priority during rollback verification.

## Observability Plan
- Compare pre/post refactor test pass/fail profiles for dispatch and workflow suites.
- Add lightweight operational logging at dispatch boundaries (tool selected, outcome category) without changing response contracts.
- Track error category rates for invalid/missing parameters to detect drift.
- On-call playbook focus:
  - tool-not-found/registration mismatch incidents
  - spikes in parameter-validation failures after rollout
  - rollback trigger: any contract regression or elevated dispatch failure rate

## Test Strategy Summary
1. Contract parity tests for tool names and required parameters.
2. Success-path regression checks on representative existing tools.
3. Failure-path regression checks for invalid/missing parameters and deterministic error messages.
4. Dispatch/registration integration tests verifying routing reaches intended handlers.
5. Broad regression run for server + workflow tool suites with no expectation changes for API behavior.
6. Optional micro-benchmark/smoke timing check to guard against measurable latency regression.

## Assumptions Documented
- This work item is the maintainability follow-up identified in GCP-0060 closure notes.
- Existing MCP tool names and response shapes are strict backward-compatibility constraints.
- Validation is performed using existing automated tests in this repository, with targeted additions only for parity confidence.
