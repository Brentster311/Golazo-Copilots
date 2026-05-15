# AGL-001 Design Doc

## Summary
Implement a basic, reusable Agent Loop Python package that executes a deterministic plan -> execute -> evaluate cycle, supports pluggable state storage via an interface, and ships with an in-memory default implementation.

## Problem Statement
The repository lacks a foundational agent control-flow package. Without a standard loop abstraction, future agent features risk fragmented implementations and repeated redesign.

## Business Case
- Why now: Establishing the loop baseline reduces future integration friction for agent-oriented features.
- Expected impact: Faster iteration on higher-level agent capabilities and lower maintenance overhead.
- KPIs:
  - Build success with passing unit tests in CI/local run
  - Core module test coverage at or above 70%
  - Time to integrate first downstream use case reduced versus ad-hoc loop implementation

## Stakeholders
- Primary: Developers implementing agent behavior
- Secondary: Maintainers responsible for quality and future extensibility

## Functional Requirements
- Expose an AgentLoop class with run(max_steps) as the primary API.
- Execute deterministic iteration stages: plan, execute, evaluate.
- Support termination on success signal or max step limit.
- Record structured step results for each iteration.
- Use a state store abstraction with an in-memory implementation.

## Non-Functional Requirements
- Cross-platform Python compatibility (Windows/Mac/Linux).
- Deterministic behavior for identical input state and stage functions.
- Type hints and concise package documentation.
- Minimal dependency footprint (standard library where possible).

## Proposed Approach
- Package structure:
  - agent_loop/core.py: AgentLoop orchestration
  - agent_loop/models.py: dataclasses/protocols for state and step result
  - agent_loop/store.py: StateStore abstraction and InMemoryStateStore
  - tests/: unit tests for success and max-step termination paths
- API approach:
  - Inject stage callables (planner/executor/evaluator) into AgentLoop.
  - Keep state serialization concerns out of scope for this slice.

## Alternatives Considered
- Function-only loop utilities: rejected due to weaker encapsulation and lower extensibility.
- Coupling to persistence implementation directly: rejected to preserve future adaptability.

## Risks, Mitigations, Open Questions
- Risk: Over-design for v1.
  - Mitigation: Keep interfaces minimal and implement only required behavior.
- Risk: Ambiguous stage contract semantics.
  - Mitigation: Define typed call signatures and deterministic test fixtures.
- Open question: Should future versions include async stage support?
  - Decision: defer to a future work item.

## Dependencies
- Python 3.11+
- Testing framework: pytest

## Migration / Rollout / Rollback Plan
- Migration: Introduce new package modules and tests incrementally.
- Rollout: Validate via unit test run and basic import smoke check.
- Rollback: Remove package modules and tests with no external data migration needed.

## Observability Plan
- Expose loop execution metadata:
  - total_steps
  - termination_reason
  - runtime_ms
- Keep telemetry local to return values/logging hooks (no remote sink in this slice).

## Test Strategy Summary
- Unit tests for:
  - Successful termination path
  - Max-step termination path
  - Step result recording integrity
  - In-memory store read/write behavior
- Verify deterministic outcomes with controlled stage functions.
