# TTT-0001 QA Review Comments

## Review Outcome
- **Decision**: Conditionally approved for MVP implementation.
- **Reasoning**: The design is clear, feasible, and largely testable against all acceptance criteria; implementation can proceed if the clarifications below are treated as test-time expectations (not scope changes).

## Assumptions Applied
- Windows path and filename casing are treated as equivalent for this repository (`TTT-0001-design-doc.md` is accepted as the required design doc input).
- “Simple and readable UI” is validated through objective checks (visible status text, legible board labels, clear terminal-state messaging) rather than subjective visual scoring.
- Optional in-session counters are considered non-blocking for AC pass/fail, but if implemented they must remain in-memory only.

## What Is Strong
- Design maps directly to MVP scope and explicitly excludes non-MVP features (AI, network, persistence).
- Game state model is minimal and suitable for deterministic unit testing.
- Win/draw evaluation order is explicit and prevents draw-over-win mistakes.
- Restart behavior preserves session counters while resetting game state, matching user story assumptions.

## Risks and Actionable QA Comments

### 1) Occupied/locked click feedback is ambiguous
- **Observation**: UI behavior says occupied/locked clicks do nothing “(or brief non-blocking message)”.
- **Risk**: Inconsistent UX and inconsistent tests across implementations.
- **QA Recommendation (MVP-safe)**: Treat feedback message as optional; make state invariants mandatory:
  - board state unchanged,
  - current player unchanged,
  - status text remains correct for current game state.
- **Impact**: No scope change; only clarifies pass/fail criteria.

### 2) Invalid index handling needs explicit non-crash expectation
- **Observation**: Invalid callback index is listed in error handling.
- **Risk**: Hidden exceptions from UI callback mismatch can crash app.
- **QA Recommendation (MVP-safe)**: Add explicit acceptance-level test expectation that invalid indices are ignored and app remains responsive.
- **Impact**: Improves reliability validation without adding features.

### 3) Terminal state messaging format not fixed
- **Observation**: Winner/draw must be displayed, but exact text is not fixed.
- **Risk**: Fragile tests if string-matching is too strict.
- **QA Recommendation (MVP-safe)**: Validate semantic message classes (`Winner: X`, `Winner: O`, or `Draw`) with tolerant text matching policy.
- **Impact**: Stabilizes test suite; no product behavior change.

### 4) “Immediate” restart requires practical timing bound
- **Observation**: AC says restart enables new game immediately.
- **Risk**: Ambiguous interpretation can hide UI lag regressions.
- **QA Recommendation (MVP-safe)**: Use a practical UI assertion bound (e.g., refresh visible within 500 ms in local run) for integration tests.
- **Impact**: Adds measurable quality gate; does not change scope.

### 5) Performance/reliability expectations are implied but not explicit
- **Observation**: NFRs require interactable local app and clear messaging.
- **Risk**: Event-loop freezes or repeated restarts may regress responsiveness.
- **QA Recommendation (MVP-safe)**:
  - Add smoke performance checks for startup and click responsiveness.
  - Add reliability soak check for repeated restart cycles.
- **Impact**: Quality hardening within MVP boundaries.

## Testability Verdict by Acceptance Criterion
- **AC1 (launch board + X turn)**: Fully testable via UI smoke/integration.
- **AC2 (mark placement + no overwrite)**: Fully testable via unit + integration.
- **AC3 (winner/draw detection)**: Fully testable via deterministic rule tests + UI path checks.
- **AC4 (lock board after terminal)**: Fully testable via post-terminal click tests.
- **AC5 (restart reset and replay)**: Fully testable via restart state/reset tests.

## QA Gate Decision
- **Gate Status**: PASS WITH COMMENTS
- **Blocking issues**: None.
- **Follow-up required**: Implement test suite using the attached QA test cases and preserve MVP scope exactly.
