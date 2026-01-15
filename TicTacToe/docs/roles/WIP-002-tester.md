# Tester Notes: WIP-002 - AI Player Option for O

## Decisions Made

1. **19 unit test cases defined**: Cover AI strategy, toggle behavior, integration
2. **4 manual test cases for GUI**: Timing, visual feedback, checkbox behavior
3. **All acceptance criteria mapped to tests**: Full traceability

## Test Categories

| Category | Test Count | Purpose |
|----------|------------|---------|
| AI Strategy | 6 tests | Win, block, center, corner, side priority |
| Toggle Behavior | 5 tests | Enable, disable, mid-game toggle |
| Integration | 4 tests | Two-player compatibility, reset, legal moves |
| Helper Methods | 4 tests | _find_winning_move for rows, cols, diagonals |
| Manual/GUI | 4 tests | Visual verification |

## Alternatives Considered

1. **Property-based testing for AI**: 
   - Could generate random boards
   - Overkill for deterministic strategy
   - Rejected

2. **Automated GUI testing**:
   - Would require additional dependencies
   - Manual testing sufficient
   - Rejected

## Tradeoffs Accepted

- Some timing tests require manual verification
- AI delay cannot be easily unit tested (uses tkinter after())

## Known Limitations or Risks

- Testing `root.after()` timing is difficult in unit tests
- Will mock or skip timing in unit tests, verify manually
