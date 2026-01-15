# Test Cases: WIP-001 - Tic-Tac-Toe GUI Game

## Test Strategy
- Unit tests for game logic (win detection, draw detection, turn management)
- Manual verification for GUI interactions

---

## Unit Test Cases

### TC-001: Initial Game State
**Description**: Verify game initializes correctly
**Preconditions**: None
**Steps**:
1. Create new TicTacToe instance
**Expected Results**:
- Board is empty (all cells None or empty string)
- Current player is 'X'
- Game is not over

### TC-002: Player X Makes First Move
**Description**: Verify first move places X
**Preconditions**: New game
**Steps**:
1. Click cell at position (0, 0)
**Expected Results**:
- Cell (0, 0) shows 'X'
- Current player changes to 'O'

### TC-003: Players Alternate Turns
**Description**: Verify turn alternation
**Preconditions**: New game
**Steps**:
1. Make move at (0, 0)
2. Make move at (0, 1)
3. Make move at (0, 2)
**Expected Results**:
- (0, 0) = 'X'
- (0, 1) = 'O'
- (0, 2) = 'X'

### TC-004: Cannot Overwrite Occupied Cell
**Description**: Verify occupied cells are protected
**Preconditions**: New game
**Steps**:
1. Make move at (1, 1) as X
2. Attempt move at (1, 1) as O
**Expected Results**:
- Cell (1, 1) still shows 'X'
- Current player still 'O'

### TC-005: Horizontal Win Detection (Row 0)
**Description**: Verify horizontal win in first row
**Preconditions**: New game
**Steps**:
1. X at (0, 0)
2. O at (1, 0)
3. X at (0, 1)
4. O at (1, 1)
5. X at (0, 2)
**Expected Results**:
- Game declares X as winner
- Game is over

### TC-006: Horizontal Win Detection (Row 1)
**Description**: Verify horizontal win in second row
**Steps**: Place X in cells (1,0), (1,1), (1,2) with O moves elsewhere
**Expected Results**: X wins

### TC-007: Horizontal Win Detection (Row 2)
**Description**: Verify horizontal win in third row
**Steps**: Place X in cells (2,0), (2,1), (2,2) with O moves elsewhere
**Expected Results**: X wins

### TC-008: Vertical Win Detection (Column 0)
**Description**: Verify vertical win in first column
**Steps**: Place X in cells (0,0), (1,0), (2,0) with O moves elsewhere
**Expected Results**: X wins

### TC-009: Vertical Win Detection (Column 1)
**Description**: Verify vertical win in second column
**Steps**: Place X in cells (0,1), (1,1), (2,1) with O moves elsewhere
**Expected Results**: X wins

### TC-010: Vertical Win Detection (Column 2)
**Description**: Verify vertical win in third column
**Steps**: Place X in cells (0,2), (1,2), (2,2) with O moves elsewhere
**Expected Results**: X wins

### TC-011: Diagonal Win Detection (Top-Left to Bottom-Right)
**Description**: Verify diagonal win
**Steps**: Place X in cells (0,0), (1,1), (2,2) with O moves elsewhere
**Expected Results**: X wins

### TC-012: Diagonal Win Detection (Top-Right to Bottom-Left)
**Description**: Verify anti-diagonal win
**Steps**: Place X in cells (0,2), (1,1), (2,0) with O moves elsewhere
**Expected Results**: X wins

### TC-013: Draw Detection
**Description**: Verify draw when board is full with no winner
**Preconditions**: New game
**Steps**: Fill board without creating 3 in a row
```
X | O | X
---------
X | O | O
---------
O | X | X
```
**Expected Results**:
- Game declares a draw
- Game is over

### TC-014: No Moves After Win
**Description**: Verify game stops accepting moves after win
**Preconditions**: Game where X has won
**Steps**:
1. Complete a winning game for X
2. Attempt to click an empty cell
**Expected Results**:
- Cell remains empty
- Game state unchanged

### TC-015: Reset Game Functionality
**Description**: Verify reset clears the board
**Preconditions**: Game in progress with some moves made
**Steps**:
1. Make several moves
2. Click reset/new game button
**Expected Results**:
- All cells are empty
- Current player is 'X'
- Game is not over
- Status shows "Player X's turn"

### TC-016: O Can Win
**Description**: Verify O can also win
**Steps**: Arrange board so O gets 3 in a row
**Expected Results**: O wins, game over

---

## Manual Test Cases (GUI Verification)

### TC-M01: Window Displays Correctly
**Steps**: Launch application
**Expected**: Window appears with 3x3 grid, status label, and reset button

### TC-M02: Button Click Visual Feedback
**Steps**: Click empty cell
**Expected**: Cell immediately shows X or O, button text updates

### TC-M03: Status Label Updates
**Steps**: Make moves and win/draw
**Expected**: Status label reflects current player or game result

### TC-M04: Reset Button Works
**Steps**: Click reset button
**Expected**: All cells clear, status resets

---

## Acceptance Criteria Mapping

| AC | Test Cases |
|----|------------|
| 3x3 grid displayed | TC-M01 |
| Players alternate | TC-002, TC-003 |
| Click places mark | TC-002, TC-M02 |
| Occupied cell protected | TC-004 |
| Winner detected | TC-005 through TC-012, TC-016 |
| Draw detected | TC-013 |
| Reset available | TC-015, TC-M04 |
| Turn displayed | TC-M03 |
| Responsive UI | TC-M02 |
