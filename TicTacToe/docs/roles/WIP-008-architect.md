# Architect Notes: WIP-008 - AI Fork Detection and Blocking

**Work Item**: WIP-008  
**Role**: Architect  
**Date**: 2026-01-14

---

## Decisions Made

1. **Approved integration point**: Fork detection will be added as a private method `_find_fork_block()` following existing patterns.

2. **No structural changes needed**: The change fits cleanly into the existing `_find_best_move()` priority chain.

3. **Method signature**: `_find_fork_block(self, player: str) -> tuple[int, int] | None` - consistent with `_find_winning_move()`.

---

## Alternatives Considered

1. **Separate AI strategy class**: Rejected - would be over-engineering for this scope.
2. **Configuration-based priority**: Rejected - not needed for current requirements.

---

## Tradeoffs Accepted

1. Keeping AI logic in the main `TicTacToe` class rather than extracting to separate module. This maintains simplicity but may need refactoring if AI grows more complex.

---

## Known Limitations / Risks

1. The monolithic `TicTacToe` class continues to grow. Future work may benefit from extracting AI logic to a separate class.

---

## Architectural Guidance for Implementation

### Method Placement
Add `_find_fork_block()` after `_find_winning_move()` method to maintain logical grouping.

### Integration Point
```python
def _find_best_move(self):
    # Priority 1: Win
    winning_move = self._find_winning_move("O")
    if winning_move:
        return winning_move

    # Priority 2: Block
    blocking_move = self._find_winning_move("X")
    if blocking_move:
        return blocking_move

    # Priority 3: Block fork ? INSERT HERE
    fork_block = self._find_fork_block("X")
    if fork_block:
        return fork_block

    # ... rest unchanged
```

---

## Next Role

Ready for **Tester** to define test cases.
