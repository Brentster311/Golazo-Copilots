# TTT-0001 QA Test Cases (TDD-First, MVP)

## Test Strategy
- Define and review these tests before production implementation (TDD-first).
- Prioritize deterministic unit tests for game logic, then add lightweight UI integration checks.
- Keep assertions scoped to MVP only; do not test out-of-scope features.

## Traceability Matrix
| Acceptance Criterion | Covered Test IDs |
|---|---|
| AC1: Launch shows 3x3 board + turn indicator (X starts) | TC-AC1-001, TC-NFR-001 |
| AC2: Empty click places mark, occupied cannot be overwritten | TC-AC2-001, TC-AC2-002, TC-ERR-001 |
| AC3: Winner/draw detected and displayed | TC-AC3-001, TC-AC3-002, TC-AC3-003 |
| AC4: After terminal state, additional moves blocked until Restart | TC-AC4-001, TC-AC4-002 |
| AC5: Restart clears board, resets turn to X, enables immediate replay | TC-AC5-001, TC-AC5-002 |

---

## Functional Acceptance Tests

### TC-AC1-001 — App launch baseline UI state
- **Type**: Integration/UI
- **Priority**: P0
- **Covers**: AC1
- **Preconditions**: App not running.
- **Steps**:
  1. Launch app on Windows.
  2. Observe main game window.
- **Expected Outcome**:
  - A visible 3x3 board (9 interactive cells).
  - Status indicator is visible and indicates X turn at startup.
  - No error dialogs on startup.
- **Failure Message**:
  - `AC1_FAIL_LAUNCH_UI_STATE: Expected 3x3 board and initial turn indicator 'X', but baseline UI state was incomplete or incorrect.`

### TC-AC2-001 — Valid move places mark and toggles turn
- **Type**: Integration/UI
- **Priority**: P0
- **Covers**: AC2
- **Preconditions**: Fresh game state.
- **Steps**:
  1. Click an empty cell.
  2. Observe cell value and status text.
  3. Click a second different empty cell.
- **Expected Outcome**:
  - First clicked cell displays `X`.
  - Turn indicator switches to `O` after first move.
  - Second clicked cell displays `O`.
  - Turn indicator switches back to `X` after second move.
- **Failure Message**:
  - `AC2_FAIL_VALID_MOVE_OR_TURN: Expected valid placement and turn alternation X->O->X, but observed incorrect mark and/or turn state.`

### TC-AC2-002 — Occupied cell cannot be overwritten
- **Type**: Unit + Integration
- **Priority**: P0
- **Covers**: AC2
- **Preconditions**: One cell already occupied by `X`.
- **Steps**:
  1. Attempt to click/select the same occupied cell again.
- **Expected Outcome**:
  - Cell value remains `X` (unchanged).
  - Turn does not advance due to invalid overwrite attempt.
  - Game status remains otherwise unchanged.
- **Failure Message**:
  - `AC2_FAIL_OVERWRITE_ALLOWED: Occupied cell was modified or turn advanced on invalid overwrite attempt.`

### TC-AC3-001 — Winner detection for X and status display
- **Type**: Integration/UI
- **Priority**: P0
- **Covers**: AC3
- **Preconditions**: Fresh game.
- **Steps**:
  1. Play moves to produce X win on top row: X(0), O(3), X(1), O(4), X(2).
- **Expected Outcome**:
  - Game enters terminal win state for X.
  - Status message indicates X is winner.
- **Failure Message**:
  - `AC3_FAIL_WINNER_DETECTION_X: Expected winner X after winning sequence, but winner status/message was incorrect or missing.`

### TC-AC3-002 — Winner detection across all 8 lines (engine)
- **Type**: Unit
- **Priority**: P1
- **Covers**: AC3
- **Preconditions**: Test harness for `check_winner(board)`.
- **Steps**:
  1. Evaluate boards representing each winning line (3 rows, 3 columns, 2 diagonals) for both players.
- **Expected Outcome**:
  - `check_winner` returns correct winner symbol for every winning pattern.
- **Failure Message**:
  - `AC3_FAIL_WIN_PATTERN_MISS: check_winner failed to identify one or more valid winning line patterns.`

### TC-AC3-003 — Draw detection and status display
- **Type**: Unit + Integration
- **Priority**: P0
- **Covers**: AC3
- **Preconditions**: Board reaches full non-winning state.
- **Steps**:
  1. Execute a known draw move sequence without creating a winner.
- **Expected Outcome**:
  - Game status is draw.
  - UI status message indicates draw.
- **Failure Message**:
  - `AC3_FAIL_DRAW_DETECTION: Expected draw on full non-winning board, but draw status/message was not produced.`

### TC-AC4-001 — Board lock after win
- **Type**: Integration/UI
- **Priority**: P0
- **Covers**: AC4
- **Preconditions**: Game already in win terminal state.
- **Steps**:
  1. Attempt additional clicks on empty and occupied cells after win.
