# Test Cases: WIP-007 - Game Logging for AI Training Data

## Test Strategy
Unit tests using mocked tkinter to verify logging functionality without GUI.

## Test Cases

### TC-301: Move History Recorded
- **Description**: Verify moves are recorded in history during gameplay
- **Precondition**: New game started
- **Steps**: Make moves at (0,0) and (1,1)
- **Expected**: `move_history` contains 2 entries with correct player, row, col

### TC-302: Move History Cleared on Reset
- **Description**: Verify move history is cleared when game resets
- **Precondition**: Game with moves made
- **Steps**: Call `reset_game()`
- **Expected**: `move_history` is empty

### TC-303: Log File Created on Game End
- **Description**: Verify log file is created when game ends with win
- **Precondition**: No log file exists
- **Steps**: Play game to X win
- **Expected**: Log file exists on disk

### TC-304: Log Contains Correct Winner
- **Description**: Verify log contains correct winner
- **Precondition**: Game completed
- **Steps**: Play game to X win, read log
- **Expected**: Log entry has `"winner": "X"`

### TC-305: Log Contains Move History
- **Description**: Verify log contains complete move history
- **Precondition**: Game completed
- **Steps**: Play 5-move game to win, read log
- **Expected**: Log entry has `total_moves: 5` and 5 moves in array

### TC-306: Log Contains AI Status
- **Description**: Verify log contains AI enabled/disabled status
- **Precondition**: Game completed with AI disabled
- **Steps**: Play game, read log
- **Expected**: Log entry has `"ai_enabled": false`

### TC-307: Log Contains Timestamp
- **Description**: Verify log contains timestamp
- **Precondition**: Game completed
- **Steps**: Play game, read log
- **Expected**: Log entry has `timestamp` field with ISO format

### TC-308: Draw Game Logged
- **Description**: Verify draw games are logged correctly
- **Precondition**: None
- **Steps**: Play game to draw (9 moves, no winner)
- **Expected**: Log entry has `"winner": "Draw"` and `total_moves: 9`

### TC-309: Multiple Games Appended
- **Description**: Verify multiple games are appended to log
- **Precondition**: None
- **Steps**: Play two complete games
- **Expected**: Log file contains array with 2 entries

### TC-310: Logging Failure Does Not Crash Game
- **Description**: Verify logging failure doesn't crash the game
- **Precondition**: Log file path set to invalid location
- **Steps**: Play game to completion
- **Expected**: Game ends normally, no exception raised

## Acceptance Criteria Mapping

| Acceptance Criteria | Test Case(s) |
|---------------------|--------------|
| Each completed game is logged | TC-303, TC-308 |
| Log includes timestamp | TC-307 |
| Log includes game mode | TC-306 |
| Log includes winner | TC-304, TC-308 |
| Log includes move history | TC-301, TC-305 |
| Log format is JSON | TC-304, TC-305, TC-306 |
| Logging doesn't affect performance | N/A (manual) |
| Logging failures don't crash | TC-310 |
| Log file created if missing | TC-303 |
| Log file appended | TC-309 |
