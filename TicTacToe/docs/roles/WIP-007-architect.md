# Architect Notes: WIP-007 - Game Logging for AI Training Data

## Decisions Made

1. **Approved architecture** - logging in existing class is appropriate
2. **Standard library only** - no external dependencies
3. **Fire-and-forget pattern** - logging failures don't affect game

## Alternatives Considered

- Separate Logger class (rejected - overkill for scope)
- Async logging (rejected - unnecessary complexity)

## Tradeoffs Accepted

- Synchronous file I/O (acceptable for small writes)
- Coupled to TicTacToe class (acceptable for single-file structure)

## Known Limitations or Risks

- None significant

## Recommendations (non-blocking)

1. Consider log rotation in future
2. Consider game ID for correlation
