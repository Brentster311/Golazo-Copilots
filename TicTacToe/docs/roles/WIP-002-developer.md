# Developer Notes: WIP-002 - AI Player Option for O

## Decisions Made

1. **AI_DELAY_MS as class constant**: 500ms delay configurable in one place
2. **Priority-based strategy**: Win > Block > Center > Corner > Side
3. **Helper method `_find_winning_move`**: Reusable for both winning and blocking
4. **`_check_line_for_win`**: Generic line checker for rows, cols, diagonals
5. **BooleanVar for checkbox**: Standard tkinter pattern for checkbox state

## Implementation Details

### New Methods Added

| Method | Purpose |
|--------|---------|
| `_on_ai_toggle()` | Handle checkbox toggle, trigger AI if needed |
| `_trigger_ai_move()` | Schedule AI move with delay using `root.after()` |
| `_make_ai_move()` | Execute the AI move after delay |
| `_find_best_move()` | AI strategy - returns best (row, col) |
| `_find_winning_move(player)` | Find winning move for player |
| `_check_line_for_win(cells, player)` | Check if line has win opportunity |

### Modified Methods

| Method | Changes |
|--------|---------|
| `__init__` | Added `ai_enabled` attribute |
| `_create_widgets` | Added checkbox widget, moved reset button to row 5 |
| `make_move` | Added call to `_trigger_ai_move()` after turn change |

### AI Strategy Priority

1. **Win**: If O can complete a line, do it
2. **Block**: If X can win next turn, block that cell
3. **Center**: Take (1,1) if available
4. **Corner**: Take any corner (0,0), (0,2), (2,0), (2,2)
5. **Side**: Take any side (0,1), (1,0), (1,2), (2,1)

## Alternatives Considered

1. **Minimax algorithm**: Perfect play but not fun - rejected
2. **Random AI**: Too easy, not fun - rejected
3. **Separate AI class**: Cleaner but overkill for scope - rejected

## Tradeoffs Accepted

- AI is deterministic (same game = same AI moves)
- Single difficulty level only
- AI always O, never X

## Known Limitations or Risks

- AI delay cannot be unit tested easily (uses tkinter.after)
- Strategy is good but not perfect - can be beaten

## Test Coverage

18 new tests added:
- 6 AI strategy tests (TC-201 to TC-206)
- 8 toggle behavior tests (TC-207 to TC-215)
- 4 helper method tests (TC-216 to TC-219)

Total: 37 tests (19 WIP-001 + 18 WIP-002)

## Commands to Run

```bash
# Run the game
python PythonApplication2.py

# Run all tests
python -m unittest test_tictactoe -v

# Run only AI tests
python -m unittest test_tictactoe.TestAIStrategy test_tictactoe.TestAIToggleBehavior test_tictactoe.TestFindWinningMove -v
```