- **Expected Outcome**:
  - No additional marks are placed.
  - Board state remains unchanged.
  - Status remains terminal winner message.
- **Failure Message**:
  - `AC4_FAIL_POST_WIN_MOVE_ALLOWED: Move was accepted after win when board should be locked.`

### TC-AC4-002 — Board lock after draw
- **Type**: Integration/UI
- **Priority**: P0
- **Covers**: AC4
- **Preconditions**: Game already in draw terminal state.
- **Steps**:
  1. Attempt additional click on any board cell after draw.
- **Expected Outcome**:
  - Board state unchanged.
  - Status remains draw.
- **Failure Message**:
  - `AC4_FAIL_POST_DRAW_MOVE_ALLOWED: Move was accepted after draw when board should be locked.`

### TC-AC5-001 — Restart resets game state and enables replay
- **Type**: Integration/UI
- **Priority**: P0
- **Covers**: AC5
- **Preconditions**: Current game has non-empty board (preferably terminal).
- **Steps**:
  1. Click `Restart`.
  2. Observe board and status.
  3. Click an empty cell.
- **Expected Outcome**:
  - All 9 cells clear immediately.
  - Turn resets to X.
  - Game unlocked and accepts new move.
  - First new move after restart places `X`.
- **Failure Message**:
  - `AC5_FAIL_RESTART_STATE_RESET: Restart did not clear board/reset turn/unlock game for immediate replay.`

### TC-AC5-002 — Restart preserves in-session counters
- **Type**: Unit + Integration
- **Priority**: P1
- **Covers**: AC5 + Telemetry assumption
- **Preconditions**: At least one completed game recorded in session.
- **Steps**:
  1. Record current counter values.
  2. Click `Restart`.
- **Expected Outcome**:
  - Game board and round state reset.
  - In-session counters remain unchanged by restart operation.
- **Failure Message**:
  - `AC5_FAIL_COUNTER_RESET_ON_RESTART: Restart incorrectly altered in-session counters that should persist during app session.`

---

## Negative / Error / Reliability / Security / Performance-Sensitive Tests

### TC-ERR-001 — Invalid index callback is safely ignored
- **Type**: Unit
- **Priority**: P1
- **Related To**: Error handling reliability
- **Preconditions**: Engine method callable with index input.
- **Steps**:
  1. Invoke move handler with invalid indices (e.g., `-1`, `9`, non-int if applicable).
- **Expected Outcome**:
  - No unhandled exception.
  - Board/current player/status unchanged.
- **Failure Message**:
  - `ERR_FAIL_INVALID_INDEX_CRASH: Invalid index input caused exception or state mutation.`

### TC-REL-001 — Repeated restart reliability
- **Type**: Integration/UI
- **Priority**: P2
- **Related To**: Reliability
- **Preconditions**: App running.
- **Steps**:
  1. Perform 50 restart cycles with intermittent valid moves.
- **Expected Outcome**:
  - App remains responsive and stable.
  - No corrupted board states after any cycle.
- **Failure Message**:
  - `REL_FAIL_RESTART_SOAK: App became unstable or state-corrupted during repeated restart cycles.`

### TC-SEC-001 — Local-only/network independence check
- **Type**: Integration/Environment
- **Priority**: P2
- **Related To**: Security/attack-surface minimization + NFR
- **Preconditions**: Disconnect network or block outbound access.
- **Steps**:
  1. Launch app and play one full round.
- **Expected Outcome**:
  - App launches and functions normally with no network dependency.
  - No user-visible failure related to connectivity.
- **Failure Message**:
  - `SEC_FAIL_NETWORK_DEPENDENCY: App required network connectivity for core local gameplay.`

### TC-PERF-001 — Startup and first-interaction responsiveness
- **Type**: Integration/Performance smoke
- **Priority**: P2
- **Related To**: Performance-sensitive UX
- **Preconditions**: Typical local Windows machine.
- **Steps**:
  1. Start app and measure time to interactable UI.
  2. Perform first click on empty cell and observe update latency.
- **Expected Outcome**:
  - App is interactable within practical local threshold (target <= 2s).
  - Mark appears and status updates without noticeable lag (target <= 200ms under normal load).
- **Failure Message**:
  - `PERF_FAIL_INTERACTION_LATENCY: Startup or first interaction exceeded responsiveness threshold.`

---

## Execution Order (Recommended)
1. Run unit tests for `GameState`, `check_winner`, `is_draw`.
2. Run AC integration tests (TC-AC1/2/3/4/5).
3. Run error/reliability/performance smoke tests.

## Exit Criteria
- All P0 tests pass.
- No P1 failures without documented triage and approved deferral.
- Any P2 failure is triaged with risk note before release decision.
