# Developer Notes: WIP-007 - Game Logging for AI Training Data

## Decisions Made

1. **Added imports**: `json`, `os`, `datetime`
2. **Added LOG_FILE constant**: Configurable log file path
3. **Added move_history list**: Tracks moves during game
4. **Added _log_game method**: Writes JSON to file
5. **Try/except for graceful failure**: Logging errors don't crash game

## Implementation Details

### New Class Attributes
| Attribute | Type | Purpose |
|-----------|------|---------|
| `LOG_FILE` | str | Path to log file |
| `move_history` | list | Stores moves during game |

### New Methods
| Method | Purpose |
|--------|---------|
| `_log_game(winner)` | Write game data to JSON file |

### Modified Methods
| Method | Changes |
|--------|---------|
| `make_move()` | Records move to history, calls `_log_game()` on game end |
| `reset_game()` | Clears `move_history` |

## Alternatives Considered

- Logging on every move (rejected - too much I/O)
- Separate Logger class (rejected - overkill)

## Tradeoffs Accepted

- Synchronous file writes
- Read entire file to append (simple but not optimal for huge files)

## Known Limitations or Risks

- Log file grows indefinitely

## Commands to Run

```bash
# Run the game
python tictactoe.py

# Run all tests
python -m unittest test_tictactoe -v

# View log file
cat game_log.json
```
