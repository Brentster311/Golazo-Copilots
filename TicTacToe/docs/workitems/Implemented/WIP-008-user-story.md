# User Story: WIP-008 - AI Fork Detection and Blocking

**Status**: ? IMPLEMENTED

---

## User Story

- **Title**: AI Fork Detection and Blocking
- **As a**: Player competing against the AI in Tic-Tac-Toe
- **I want**: The AI to detect and block fork situations
- **So that**: The AI provides a challenging opponent that cannot be easily beaten with basic fork strategies

---

## Background

Analysis of `game_log.json` revealed that the AI lost a game due to failing to detect a fork setup:

```
Move 1: X plays (0,0) - top-left corner
Move 2: O plays (1,1) - center
Move 3: X plays (2,2) - bottom-right corner (diagonal fork setup!)
Move 4: O plays (0,2) - CRITICAL MISTAKE - should have blocked the fork
Move 5: X plays (2,0) - X now has two winning paths
Move 6: O plays (2,1) - blocks one path
Move 7: X plays (1,0) - X wins via column 0
```

The AI's current `_find_best_move()` method follows this priority:
1. Win if possible
2. Block opponent's immediate win
3. Take center
4. Take a corner
5. Take a side

**Missing**: Detection and prevention of fork setups (when opponent creates two winning threats simultaneously).

---

## Out of Scope

- Implementing full minimax algorithm (considered but rejected for simplicity)
- AI difficulty levels
- AI playing as X (first player)
- Changes to game logging

---

## Assumptions

- **Assumption (explicit)**: Fork detection should be added as Priority 2.5 (after blocking immediate wins, before taking center)
- **Assumption (explicit)**: The AI will continue playing as O (second player)
- **Assumption (explicit)**: Performance impact is negligible for a 3x3 board

---

## Acceptance Criteria

- [x] AI detects when opponent (X) is setting up a fork (two potential winning lines)
- [x] AI blocks fork setups by either:
  - Taking the cell that would complete the fork, OR
  - Creating a threat that forces the opponent to respond defensively
- [x] AI never loses to the classic "corner-center-opposite-corner" fork strategy
- [x] All existing tests continue to pass
- [x] New tests cover fork detection scenarios
- [x] Game log shows AI no longer loses to fork strategies

---

## Non-Functional Requirements

- No significant delay added to AI move calculation
- Code should be readable and maintainable
- Follow existing code patterns in `tictactoe.py`

---

## Telemetry / Metrics Expected

- Game log (`game_log.json`) will show improved AI win/draw rate
- No AI losses to fork strategies after implementation

---

## Rollout / Rollback Notes

- **Rollout**: Replace `_find_best_move()` logic with fork-aware version
- **Rollback**: Revert to previous `_find_best_move()` implementation if issues arise
- No database migrations or external dependencies involved

---

## Implementation Summary

### Code Changes
- Added `_find_fork_block(player)` method to detect fork setups
- Added `_count_winning_threats(player)` helper method
- Modified `_find_best_move()` to include fork blocking as Priority 3

### Test Changes
- Added 13 new tests for fork detection (TC-401 through TC-409 + helper tests)
- All 59 tests pass
