# TTT-0001 Design Document (MVP)

## 1) Scope and Constraints
- Platform: Windows only.
- UI: simple desktop GUI for two local human players.
- Persistence: in-memory only (reset on app close).
- Out of scope: AI opponent, online play, accounts, history persistence, alternate board sizes.

## 2) Architecture (Minimal)
Use a small single-process desktop app with clear separation:
- **UI Layer**: window, 3x3 grid buttons, status label, restart button, optional in-session counters display.
- **Game Engine Layer**: pure game state + rules (turn handling, move validation, win/draw evaluation, lock state).
- **Session Stats Layer**: in-memory counters (`games_played`, `x_wins`, `o_wins`, `draws`).

Recommended modules (implementation-ready):
- `app.py` (entry + UI wiring)
- `game_state.py` (state model + rule methods)

## 3) Data Model
`GameState` (in memory):
- `board: list[str]` length 9; values: `""`, `"X"`, `"O"`
- `current_player: str` (`"X"` starts)
- `status: str` (`"IN_PROGRESS" | "X_WON" | "O_WON" | "DRAW"`)
- `locked: bool` (true after terminal state)

`SessionStats`:
- `games_played: int`
- `x_wins: int`
- `o_wins: int`
- `draws: int`

## 4) UI Layout
Single window, fixed/simple layout:
- Top: status text (e.g., `Turn: X`, `Winner: O`, `Draw`).
- Center: 3x3 board of clickable cells (uniform size, readable font).
- Bottom: `Restart` button.
- Optional small text row for in-session counters.

UI behavior rules:
- Empty cell click places current player symbol.
- Occupied cell click does nothing (or brief non-blocking message).
- After win/draw: board interactions disabled until restart.

## 5) Game Rules Handling
On cell click (`index` 0..8):
1. If `locked` is true: ignore input.
2. If index invalid or cell occupied: ignore input.
3. Write mark for `current_player`.
4. Evaluate terminal state:
   - Win if any winning line has same non-empty symbol.
   - Draw if board full and no win.
5. If terminal:
   - Set `status` (`X_WON`/`O_WON`/`DRAW`), set `locked = true`.
   - Increment `games_played` and appropriate win/draw counter.
6. Else toggle player (`X <-> O`) and update status text.

Winning lines (indices):
- Rows: `[0,1,2]`, `[3,4,5]`, `[6,7,8]`
- Columns: `[0,3,6]`, `[1,4,7]`, `[2,5,8]`
- Diagonals: `[0,4,8]`, `[2,4,6]`

## 6) Winner/Draw Detection
Provide pure functions/methods for testability:
- `check_winner(board) -> "X" | "O" | None`
- `is_draw(board) -> bool` (true when no empties and no winner)

Order of evaluation after each valid move:
1. Check winner.
2. Else check draw.
3. Else continue game.

## 7) Restart Flow
`restart_game()`:
- Reset board to empty.
- Set `current_player = "X"`.
- Set `status = "IN_PROGRESS"` and `locked = false`.
- Keep session stats unchanged.
- Refresh UI immediately (clear board text + status label).

## 8) Error Handling (MVP)
- Invalid UI index/callback mismatch: safely ignore and keep app responsive.
- Double-click/race-like repeated click on same cell: second action ignored by occupied check.
- Unexpected exceptions in UI callbacks: catch at handler boundary, show concise message, avoid crash if possible.
- No file/network errors expected (no external dependency for gameplay).

## 9) Testability Notes (MVP)
Prioritize unit tests for rule logic (UI-agnostic):
- Initial state (empty board, X turn, in progress).
- Valid move updates board and toggles turn.
- Occupied cell is rejected (state unchanged).
- All 8 win line patterns detected.
- Draw detected on full non-winning board.
- Post-terminal move attempts are blocked.
- Restart resets game state but preserves session counters.

Optional lightweight integration checks:
- Launch window renders board + status + restart.
- Clicking through a known win path updates status and locks board.
- Restart restores interactive state.

## 10) Definition of Done Mapping
This design satisfies the story AC by ensuring:
- 3x3 board + turn indicator on launch.
- Click-only placement into empty cells.
- Winner/draw detection after every move.
- Board lock after terminal state.
- Restart resets board and turn to X for immediate replay.
