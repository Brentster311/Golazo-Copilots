# Program Manager Notes: WIP-008 - AI Fork Detection and Blocking

**Work Item**: WIP-008  
**Role**: Program Manager  
**Date**: 2026-01-14

---

## Decisions Made

1. **Insert fork detection as Priority 3**: Placed between "block immediate win" and "take center" to ensure critical threats are handled first.

2. **Simulation-based detection**: Chose to simulate opponent moves to detect fork creation rather than pattern matching, as it's more generalizable.

3. **Single method addition**: Encapsulate all fork logic in `_find_fork_block()` to maintain separation of concerns.

---

## Alternatives Considered

1. **Pattern matching for known fork setups**: Rejected because it's brittle and doesn't generalize.

2. **Minimax algorithm**: Rejected as overkill for this specific issue.

3. **Hardcoded corner responses**: Rejected because it doesn't address the root cause.

---

## Tradeoffs Accepted

1. **Simplicity over completeness**: The fork detection approach is simpler than minimax but may not handle every edge case optimally.

2. **Defensive focus**: Prioritizing blocking opponent forks over creating AI forks, which matches the current defensive AI design.

---

## Known Limitations / Risks

1. If multiple fork cells exist, the algorithm returns the first one found. This is acceptable for a 3x3 board.

2. The AI doesn't proactively create its own forks - this is out of scope.

---

## Next Role

Ready for **Reviewer** to critique the design.
