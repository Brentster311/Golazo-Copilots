# Design Review: WIP-007 - Game Logging for AI Training Data

## Summary
Add automatic game logging to capture completed games in JSON format for future AI strategy analysis.

## Problem Statement
Currently, no game data is captured. To improve the AI strategy in the future, we need historical game data showing move sequences, outcomes, and game modes.

## Business Case
- **Why now**: Foundation for future AI improvements
- **Impact**: Enables data-driven AI enhancement
- **KPIs**: Number of games logged, data quality for ML training

## Stakeholders
- Developers who will analyze game data
- Future ML training pipelines

## Functional Requirements
1. Log each completed game (win or draw) to a JSON file
2. Include timestamp, AI mode, winner, and complete move history
3. Append to existing log file (don't overwrite)
4. Create log file if it doesn't exist

## Non-functional Requirements
1. No external dependencies (standard library only)
2. Logging failures must not crash the game
3. No noticeable performance impact

## Proposed Approach

### Data Structure
```json
{
  "timestamp": "ISO-8601 format",
  "ai_enabled": boolean,
  "winner": "X" | "O" | "Draw",
  "moves": [{"player": "X", "row": 0, "col": 0}, ...],
  "total_moves": integer
}
```

### Implementation
1. Add `move_history` list to track moves during game
2. Record each move in `make_move()` method
3. Add `_log_game(winner)` method called on game end
4. Clear history on `reset_game()`
5. Use try/except for graceful failure handling

### File Location
- `game_log.json` in the working directory
- Configurable via `LOG_FILE` class constant

## Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| JSON format | Machine-readable, structured | Slightly larger | ? Selected |
| CSV format | Compact | Hard to store move arrays | Rejected |
| SQLite | Queryable | External complexity | Rejected |
| One file per game | Easy management | Many files | Rejected |

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Log file grows large | Low | Future: add rotation |
| Disk write fails | Low | Graceful exception handling |
| Corrupted JSON | Low | Handle JSONDecodeError |

## Dependencies
- None (standard library only: json, os, datetime)

## Migration / Rollout Plan
- New feature, backward compatible
- Log file can be deleted without affecting game

## Observability Plan
- Log file itself is the observability artifact

## Test Strategy
- Unit tests for move history tracking
- Unit tests for log file creation and content
- Test graceful handling of write failures
