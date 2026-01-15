# Test Cases: WIP-002 - AI Player Option for O

## Test Strategy
- Unit tests for AI strategy logic (win, block, center, corner, side)
- Unit tests for toggle behavior
- Unit tests for AI not interfering with two-player mode
- Manual verification for timing and UX

---

## Unit Test Cases

### AI Strategy Tests

#### TC-201: AI Takes Winning Move
**Description**: AI should take winning move when available
**Preconditions**: AI enabled, AI's turn (O)
**Steps**:
1. Set board state where O can win with one move
2. Trigger AI move
**Expected Results**:
- AI places O in winning position
- Game declares O as winner

#### TC-202: AI Blocks Human Win
**Description**: AI should block human's winning move
**Preconditions**: AI enabled, AI's turn (O)
**Steps**:
1. Set board where X can win next turn
2. Trigger AI move
**Expected Results**:
- AI places O to block X's winning line
- Game continues

#### TC-203: AI Takes Center When Available
**Description**: AI prioritizes center after win/block
**Preconditions**: AI enabled, AI's turn, no win/block needed
**Steps**:
1. X moves to corner (0,0)
2. AI moves
**Expected Results**:
- AI takes center (1,1)

#### TC-204: AI Takes Corner When Center Occupied
**Description**: AI takes corner when center not available
**Preconditions**: AI enabled, center occupied, no win/block
**Steps**:
1. Set board with center occupied, no win/block opportunities
2. Trigger AI move
**Expected Results**:
- AI places O in a corner (0,0), (0,2), (2,0), or (2,2)

#### TC-205: AI Takes Side As Last Resort
**Description**: AI takes side when no other option
**Preconditions**: AI enabled, center and corners occupied
**Steps**:
1. Set board with center and all corners occupied
2. Trigger AI move
**Expected Results**:
- AI places O in a side position (0,1), (1,0), (1,2), or (2,1)

#### TC-206: AI Win Priority Over Block
**Description**: AI should win rather than block
**Preconditions**: AI enabled, both win and block available
**Steps**:
1. Set board where AI can win OR block
2. Trigger AI move
**Expected Results**:
- AI takes winning move, not blocking move

### Toggle Behavior Tests

#### TC-207: AI Toggle Default State
**Description**: AI should be disabled by default
**Preconditions**: New game
**Steps**:
1. Create new TicTacToe instance
**Expected Results**:
- AI toggle is unchecked/disabled
- Game is in two-player mode

#### TC-208: Enable AI Toggle
**Description**: Enabling AI activates AI opponent
**Preconditions**: New game, AI disabled
**Steps**:
1. Enable AI toggle
2. X makes move
**Expected Results**:
- AI automatically makes O's move

#### TC-209: Disable AI Mid-Game
**Description**: Disabling AI reverts to two-player
**Preconditions**: Game in progress with AI enabled
**Steps**:
1. Play with AI enabled
2. Disable AI toggle
3. X makes move
**Expected Results**:
- O does NOT move automatically
- Human must click to place O

#### TC-210: Enable AI On O's Turn
**Description**: AI moves when enabled during O's turn
**Preconditions**: Two-player game, O's turn
**Steps**:
1. X makes move (AI disabled)
2. Enable AI toggle (now O's turn)
**Expected Results**:
- AI makes O's move (after delay)

#### TC-211: AI Respects Game Over
**Description**: AI does not move when game is over
**Preconditions**: AI enabled, game won/drawn
**Steps**:
1. Complete a game (win or draw)
2. Observe AI behavior
**Expected Results**:
- AI does not attempt to move
- No errors occur

### Integration with Existing Functionality

#### TC-212: Two-Player Mode Unchanged
**Description**: AI disabled = normal two-player
**Preconditions**: AI disabled
**Steps**:
1. Play entire game with AI disabled
**Expected Results**:
- Game works exactly as WIP-001
- Both players click to move

#### TC-213: Reset Preserves AI Toggle
**Description**: Reset game keeps AI setting
**Preconditions**: AI enabled, game in progress
**Steps**:
1. Enable AI
2. Play some moves
3. Click reset
**Expected Results**:
- Board clears
- AI toggle remains enabled
- AI ready for new game

#### TC-214: AI Makes Only Legal Moves
**Description**: AI never moves to occupied cell
**Preconditions**: AI enabled
**Steps**:
1. Play multiple games with AI
**Expected Results**:
- AI always places O in empty cell
- No errors or overwrites

#### TC-215: AI Does Not Move As X
**Description**: AI only plays as O
**Preconditions**: AI enabled
**Steps**:
1. Start new game with AI
2. Observe turn order
**Expected Results**:
- Human always plays X (first)
- AI always plays O (second)

### Find Winning Move Helper Tests

#### TC-216: Find Winning Move - Row
**Description**: Detect winning move in row
**Steps**: 
1. Set row with two O's and one empty
2. Call _find_winning_move('O')
**Expected Results**: Returns the empty cell position

#### TC-217: Find Winning Move - Column
**Description**: Detect winning move in column
**Steps**:
1. Set column with two O's and one empty
2. Call _find_winning_move('O')
**Expected Results**: Returns the empty cell position

#### TC-218: Find Winning Move - Diagonal
**Description**: Detect winning move on diagonal
**Steps**:
1. Set diagonal with two O's and one empty
2. Call _find_winning_move('O')
**Expected Results**: Returns the empty cell position

#### TC-219: Find Winning Move - None Available
**Description**: Return None when no winning move
**Steps**:
1. Set board with no winning move for player
2. Call _find_winning_move('O')
**Expected Results**: Returns None

---

## Manual Test Cases (GUI Verification)

### TC-M201: AI Checkbox Displays
**Steps**: Launch application
**Expected**: Checkbox labeled "Play against AI" visible below grid

### TC-M202: AI Move Delay Visible
**Steps**: Enable AI, make X move
**Expected**: Brief pause (~500ms) before O appears, status shows "AI is thinking..."

### TC-M203: Checkbox Toggle Works
**Steps**: Click checkbox on/off
**Expected**: Visual feedback, checkbox state changes

### TC-M204: Status Updates for AI
**Steps**: Play game with AI
**Expected**: Status shows "AI is thinking..." during delay, then "Player X's turn"

---

## Acceptance Criteria Mapping

| AC | Test Cases |
|----|------------|
| UI toggle for AI | TC-207, TC-M201, TC-M203 |
| AI moves automatically | TC-208, TC-M202 |
| AI makes legal moves | TC-214 |
| AI makes intelligent moves | TC-201, TC-202, TC-203, TC-204, TC-205, TC-206 |
| Toggle on/off anytime | TC-209, TC-210 |
| Reverts to two-player | TC-209, TC-212 |
| AI move delay | TC-M202 |
| Status reflects AI | TC-M204 |
| Two-player still works | TC-212 |
