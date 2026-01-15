# Project Owner Notes: WIP-007 - Game Logging for AI Training Data

## Decisions Made

1. **JSON format for logs**: Machine-readable, easy to parse for future ML work
2. **Single log file with append**: Simple implementation, all games in one file
3. **Log on game completion only**: Not during gameplay to avoid performance impact
4. **Include move history**: Essential for analyzing game patterns
5. **Graceful failure handling**: Logging errors should not break the game

## Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| JSON format | Machine-readable, structured | Slightly larger file size | ? Selected |
| CSV format | Compact, spreadsheet-friendly | Harder to store move arrays | Rejected |
| Plain text | Human-readable | Hard to parse programmatically | Rejected |
| SQLite database | Queryable, structured | External dependency complexity | Rejected |
| One file per game | Easy to manage individual games | Many files created | Rejected |

## Log Data Fields

| Field | Type | Purpose |
|-------|------|---------|
| `timestamp` | ISO 8601 string | When game ended |
| `ai_enabled` | boolean | Whether AI was playing |
| `winner` | string | "X", "O", or "Draw" |
| `moves` | array | Ordered list of all moves |
| `total_moves` | integer | Quick reference for game length |

## Tradeoffs Accepted

- Single file will grow indefinitely (acceptable for initial implementation)
- No log rotation or cleanup (can add in future work item)
- Synchronous file I/O (acceptable for small writes)

## Known Limitations or Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Log file grows large | Low (small games) | Future: add rotation |
| File write fails | Low | Graceful error handling |
| Disk full | Very Low | Log error, continue game |

## Future Enhancement Opportunities

1. Log file rotation when size exceeds threshold
2. Statistics aggregation from logs
3. ML training pipeline integration
4. Game replay functionality
5. Export to cloud storage

## Source

User request: "I want you to log out each game played. This will be used later to improve the AI strategy."
