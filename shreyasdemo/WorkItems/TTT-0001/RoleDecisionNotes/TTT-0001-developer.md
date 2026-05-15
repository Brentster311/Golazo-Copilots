# TTT-0001 Developer Decision Notes

## Summary
Implemented MVP Windows-local Tic-Tac-Toe using Python stdlib (`tkinter`) with separated game logic (`game_state.py`) and GUI entry (`app.py`), plus automated game-logic tests.

## Assumptions Made
- Repository currently has no prior Python app code, so new minimal files were created at workspace root.
- QA "optional in-session counters" were implemented because they are explicitly expected in story telemetry notes and remain in-memory only.
- UI feedback for invalid/locked clicks is silent no-op (allowed by QA comments), with state invariants enforced.

## TDD Evidence
1. Created test suite first in `tests/test_game_state.py`.
2. Executed red-phase command:
   - `python -m unittest discover -s tests -p "test_*.py"`
   - Result: failed with `ModuleNotFoundError: No module named 'game_state'`.
3. Implemented production logic in `game_state.py`.
4. Executed green-phase command:
   - `python -m unittest discover -s tests -p "test_*.py"`
   - Result: 10 tests passed.

## Implementation Decisions
- Used dataclasses for `GameState` and `SessionStats` to keep state explicit and minimal.
- Added pure functions `check_winner(board)` and `is_draw(board)` for deterministic unit testing.
- `GameState.apply_move(index, stats=None)` handles all move rules:
  - ignores invalid index, occupied cell, and locked state,
  - applies move,
  - checks winner before draw,
  - updates terminal status/lock and counters,
  - toggles turn when non-terminal.
- `restart_game()` resets board + turn + status + lock, preserving in-session counters.
- GUI in `app.py` includes:
  - 3x3 clickable board,
  - turn/winner/draw status label,
  - restart button,
  - in-session counters row,
  - callback boundary exception handling via concise error dialog.

## Acceptance Criteria Coverage
- AC1: Launch UI includes 3x3 board + initial `Turn: X` indicator.
- AC2: Empty click places mark; occupied clicks are ignored.
- AC3: Winner/draw computed after each valid move and displayed.
- AC4: Board is functionally locked after terminal state (moves ignored until restart).
- AC5: Restart clears board, resets turn to X, and enables immediate replay.

## Verification Commands Run
- `python -m unittest discover -s tests -p "test_*.py"` (pass)

## Files Created
- `game_state.py`
- `app.py`
- `tests/test_game_state.py`
- `README.md`
- `WorkItems/TTT-0001/RoleDecisionNotes/TTT-0001-developer.md`