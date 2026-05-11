# AGL-001 Test Cases

## Traceability Matrix
- AC1 -> TC-001, TC-002
- AC2 -> TC-003, TC-004
- AC3 -> TC-005
- AC4 -> TC-006
- AC5 -> TC-007, TC-008

## Test Cases

### TC-001: AgentLoop public API exposure
- Acceptance Criteria: AC1
- Type: Unit
- Precondition: Package import path configured for tests.
- Steps:
  - Import AgentLoop from package root.
  - Instantiate using deterministic stage callables and in-memory store.
- Expected Outcome:
  - Import succeeds.
  - Instance exposes run(max_steps: int).
- Failure Message:
  - "AgentLoop public API is not importable or missing run(max_steps)."

### TC-002: Typed interface contract smoke check
- Acceptance Criteria: AC1
- Type: Unit
- Precondition: Type hints present in exported interfaces.
- Steps:
  - Inspect AgentLoop and key model signatures for annotations.
- Expected Outcome:
  - Required constructor and run method annotations are present.
- Failure Message:
  - "Public interfaces are missing required type hints."

### TC-003: Successful termination path
- Acceptance Criteria: AC2
- Type: Unit
- Precondition: Evaluator returns success at a known step.
- Steps:
  - Execute run(max_steps=10) using deterministic stage callables.
- Expected Outcome:
  - Loop terminates before max_steps.
  - Termination reason is success.
- Failure Message:
  - "Loop did not terminate on success signal."

### TC-004: Max-step termination path
- Acceptance Criteria: AC2
- Type: Unit
- Precondition: Evaluator never returns success.
- Steps:
  - Execute run(max_steps=3).
- Expected Outcome:
  - Loop runs exactly 3 iterations.
  - Termination reason is max_steps.
- Failure Message:
  - "Loop did not terminate at max_steps boundary."

### TC-005: Default in-memory store and abstraction behavior
- Acceptance Criteria: AC3
- Type: Unit
- Precondition: No custom store provided.
- Steps:
  - Instantiate AgentLoop with default constructor path.
  - Validate store type compatibility with state store abstraction.
- Expected Outcome:
  - InMemoryStateStore is used by default.
  - Store operations complete through abstraction contract.
- Failure Message:
  - "Default state store is not in-memory or violates store abstraction."

### TC-006: Step result structure integrity
- Acceptance Criteria: AC4
- Type: Unit
- Precondition: Deterministic stage functions produce known action/outcome values.
- Steps:
  - Execute run(max_steps=4).
  - Inspect each recorded step result.
- Expected Outcome:
  - Each step contains index, action summary, outcome, and termination signal fields.
  - Step indexes are contiguous and monotonic from 1..n.
- Failure Message:
  - "Step result records are incomplete or malformed."

### TC-007: Happy-path test suite gate
- Acceptance Criteria: AC5
- Type: Verification
- Precondition: Unit tests implemented.
- Steps:
  - Run pytest for loop tests.
- Expected Outcome:
  - Success-path loop test passes.
- Failure Message:
  - "Successful termination test is missing or failing."

### TC-008: Max-step suite gate
- Acceptance Criteria: AC5
- Type: Verification
- Precondition: Unit tests implemented.
- Steps:
  - Run pytest for loop tests.
- Expected Outcome:
  - Max-step termination test passes.
- Failure Message:
  - "Max-step termination test is missing or failing."

## Additional Quality Checks
- Determinism check: same seed state + same stage callables yields identical step records.
- Performance sensitivity check: runtime should remain stable for small max_steps in local execution.
