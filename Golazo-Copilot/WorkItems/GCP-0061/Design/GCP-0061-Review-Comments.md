# GCP-0061 Review Comments (Quality Assurance)

## Scope and Entry Checks
- User Story present: `WorkItems/GCP-0061/GCP-0061-User-Story.md`.
- Design Doc present: `WorkItems/GCP-0061/Design/GCP-0061-design-doc.md`.
- QA assumption: file-name casing difference from role template (`Design-Doc` vs `design-doc`) is non-functional and accepted.

## QA Decision
- **Status**: Conditionally Approved for implementation.
- **Rationale**: Design is feasible and aligned to behavior-preserving refactor goals, with manageable risk if parity and latency gates are enforced.

## Findings

### 1) Registration parity must be an explicit release gate (**Major**)
- **Issue**: Design references parity but does not define blocking criteria for missing/renamed registrations.
- **Risk**: Runtime tool lookup failures and silent contract drift.
- **Recommendation**: Add a required check that compares pre/post registered tool-name set and required-parameter definitions; any delta blocks merge.
- **Verification**: Integration test asserting exact set equality and required-parameter parity.

### 2) Error determinism needs explicit category-level assertions (**Major**)
- **Issue**: Design says deterministic messaging intent is preserved but lacks category parity guardrails.
- **Risk**: Changed validation order or exception mapping alters expected error behavior.
- **Recommendation**: Standardize error outcome categories (`validation_error`, `handler_error`, `tool_not_found`) and assert parity for representative invalid/missing parameter cases.
- **Verification**: Parameterized failure-path tests asserting stable category and message-intent tokens.

### 3) “Materially reduced responsibility” is qualitative and can drift (**Minor**)
- **Issue**: AC1 includes qualitative language without implementation review signal.
- **Risk**: Refactor accepted without meaningful decomposition.
- **Recommendation**: Use a review checklist requiring `server.py` to remain orchestration-only (bootstrap/wiring/delegation) with no direct business handling logic.
- **Verification**: Code review checklist + architecture note confirming boundaries.

### 4) Latency NFR requires measurable rollback trigger (**Major**)
- **Issue**: No concrete rollback threshold for “no measurable regression.”
- **Risk**: Performance degradation accepted due to undefined tolerance.
- **Recommendation**: Run baseline vs post-refactor timing smoke on representative tools; rollback on statistically consistent degradation beyond agreed team threshold.
- **Verification**: Repeatable smoke timing script output attached to PR.

### 5) Incremental sequencing is correct and should be enforced in PR slicing (**Minor**)
- **Issue**: Good sequencing exists but can be bypassed in one large PR.
- **Risk**: Reduced reviewability and rollback precision.
- **Recommendation**: Keep extraction slices aligned to design order (formatters -> handlers -> registration -> orchestration reduction).
- **Verification**: PR plan references slice boundaries and completion criteria.

## Acceptance Criteria Coverage Assessment
- **AC1 (modular boundaries + thinner `server.py`)**: Covered, with added review checklist recommendation.
- **AC2 (tool name/param/contract stability)**: Covered, requires explicit parity gate.
- **AC3 (regression suites pass unchanged expectations)**: Covered, ensure no expectation rewrites for API behavior.
- **AC4 (deterministic invalid/missing parameter behavior)**: Covered, requires error-category parity assertions.
- **AC5 (developer-facing extension documentation)**: Covered, maintainers’ note must identify where to register tools and where to implement handlers/formatters.

## Risks to Track During Implementation
- Validation-order drift causing changed error category/message intent.
- Registration map drift causing missing or renamed tools.
- Dispatch indirection overhead increasing normal-call latency.
- Oversized refactor slices obscuring behavior changes.

## QA Exit Criteria (Implementation Gate)
1. Pre/post parity evidence for registered tool names and required parameters is green.
2. Success/error contract-shape regression checks pass with unchanged expected API behavior.
3. Missing/invalid parameter tests show deterministic error-category/message-intent parity.
4. Relevant server/workflow suites pass without API-behavior expectation rewrites.
5. Developer-facing extension-point note is present and reviewed.
6. Latency smoke comparison shows no measurable regression per team threshold.

## Architect Notes

### Architectural Alignment and Boundaries
- **Decision**: Approve modular decomposition with strict behavior parity, keeping `server.py` as orchestration-only (bootstrap, wiring, delegation) after extraction.
- **Boundary contract**:
	- `dispatch/*`: route selection and dispatch table composition only.
	- `handlers/*`: tool-specific business handling only.
	- `formatters/*`: response/error envelope shaping only.
- **Blast-radius control**: preserve existing MCP tool names, parameter requirements, and response envelopes; disallow cross-cutting logic duplication between handlers and formatters.

### Contract and Failure-Handling Constraints (Required)
- **Registration parity gate**: merge is blocked on exact pre/post equality for registered tool-name set and required-parameter definitions.
- **Error determinism gate**: preserve stable outcome categories and message intent for `validation_error`, `handler_error`, and `tool_not_found`.
- **Dispatch contract**: route resolution must deterministically map each existing tool name to a single handler path with no fallback ambiguity.
- **Rollback safety**: extraction slices must remain revertible in isolation (formatters -> handlers -> registration -> orchestration reduction).

### Security, Privacy, and Operability Review
- **Data exposure**: no secrets/tokens/PII should be introduced in formatter outputs or dispatch logs; preserve least-information error payloads.
- **Auth boundary**: no new authentication/authorization surface is introduced; trust boundary remains existing MCP server entry path.
- **Dependency risk**: prefer zero new runtime dependencies for this refactor; if introduced, they require explicit vulnerability review and rationale.
- **On-call impact**: require observable failure categories at dispatch boundaries (registration mismatch, validation failure, handler exception) to support incident triage.

### Explicit Questions to Project Owner (Library/Default Behaviors)
1. For any newly extracted formatter helper, should default error verbosity remain minimal (current behavior intent) or include richer internal context for maintainers?
2. If extracted modules use default dict iteration/order semantics for registration assembly, is preserving exact registration ordering a required compatibility constraint?
3. For any file/path helper introduced during extraction, should default encoding/newline behavior be fixed explicitly (UTF-8, deterministic newlines) to avoid platform drift?

### Architect Disposition
- **Disposition**: Approved with constraints above; no architectural gate failure.
- **Scope change**: None proposed in this pass; no new user story required.
