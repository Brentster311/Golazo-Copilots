# Developer Notes: WIP-008 - AI Fork Detection and Blocking

**Work Item**: WIP-008  
**Role**: Developer  
**Date**: 2026-01-14  
**Updated**: 2026-01-14 (Bugfix)

---

## Decisions Made

1. **Added `_find_fork_block(player)` method**: Detects fork setups using two strategies:
   - Simulation-based detection: For each empty cell, simulate opponent placing there and count threats
   - Special case detection: Opposite corners pattern with center taken

2. **Added `_count_winning_threats(player)` helper**: Counts lines where player has 2 marks and 1 empty (imminent winning positions).

3. **Integrated into priority chain**: Fork blocking is now Priority 3, after win and block checks.

---

## Implementation Details

### Bugfix (2026-01-14)

**Original bug**: The initial implementation only detected forks when placing a mark would *immediately* create 2+ threats. However, the classic diagonal fork setup (X at opposite corners with O at center) doesn't create immediate threats - it creates a *setup* for a fork on the next move.

**Fix**: Added special case detection for the "opposite corners" pattern:
- If opponent has corners (0,0) and (2,2) OR (0,2) and (2,0)
- And AI has the center
- And the diagonal isn't already blocked
- Then AI takes an edge to create a threat, forcing opponent to respond defensively

### New Methods

```python
def _find_fork_block(self, player):
    """Finds cells where opponent could create a fork, plus special case patterns."""
    
def _count_winning_threats(self, player):
    """Counts lines with 2 player marks and 1 empty."""
```

### Modified Methods

- `_find_best_move()`: Added Priority 3 fork blocking call

### Files Changed

- `TicTacToe/tictactoe.py`: Added 2 methods, modified 1 method
- `TicTacToe/test_tictactoe.py`: Added 12 new tests, updated 2 test expectations

---

## Alternatives Considered

None - followed the approved design with bugfix enhancement.

---

## Tradeoffs Accepted

1. Linear scan of all empty cells (O(9)) is acceptable for 3x3 board.
2. Special case pattern matching for opposite corners is explicit rather than general, but handles the most common fork strategy.

---

## Known Limitations / Risks

1. The special case only handles the opposite corners pattern explicitly. Other fork patterns rely on the simulation-based detection.

---

## Test Results

All 59 tests pass:
- 16 original game logic tests
- 19 AI strategy tests  
- 10 game logging tests
- 2 direct winner check tests
- **12 fork detection tests** (includes updated expectations)

---

## Next Role

Ready for **Builder** to verify build and deployment.
