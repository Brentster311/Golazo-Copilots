"""
Tic-Tac-Toe GUI Game
Work Items: WIP-001, WIP-002, WIP-007, WIP-008

A graphical tic-tac-toe game using tkinter for two human players,
with optional AI opponent for single-player mode.
"""

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import font


class TicTacToe:
    """Main game class that handles both UI and game logic."""

    AI_DELAY_MS = 500  # Delay before AI makes a move (milliseconds)
    CORNERS = [(0, 0), (0, 2), (2, 0), (2, 2)]
    SIDES = [(0, 1), (1, 0), (1, 2), (2, 1)]
    LOG_FILE = "game_log.json"

    def __init__(self, root):
        """Initialize the game window and state."""
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.root.resizable(False, False)

        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.ai_enabled = None  # Will be set to BooleanVar in _create_widgets
        self.move_history = []  # Track moves for logging

        self._create_widgets()

    def _create_widgets(self):
        """Create and layout all UI widgets."""
        button_font = font.Font(size=32, weight="bold")
        status_font = font.Font(size=14)

        self.status_label = tk.Label(
            self.root,
            text=f"Player {self.current_player}'s turn",
            font=status_font,
            pady=10
        )
        self.status_label.grid(row=0, column=0, columnspan=3)

        for row in range(3):
            for col in range(3):
                button = tk.Button(
                    self.root,
                    text="",
                    font=button_font,
                    width=4,
                    height=2,
                    command=lambda r=row, c=col: self.make_move(r, c)
                )
                button.grid(row=row + 1, column=col, padx=2, pady=2)
                self.buttons[row][col] = button

        # AI toggle checkbox
        self.ai_enabled = tk.BooleanVar(value=False)
        self.ai_checkbox = tk.Checkbutton(
            self.root,
            text="Play against AI",
            variable=self.ai_enabled,
            font=status_font,
            command=self._on_ai_toggle
        )
        self.ai_checkbox.grid(row=4, column=0, columnspan=3, pady=5)

        self.reset_button = tk.Button(
            self.root,
            text="New Game",
            font=status_font,
            command=self.reset_game
        )
        self.reset_button.grid(row=5, column=0, columnspan=3, pady=10)

    def make_move(self, row, col):
        """Handle a player's move at the specified cell."""
        if self.game_over:
            return
        if self.board[row][col] != "":
            return

        # Record move for logging
        self.move_history.append({
            "player": self.current_player,
            "row": row,
            "col": col
        })

        self.board[row][col] = self.current_player
        self.buttons[row][col].config(text=self.current_player)

        winner = self.check_winner()
        if winner:
            self.status_label.config(text=f"Player {winner} wins!")
            self.game_over = True
            self._log_game(winner)
        elif self._is_board_full():
            self.status_label.config(text="It's a draw!")
            self.game_over = True
            self._log_game("Draw")
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.status_label.config(text=f"Player {self.current_player}'s turn")
            # Trigger AI move if enabled and it's O's turn
            self._trigger_ai_move()

    def _on_ai_toggle(self):
        """Handle AI checkbox toggle."""
        # If AI was just enabled and it's O's turn, trigger AI move
        self._trigger_ai_move()

    def _trigger_ai_move(self):
        """Schedule AI move if conditions are met."""
        if (self.ai_enabled and self.ai_enabled.get() and 
            self.current_player == "O" and not self.game_over):
            self.status_label.config(text="AI is thinking...")
            self.root.after(self.AI_DELAY_MS, self._make_ai_move)

    def _make_ai_move(self):
        """Execute AI move."""
        if self.game_over or self.current_player != "O":
            return
        if not self.ai_enabled or not self.ai_enabled.get():
            return

        move = self._find_best_move()
        if move:
            row, col = move
            self.make_move(row, col)

    def _find_best_move(self):
        """Find the best move for AI using priority strategy."""
        # Priority 1: Win if possible
        winning_move = self._find_winning_move("O")
        if winning_move:
            return winning_move

        # Priority 2: Block opponent's win
        blocking_move = self._find_winning_move("X")
        if blocking_move:
            return blocking_move

        # Priority 3: Block opponent's fork
        fork_block = self._find_fork_block("X")
        if fork_block:
            return fork_block

        # Priority 4: Take center
        if self.board[1][1] == "":
            return (1, 1)

        # Priority 5: Take a corner
        for row, col in self.CORNERS:
            if self.board[row][col] == "":
                return (row, col)

        # Priority 6: Take any side
        for row, col in self.SIDES:
            if self.board[row][col] == "":
                return (row, col)

        return None

    def _find_fork_block(self, player):
        """Find a move that blocks the opponent's fork setup.
        
        A fork occurs when a player can create two winning threats simultaneously.
        This method detects potential fork setups and returns a blocking move.
        
        Args:
            player: The player whose fork we want to block ('X' or 'O')
            
        Returns:
            Tuple (row, col) of the blocking move, or None if no fork threat.
        """
        # Find all cells where opponent could create a fork
        fork_cells = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == "":
                    # Simulate placing opponent's mark
                    self.board[row][col] = player
                    
                    # Count winning threats this would create
                    threats = self._count_winning_threats(player)
                    
                    # Undo simulation
                    self.board[row][col] = ""
                    
                    # If this creates 2+ threats, it's a fork cell
                    if threats >= 2:
                        fork_cells.append((row, col))
        
        # If opponent has fork cells, we need to block
        if fork_cells:
            # If only one fork cell, block it directly
            if len(fork_cells) == 1:
                return fork_cells[0]
            
            # Multiple fork cells: create a threat that forces opponent to block
            # while also blocking one of their fork cells
            ai_player = "O" if player == "X" else "X"
            for row in range(3):
                for col in range(3):
                    if self.board[row][col] == "":
                        # Simulate AI placing here
                        self.board[row][col] = ai_player
                        
                        # Check if this creates a threat for AI
                        ai_threats = self._count_winning_threats(ai_player)
                        
                        # Undo simulation
                        self.board[row][col] = ""
                        
                        # If we create a threat AND don't give opponent a fork response
                        if ai_threats >= 1:
                            # Check if opponent's forced block position is a fork cell
                            # This is complex, so just take an edge if available
                            if (row, col) in self.SIDES:
                                return (row, col)
            
            # Fallback: block first fork cell
            return fork_cells[0]
        
        # Special case: opposite corners pattern (diagonal fork setup)
        # If X has opposite corners and O has center, O should take an edge
        # BUT only if the diagonals aren't already blocked by O
        opposite_corners = [((0, 0), (2, 2)), ((0, 2), (2, 0))]
        for corner1, corner2 in opposite_corners:
            if (self.board[corner1[0]][corner1[1]] == player and 
                self.board[corner2[0]][corner2[1]] == player and
                self.board[1][1] != "" and self.board[1][1] != player):
                # Check if the fork is still possible (diagonal not blocked)
                # For (0,0)-(2,2) diagonal, check if any other cell has opponent
                # For (0,2)-(2,0) diagonal, same check
                if corner1 == (0, 0):  # Main diagonal
                    # Check if diagonal is blocked
                    diagonal = [self.board[0][0], self.board[1][1], self.board[2][2]]
                    other_player = "O" if player == "X" else "X"
                    if diagonal.count(other_player) > 0:
                        continue  # Diagonal blocked, skip this pattern
                else:  # Anti-diagonal
                    anti_diag = [self.board[0][2], self.board[1][1], self.board[2][0]]
                    other_player = "O" if player == "X" else "X"
                    if anti_diag.count(other_player) > 0:
                        continue  # Anti-diagonal blocked, skip
                
                # Opponent has opposite corners, we have center - take an edge
                for edge in self.SIDES:
                    if self.board[edge[0]][edge[1]] == "":
                        return edge
        
        return None

    def _count_winning_threats(self, player):
        """Count lines where player has 2 marks and 1 empty cell."""
        threats = 0
        
        # Check rows
        for row in range(3):
            cells = [self.board[row][c] for c in range(3)]
            if cells.count(player) == 2 and cells.count("") == 1:
                threats += 1
        
        # Check columns
        for col in range(3):
            cells = [self.board[r][col] for r in range(3)]
            if cells.count(player) == 2 and cells.count("") == 1:
                threats += 1
        
        # Check diagonal
        diagonal = [self.board[i][i] for i in range(3)]
        if diagonal.count(player) == 2 and diagonal.count("") == 1:
            threats += 1
        
        # Check anti-diagonal
        anti_diagonal = [self.board[i][2-i] for i in range(3)]
        if anti_diagonal.count(player) == 2 and anti_diagonal.count("") == 1:
            threats += 1
        
        return threats

    def _find_winning_move(self, player):
        """Find a winning move for the given player, or None."""
        # Check rows
        for row in range(3):
            cells = [(row, 0), (row, 1), (row, 2)]
            move = self._check_line_for_win(cells, player)
            if move:
                return move

        # Check columns
        for col in range(3):
            cells = [(0, col), (1, col), (2, col)]
            move = self._check_line_for_win(cells, player)
            if move:
                return move

        # Check diagonal
        diagonal = [(0, 0), (1, 1), (2, 2)]
        move = self._check_line_for_win(diagonal, player)
        if move:
            return move

        # Check anti-diagonal
        anti_diagonal = [(0, 2), (1, 1), (2, 0)]
        move = self._check_line_for_win(anti_diagonal, player)
        if move:
            return move

        return None

    def _check_line_for_win(self, cells, player):
        """Check if a line has 2 player marks and 1 empty. Return empty cell or None."""
        values = [self.board[r][c] for r, c in cells]
        if values.count(player) == 2 and values.count("") == 1:
            empty_index = values.index("")
            return cells[empty_index]
        return None

    def check_winner(self):
        """Check if there's a winner. Returns 'X', 'O', or None."""
        # Check rows
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != "":
                return self.board[row][0]

        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != "":
                return self.board[0][col]

        # Check diagonal (top-left to bottom-right)
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            return self.board[0][0]

        # Check anti-diagonal (top-right to bottom-left)
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            return self.board[0][2]

        return None

    def _is_board_full(self):
        """Check if the board is completely filled."""
        return all(cell != "" for row in self.board for cell in row)

    def _log_game(self, winner):
        """Log completed game to JSON file."""
        try:
            game_data = {
                "timestamp": datetime.now().isoformat(),
                "ai_enabled": self.ai_enabled.get() if self.ai_enabled else False,
                "winner": winner,
                "moves": self.move_history,
                "total_moves": len(self.move_history)
            }

            # Read existing logs or start fresh
            logs = []
            if os.path.exists(self.LOG_FILE):
                try:
                    with open(self.LOG_FILE, 'r') as f:
                        logs = json.load(f)
                except (json.JSONDecodeError, IOError):
                    logs = []

            # Append new game
            logs.append(game_data)

            # Write back to file
            with open(self.LOG_FILE, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception:
            # Logging failures should not crash the game
            pass

    def reset_game(self):
        """Reset the game to initial state."""
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        self.move_history = []  # Clear move history

        for row in range(3):
            for col in range(3):
                self.buttons[row][col].config(text="")

        self.status_label.config(text=f"Player {self.current_player}'s turn")


def main():
    """Entry point for the application."""
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()


if __name__ == "__main__":
    main()
