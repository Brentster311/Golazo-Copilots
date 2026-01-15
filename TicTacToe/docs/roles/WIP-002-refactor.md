# Refactor Expert Notes: WIP-002 - AI Player Option for O

## Decisions Made

1. **Extracted CORNERS and SIDES as class constants**: Improves readability and potential reuse
   - `CORNERS = [(0, 0), (0, 2), (2, 0), (2, 2)]`
   - `SIDES = [(0, 1), (1, 0), (1, 2), (2, 1)]`

2. **No other changes needed**: Code is well-structured after WIP-002 implementation

## Changes Applied

### Class constants added

**Before:**
```python
class TicTacToe:
    AI_DELAY_MS = 500

    def _find_best_move(self):
        ...
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for row, col in corners:
            ...
        sides = [(0, 1), (1, 0), (1, 2), (2, 1)]
        for row, col in sides:
            ...
```

**After:**
```python
class TicTacToe:
    AI_DELAY_MS = 500
    CORNERS = [(0, 0), (0, 2), (2, 0), (2, 2)]
    SIDES = [(0, 1), (1, 0), (1, 2), (2, 1)]

    def _find_best_move(self):
        ...
        for row, col in self.CORNERS:
            ...
        for row, col in self.SIDES:
            ...
```

## Alternatives Considered

1. **Extract DIAGONAL and ANTI_DIAGONAL constants**: Could do but only used in one place each
2. **Create WINNING_LINES constant**: Would require refactoring check_winner - out of scope
3. **Extract AI strategy to separate class**: Overkill for current scope

## Tradeoffs Accepted

- Kept simple refactoring to avoid introducing new risks
- No behavior changes

## Known Limitations or Risks

- None introduced by this refactoring

## Verification

- All 37 unit tests pass after refactoring
- No behavior changes
