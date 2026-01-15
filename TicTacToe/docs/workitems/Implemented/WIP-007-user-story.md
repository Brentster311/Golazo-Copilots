# User Story: WIP-007 - Game Logging for AI Training Data

**Status**: ? IMPLEMENTED

## Title
Log Each Game Played for Future AI Strategy Improvement

## As a
Developer who wants to improve the AI strategy

## I want
Each completed game to be logged with full move history

## So that
- Game data can be analyzed to identify patterns
- AI strategy can be improved based on real gameplay
- Training data is available for future machine learning approaches
- Win/loss patterns can be studied

## Out of scope
- Implementing AI improvements based on the logs (future work)
- Real-time AI adaptation during gameplay
- Cloud storage or database integration
- Log file rotation or cleanup
- Replaying games from logs
- User interface for viewing logs

## Assumptions
- Logs stored in local file (e.g., `game_log.json` or `game_log.txt`)
- Each game is a separate log entry with timestamp
- Logging happens automatically when game ends (win or draw)
- Log format is machine-readable (JSON preferred for future ML use)
- Logs persist across application restarts (append mode)
- Both AI and human vs human games are logged

## Acceptance Criteria
- [x] Each completed game is logged to a file
- [x] Log includes timestamp of when game ended
- [x] Log includes game mode (AI enabled/disabled)
- [x] Log includes winner (X, O, or Draw)
- [x] Log includes complete move history in order
- [x] Log format is JSON for easy parsing
- [x] Logging does not affect game performance
- [x] Logging failures do not crash the game (graceful handling)
- [x] Log file is created if it doesn't exist
- [x] Log file is appended to (not overwritten) on each game

## Non-functional requirements
- No external dependencies (use standard library `json` module)
- Logging should be non-blocking (not noticeable to user)
- Log file size is not a concern for initial implementation
- Single file structure maintained

## Telemetry / metrics expected
- Number of games logged
- Win rate by player (X vs O)
- Win rate when AI enabled vs disabled

## Rollout / rollback notes
- New feature, backward compatible
- If logging fails, game should still work normally
- Log file can be deleted without affecting game

## Example Log Entry (JSON)
```json
{
  "timestamp": "2025-01-14T15:30:00",
  "ai_enabled": true,
  "winner": "X",
  "moves": [
    {"player": "X", "row": 1, "col": 1},
    {"player": "O", "row": 0, "col": 0},
    {"player": "X", "row": 0, "col": 2},
    {"player": "O", "row": 2, "col": 0},
    {"player": "X", "row": 2, "col": 2},
    {"player": "O", "row": 0, "col": 1},
    {"player": "X", "row": 1, "col": 0}
  ],
  "total_moves": 7
}
```

## Future Use Cases (Out of Scope for WIP-007)
- Analyze logs to find weaknesses in AI strategy
- Train ML model on game data
- Generate statistics dashboard
- Identify common human strategies to counter
