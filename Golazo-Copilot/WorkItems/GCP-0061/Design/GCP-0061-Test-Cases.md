# GCP-0061 Test Cases (Quality Assurance)

## Test Strategy
- Objective: Prove behavior-preserving modular refactor of MCP registration/dispatch with deterministic error handling and no measurable latency regression.
- Principle: TDD-first parity checks are defined before production refactor merges.
- Scope: Existing tools only; no new MCP tool behavior or contract changes.

## Assumptions
- Baseline behavior is captured from current `main` implementation before refactor.
- Existing automated suites remain the primary regression evidence.
- Error parity means same outcome category and stable message intent for equivalent invalid inputs.

## Acceptance Criteria to Test Mapping
- AC1 -> TC-AC1-001, TC-AC1-002
- AC2 -> TC-AC2-001, TC-AC2-002, TC-AC2-003
- AC3 -> TC-AC3-001
- AC4 -> TC-AC4-001, TC-AC4-002, TC-AC4-003
- AC5 -> TC-AC5-001
- NFR latency -> TC-NFR-001

## Test Cases

### AC1 — Modular boundaries and reduced `server.py` responsibility

#### TC-AC1-001: Server orchestration-only boundary check
- Type: Static architecture/test review check
- Precondition: Refactor branch contains extracted dispatch/handler/formatter modules.
- Steps:
  1. Inspect `server.py` responsibilities.
  2. Confirm it performs startup/wiring/delegation only.
  3. Confirm routing/handler logic resides outside `server.py`.
- Expected Outcome:
  - `server.py` is orchestration-only and delegates to modular components.
- Explicit Failure Message:
  - "AC1 boundary failure: `server.py` still contains direct dispatch/handler business logic."

#### TC-AC1-002: Dispatch path ownership verification
- Type: Unit/integration architecture test
- Precondition: Dispatch table/composition module exists.
- Steps:
  1. Invoke representative MCP calls through server entrypoint.
  2. Assert dispatch resolves through dedicated routing module.
- Expected Outcome:
  - Requests route through external dispatch components, not inline branching in `server.py`.
- Explicit Failure Message:
  - "AC1 ownership failure: dispatch path does not traverse modular routing components."

### AC2 — Contract parity for tool names, parameters, and success/error shapes

#### TC-AC2-001: Registered tool-name set parity
- Type: Integration parity test
- Precondition: Baseline registered tool-name set captured pre-refactor.
- Steps:
  1. Enumerate registered tool names in baseline and refactor branch.
  2. Compare as exact set equality.
- Expected Outcome:
  - No missing, additional, or renamed tool names.
- Explicit Failure Message:
  - "AC2 contract failure: registered tool-name set changed (missing/additional/renamed tool detected)."

#### TC-AC2-002: Required-parameter parity
- Type: Integration parity test
- Precondition: Baseline required-parameter metadata captured for representative tools.
- Steps:
  1. Query required parameters for each selected tool before and after refactor.
  2. Compare required-parameter lists/semantics.
- Expected Outcome:
  - Required parameters and validation semantics remain unchanged.
- Explicit Failure Message:
  - "AC2 contract failure: required-parameter semantics changed for tool <tool_name>."

#### TC-AC2-003: Success/error response-shape parity
- Type: Integration contract test
- Precondition: Baseline success and error payload shape snapshots for representative tools.
- Steps:
  1. Execute representative success-path calls.
  2. Execute representative controlled error-path calls.
  3. Compare response top-level shape and required fields.
- Expected Outcome:
  - Success and error response contracts are shape-equivalent to baseline.
- Explicit Failure Message:
  - "AC2 contract failure: response shape drift detected for tool <tool_name>/<scenario>."

### AC3 — Regression suite parity with unchanged API behavior expectations

#### TC-AC3-001: Relevant suite pass without API expectation rewrites
- Type: Regression suite gate
- Precondition: Relevant server/workflow/tool suites identified.
- Steps:
  1. Run targeted server/workflow regression tests after refactor.
  2. Verify pass results without changing API behavior expectations.
- Expected Outcome:
  - All relevant tests pass with no expectation updates tied to API behavior drift.
- Explicit Failure Message:
  - "AC3 regression failure: suite requires API expectation changes or has failing behavior-parity tests."

### AC4 — Deterministic handling for invalid/missing parameters

#### TC-AC4-001: Missing required parameter deterministic parity
- Type: Negative integration test
- Precondition: Baseline missing-parameter outcomes recorded for representative tools.
- Steps:
  1. Submit requests missing required parameters.
  2. Compare category and message intent to baseline.
- Expected Outcome:
  - Error category and message intent remain deterministic and parity-aligned.
- Explicit Failure Message:
  - "AC4 determinism failure: missing-parameter handling changed category or message intent for <tool_name>."

#### TC-AC4-002: Invalid parameter type/value deterministic parity
- Type: Negative integration test
- Precondition: Baseline invalid-parameter outcomes recorded.
- Steps:
  1. Submit invalid type/value inputs for representative tools.
  2. Compare category and message intent to baseline.
- Expected Outcome:
  - Deterministic invalid-input behavior remains parity-aligned.
- Explicit Failure Message:
  - "AC4 determinism failure: invalid-parameter handling changed category or message intent for <tool_name>."

#### TC-AC4-003: Tool-not-found deterministic behavior
- Type: Negative dispatch test
- Precondition: Baseline tool-not-found behavior recorded.
- Steps:
  1. Invoke a non-existent tool identifier.
  2. Compare category/message intent to baseline.
- Expected Outcome:
  - Tool-not-found behavior remains deterministic and contract-consistent.
- Explicit Failure Message:
  - "AC4 determinism failure: tool-not-found behavior differs from baseline contract intent."

### AC5 — Developer-facing documentation for extension points

#### TC-AC5-001: Maintainer notes completeness check
- Type: Documentation verification
- Precondition: Developer-facing note exists in work item outputs or repository docs.
- Steps:
  1. Confirm note identifies where to register tools.
  2. Confirm note identifies where to implement handlers and formatters.
  3. Confirm note describes minimal extension flow.
- Expected Outcome:
  - Maintainers can identify extension points without guessing.
- Explicit Failure Message:
  - "AC5 documentation failure: extension-point guidance is missing or incomplete."

### Non-Functional — Latency

#### TC-NFR-001: Dispatch latency smoke parity
- Type: Performance smoke
- Precondition: Representative tool call set and stable test environment.
- Steps:
  1. Capture baseline median/percentile timings for representative calls.
  2. Re-run same set post-refactor with same environment.
  3. Compare deltas and evaluate against team-agreed threshold.
- Expected Outcome:
  - No measurable regression beyond threshold.
- Explicit Failure Message:
  - "NFR latency failure: post-refactor dispatch latency regression exceeds agreed threshold."

## Test Data and Execution Notes
- Use representative tools across workflow/state/validation-sensitive paths.
- Keep baseline artifacts versioned with the test run context.
- Prefer deterministic fixtures over live/external dependencies.

## Exit Evidence Checklist
- Tool-name parity evidence attached.
- Required-parameter parity evidence attached.
- Success/error shape parity evidence attached.
- Deterministic invalid/missing-parameter parity evidence attached.
- Regression suite results attached.
- Latency smoke comparison attached.
- Developer extension-point documentation verified.
