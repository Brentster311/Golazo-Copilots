# Tic-Tac-Toe

A classic Tic-Tac-Toe game with a graphical interface and optional AI opponent.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Two-Player Mode**: Play against a friend on the same computer
- **AI Opponent**: Challenge a computer opponent with intelligent strategy
- **Clean GUI**: Simple, intuitive graphical interface using tkinter
- **Game Logging**: All completed games are logged to `game_log.json` for analysis

## Requirements

- Python 3.x
- tkinter (included with standard Python installation)

## Installation

No installation required! Simply clone or download the repository.

```bash
git clone https://github.com/Brentster311/Golazo-Copilots.git
cd Golazo-Copilots/TicTacToe/TicTacToe
```

## How to Play

### Starting the Game

```bash
python tictactoe.py
```

### Game Rules

1. The game is played on a 3x3 grid
2. Player X always goes first
3. Players take turns placing their mark (X or O) in empty cells
4. The first player to get 3 marks in a row (horizontally, vertically, or diagonally) wins
5. If all 9 cells are filled without a winner, the game is a draw

### Controls

- **Click** any empty cell to place your mark
- **"Play against AI"** checkbox: Toggle to enable/disable the AI opponent
- **"New Game"** button: Reset the board and start a fresh game

### Playing Against the AI

1. Check the "Play against AI" checkbox
2. You play as X (first move)
3. The AI plays as O and will respond automatically after each of your moves

The AI uses a strategic priority system:
1. Win if possible
2. Block opponent's winning move
3. Block fork setups (prevents two-way win scenarios)
4. Take the center
5. Take a corner
6. Take a side

## Game Logging

All completed games are automatically saved to `game_log.json` with:
- Timestamp
- Winner (X, O, or Draw)
- Complete move history
- AI enabled status

Example log entry:
```json
{
  "timestamp": "2026-01-14T19:23:13.583073",
  "ai_enabled": true,
  "winner": "Draw",
  "moves": [
    {"player": "X", "row": 0, "col": 0},
    {"player": "O", "row": 1, "col": 1}
  ],
  "total_moves": 9
}
```

## Running Tests

```bash
python -m pytest test_tictactoe.py -v
```

## Project Structure

```
TicTacToe/TicTacToe/
??? tictactoe.py      # Main game application
??? test_tictactoe.py # Unit tests
??? game_log.json     # Game history (auto-generated)
??? README.md         # This file
```

## Development

This project follows the **Golazo** workflow for structured development. See the `docs/` folder for:
- User stories and work items
- Design reviews
- Test cases
- Role-specific documentation

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Please follow the Golazo workflow:
1. Create a User Story
2. Complete Design Review
3. Get Reviewer and Architect approval
4. Write tests (TDD)
5. Implement changes
6. Refactor and verify build
