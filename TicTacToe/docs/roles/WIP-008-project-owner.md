# Project Owner Notes: WIP-008 - AI Fork Detection and Blocking

**Work Item**: WIP-008  
**Role**: Project Owner  
**Date**: 2026-01-14

---

## Decisions Made

1. **Scope limited to fork detection only**: Decided not to implement full minimax algorithm as it would be overkill for this specific problem and harder to understand/maintain.

2. **Fork blocking priority placement**: Fork detection will be inserted between "block immediate win" and "take center" in the AI priority list.

3. **Focus on defensive fork blocking**: The AI plays second (O), so the primary concern is blocking opponent forks rather than creating them.

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Full Minimax Algorithm | Optimal play, handles all scenarios | Complex, overkill for 3x3, harder to debug | Rejected |
| Minimax with Alpha-Beta Pruning | Optimal + efficient | Same complexity concerns | Rejected |
| Simple Fork Detection | Targeted fix, easy to understand, minimal code change | May not cover all edge cases | **Selected** |
| Hardcoded opening book | Fast, simple | Brittle, doesn't generalize | Rejected |

---

## Tradeoffs Accepted

1. **Simplicity over optimality**: The fork detection approach may not produce theoretically optimal play in all situations, but it addresses the specific observed failure mode.

2. **Defensive focus**: By focusing on blocking forks rather than creating them, the AI may miss some winning opportunities, but this matches the current design philosophy.

---

## Known Limitations / Risks

1. **Edge cases**: There may be complex fork scenarios not covered by simple detection logic.

2. **Testing complexity**: Fork scenarios require specific board setups that need careful test case design.

3. **Future maintainability**: If more AI improvements are needed, the priority-based approach may become unwieldy and minimax might become necessary.

---

## Justification for Scope

The game log clearly shows the AI losing to a basic fork strategy. This is a specific, reproducible bug that can be fixed with targeted logic. A full algorithm rewrite is not justified for this single issue.

---

## Next Role

Ready for **Program Manager** to create Design Review document.
