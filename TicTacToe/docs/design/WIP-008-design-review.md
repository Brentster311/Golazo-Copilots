# Design Review: WIP-008 - AI Fork Detection and Blocking

**Work Item**: WIP-008  
**Author**: Program Manager  
**Date**: 2026-01-14

---

## Summary

Add fork detection and blocking capability to the Tic-Tac-Toe AI to prevent losses when the opponent sets up two simultaneous winning threats.

---

## Problem Statement

The AI currently loses to a basic fork strategy where the opponent (X) occupies two opposite corners, creating two potential winning lines. The AI fails to recognize this pattern and block it, resulting in an unwinnable position.

**Observed Failure**: In `game_log.json`, X played corners (0,0) and (2,2), the AI blocked incorrectly at (0,2), and X completed a fork at (2,0) that the AI could not defend.

---

## Business Case

### Why Now
- User testing revealed AI weakness via game logs
- Fork strategy is a well-known Tic-Tac-Toe tactic that any competent AI should handle
- Fixing this improves user satisfaction with single-player mode

### Impact
- AI will no longer lose to basic strategies
- Improved perceived game quality

### KPIs
- Zero AI losses to fork strategies in game logs
- Maintain or improve AI win/draw rate

---

## Stakeholders

| Role | Interest |
|------|----------|
| Players | Want challenging AI opponent |
| Developers | Want maintainable code |

---

## Functional Requirements

1. **FR-1**: AI must detect when opponent has potential to create a fork
2. **FR-2**: AI must block fork setups before they become unblockable
3. **FR-3**: Fork blocking must be prioritized after immediate win/block detection

---

## Non-Functional Requirements

1. **NFR-1**: No perceptible delay in AI move calculation
2. **NFR-2**: Code follows existing patterns in `tictactoe.py`
3. **NFR-3**: All existing tests must pass

---

## Proposed Approach

### Algorithm

Add a new method `_find_fork_block()` and insert it into the priority chain in `_find_best_move()`:

```
Current Priority:
1. Win if possible
2. Block opponent's win
3. Take center
4. Take corner
5. Take side

New Priority:
1. Win if possible
2. Block opponent's win
3. **Block opponent's fork** ? NEW
4. Take center
5. Take corner
6. Take side
```

### Fork Detection Logic

A fork exists when a player has two or more lines with exactly one of their marks and two empty cells. The intersection point of these lines is the fork cell.

**Detection Algorithm**:
1. For each empty cell, simulate placing opponent's mark
2. Count how many winning lines would be created (lines with 2 opponent marks + 1 empty)
3. If count >= 2, this cell creates a fork
4. AI should take this cell to block the fork

### Code Changes

File: `TicTacToe/tictactoe.py`

1. Add `_find_fork_block(self, player)` method
2. Modify `_find_best_move()` to call fork blocking after win/block checks

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Full Minimax | Optimal play | Complex, overkill | Rejected |
| Opening Book | Fast | Brittle, incomplete | Rejected |
| Fork Detection | Targeted, maintainable | May miss edge cases | **Selected** |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Logic error in fork detection | Medium | High | Comprehensive test cases |
| Performance regression | Low | Low | Simple O(9) algorithm |
| Edge cases not covered | Low | Medium | Test multiple fork scenarios |

---

## Open Questions

None - the approach is straightforward.

---

## Dependencies

- None - uses existing codebase patterns

---

## Migration / Rollout / Rollback Plan

- **Rollout**: Direct code change, no migration needed
- **Rollback**: Git revert if issues arise

---

## Observability Plan

- Game logs (`game_log.json`) will show AI performance
- Test coverage ensures correctness

---

## Test Strategy Summary

- Add unit tests for `_find_fork_block()` method
- Add integration tests for AI behavior against fork strategies
- Verify all existing tests pass
