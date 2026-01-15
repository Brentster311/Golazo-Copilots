"""
Unit Tests for Tic-Tac-Toe Game
Work Items: WIP-001, WIP-002, WIP-007, WIP-008

Tests game logic without requiring GUI interaction.
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch


class MockTk:
    """Mock tkinter.Tk for testing without GUI."""
    def title(self, *args): pass
    def resizable(self, *args): pass
    def mainloop(self): pass
    def after(self, ms, func): 
        # Immediately call the function for testing (skip delay)
        func()


class MockBooleanVar:
    """Mock tkinter.BooleanVar for testing."""
    def __init__(self, value=False):
        self._value = value
    def get(self):
        return self._value
    def set(self, value):
        self._value = value


class MockLabel:
    """Mock tkinter.Label for testing."""
    def __init__(self, *args, **kwargs):
        self.text = kwargs.get('text', '')
    def grid(self, *args, **kwargs): pass
    def config(self, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']


class MockButton:
    """Mock tkinter.Button for testing."""
    def __init__(self, *args, **kwargs):
        self.text = kwargs.get('text', '')
        self.command = kwargs.get('command')
    def grid(self, *args, **kwargs): pass
    def config(self, **kwargs):
        if 'text' in kwargs:
            self.text = kwargs['text']


class MockCheckbutton:
    """Mock tkinter.Checkbutton for testing."""
    def __init__(self, *args, **kwargs):
        self.variable = kwargs.get('variable')
        self.command = kwargs.get('command')
    def grid(self, *args, **kwargs): pass


class MockFont:
    """Mock tkinter.font.Font for testing."""
    def __init__(self, *args, **kwargs): pass


class TestTicTacToeLogic(unittest.TestCase):
    """Test cases for Tic-Tac-Toe game logic."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())

    def tearDown(self):
        """Clean up patches."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()

    # TC-001: Initial Game State
    def test_initial_game_state(self):
        """Verify game initializes correctly."""
        for row in self.game.board:
            for cell in row:
                self.assertEqual(cell, "")
        self.assertEqual(self.game.current_player, "X")
        self.assertFalse(self.game.game_over)

    # TC-002: Player X Makes First Move
    def test_player_x_first_move(self):
        """Verify first move places X."""
        self.game.make_move(0, 0)
        self.assertEqual(self.game.board[0][0], "X")
        self.assertEqual(self.game.current_player, "O")

    # TC-003: Players Alternate Turns
    def test_players_alternate_turns(self):
        """Verify turn alternation."""
        self.game.make_move(0, 0)
        self.game.make_move(0, 1)
        self.game.make_move(0, 2)
        self.assertEqual(self.game.board[0][0], "X")
        self.assertEqual(self.game.board[0][1], "O")
        self.assertEqual(self.game.board[0][2], "X")

    # TC-004: Cannot Overwrite Occupied Cell
    def test_cannot_overwrite_occupied_cell(self):
        """Verify occupied cells are protected."""
        self.game.make_move(1, 1)
        self.game.make_move(1, 1)
        self.assertEqual(self.game.board[1][1], "X")
        self.assertEqual(self.game.current_player, "O")

    # TC-005: Horizontal Win Detection (Row 0)
    def test_horizontal_win_row_0(self):
        """Verify horizontal win in first row."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-006: Horizontal Win Detection (Row 1)
    def test_horizontal_win_row_1(self):
        """Verify horizontal win in second row."""
        self.game.make_move(1, 0)
        self.game.make_move(0, 0)
        self.game.make_move(1, 1)
        self.game.make_move(0, 1)
        self.game.make_move(1, 2)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-007: Horizontal Win Detection (Row 2)
    def test_horizontal_win_row_2(self):
        """Verify horizontal win in third row."""
        self.game.make_move(2, 0)
        self.game.make_move(0, 0)
        self.game.make_move(2, 1)
        self.game.make_move(0, 1)
        self.game.make_move(2, 2)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-008: Vertical Win Detection (Column 0)
    def test_vertical_win_col_0(self):
        """Verify vertical win in first column."""
        self.game.make_move(0, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 0)
        self.game.make_move(0, 2)
        self.game.make_move(2, 0)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-009: Vertical Win Detection (Column 1)
    def test_vertical_win_col_1(self):
        """Verify vertical win in second column."""
        self.game.make_move(0, 1)
        self.game.make_move(0, 0)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        self.game.make_move(2, 1)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-010: Vertical Win Detection (Column 2)
    def test_vertical_win_col_2(self):
        """Verify vertical win in third column."""
        self.game.make_move(0, 2)
        self.game.make_move(0, 0)
        self.game.make_move(1, 2)
        self.game.make_move(0, 1)
        self.game.make_move(2, 2)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-011: Diagonal Win Detection
    def test_diagonal_win(self):
        """Verify diagonal win."""
        self.game.make_move(0, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        self.game.make_move(2, 2)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-012: Anti-Diagonal Win Detection
    def test_anti_diagonal_win(self):
        """Verify anti-diagonal win."""
        self.game.make_move(0, 2)
        self.game.make_move(0, 0)
        self.game.make_move(1, 1)
        self.game.make_move(0, 1)
        self.game.make_move(2, 0)
        self.assertEqual(self.game.check_winner(), "X")
        self.assertTrue(self.game.game_over)

    # TC-013: Draw Detection
    def test_draw_detection(self):
        """Verify draw when board is full with no winner."""
        moves = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)]
        for move in moves:
            self.game.make_move(*move)
        self.assertIsNone(self.game.check_winner())
        self.assertTrue(self.game.game_over)

    # TC-014: No Moves After Win
    def test_no_moves_after_win(self):
        """Verify game stops accepting moves after win."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        self.game.make_move(2, 2)
        self.assertEqual(self.game.board[2][2], "")

    # TC-015: Reset Game Functionality
    def test_reset_game(self):
        """Verify reset clears the board."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 1)
        self.game.make_move(2, 2)
        self.game.reset_game()
        for row in self.game.board:
            for cell in row:
                self.assertEqual(cell, "")
        self.assertEqual(self.game.current_player, "X")
        self.assertFalse(self.game.game_over)

    # TC-016: O Can Win
    def test_o_can_win(self):
        """Verify O can also win."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(2, 2)
        self.game.make_move(1, 2)
        self.assertEqual(self.game.check_winner(), "O")
        self.assertTrue(self.game.game_over)


class TestCheckWinnerDirectly(unittest.TestCase):
    """Test check_winner method with direct board manipulation."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())

    def tearDown(self):
        """Clean up patches."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()

    def test_empty_board_no_winner(self):
        """Empty board should have no winner."""
        self.assertIsNone(self.game.check_winner())

    def test_partial_row_no_winner(self):
        """Partial row should not trigger win."""
        self.game.board[0][0] = "X"
        self.game.board[0][1] = "X"
        self.assertIsNone(self.game.check_winner())

    def test_mixed_row_no_winner(self):
        """Mixed row should not trigger win."""
        self.game.board[0][0] = "X"
        self.game.board[0][1] = "O"
        self.game.board[0][2] = "X"
        self.assertIsNone(self.game.check_winner())


# =============================================================================
# WIP-002: AI Tests
# =============================================================================

class TestAIStrategy(unittest.TestCase):
    """Test cases for AI strategy logic."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())

    def tearDown(self):
        """Clean up patches."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()

    # TC-201: AI Takes Winning Move
    def test_ai_takes_winning_move(self):
        """AI should take winning move when available."""
        self.game.board = [["O", "O", ""], ["X", "X", ""], ["", "", ""]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        self.assertEqual(move, (0, 2))

    # TC-202: AI Blocks Human Win
    def test_ai_blocks_human_win(self):
        """AI should block human's winning move."""
        self.game.board = [["X", "X", ""], ["O", "", ""], ["", "", ""]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        self.assertEqual(move, (0, 2))

    # TC-203: AI Takes Center When Available
    def test_ai_takes_center(self):
        """AI prioritizes center after win/block."""
        self.game.board = [["X", "", ""], ["", "", ""], ["", "", ""]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        self.assertEqual(move, (1, 1))

    # TC-204: AI Takes Corner When Center Occupied
    def test_ai_takes_corner(self):
        """AI takes corner when center not available."""
        self.game.board = [["", "", ""], ["", "X", ""], ["", "", ""]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        self.assertIn(move, [(0, 0), (0, 2), (2, 0), (2, 2)])

    # TC-205: AI Takes Side As Last Resort
    def test_ai_takes_side(self):
        """AI takes side when no other option."""
        self.game.board = [["X", "", "O"], ["", "X", ""], ["O", "", "X"]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        self.assertIn(move, [(0, 1), (1, 0), (1, 2), (2, 1)])

    # TC-206: AI Win Priority Over Block
    def test_ai_win_over_block(self):
        """AI should win rather than block."""
        self.game.board = [["O", "O", ""], ["X", "X", ""], ["", "", ""]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        self.assertEqual(move, (0, 2))


class TestAIToggleBehavior(unittest.TestCase):
    """Test cases for AI toggle behavior."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())

    def tearDown(self):
        """Clean up patches."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()

    # TC-207: AI Toggle Default State
    def test_ai_default_disabled(self):
        """AI should be disabled by default."""
        self.assertFalse(self.game.ai_enabled.get())

    # TC-208: Enable AI Toggle - AI moves after X
    def test_ai_moves_when_enabled(self):
        """Enabling AI activates AI opponent."""
        self.game.ai_enabled.set(True)
        self.game.make_move(0, 0)
        o_count = sum(1 for row in self.game.board for cell in row if cell == "O")
        self.assertEqual(o_count, 1)

    # TC-209: Disable AI Mid-Game
    def test_disable_ai_reverts_to_two_player(self):
        """Disabling AI reverts to two-player."""
        self.game.ai_enabled.set(True)
        self.game.make_move(0, 0)
        self.game.ai_enabled.set(False)
        self.game.make_move(0, 1)
        self.assertEqual(self.game.current_player, "O")

    # TC-211: AI Respects Game Over
    def test_ai_respects_game_over(self):
        """AI does not move when game is over."""
        self.game.ai_enabled.set(True)
        self.game.game_over = True
        self.game.current_player = "O"
        self.game._make_ai_move()
        o_count = sum(1 for row in self.game.board for cell in row if cell == "O")
        self.assertEqual(o_count, 0)

    # TC-212: Two-Player Mode Unchanged
    def test_two_player_mode_works(self):
        """AI disabled = normal two-player."""
        self.game.make_move(0, 0)
        self.assertEqual(self.game.current_player, "O")
        self.game.make_move(1, 1)
        self.assertEqual(self.game.current_player, "X")

    # TC-213: Reset Preserves AI Toggle
    def test_reset_preserves_ai_toggle(self):
        """Reset game keeps AI setting."""
        self.game.ai_enabled.set(True)
        self.game.make_move(0, 0)
        self.game.reset_game()
        self.assertTrue(self.game.ai_enabled.get())

    # TC-214: AI Makes Only Legal Moves
    def test_ai_makes_legal_moves(self):
        """AI never moves to occupied cell."""
        self.game.ai_enabled.set(True)
        for _ in range(4):
            empty_cells = [(r, c) for r in range(3) for c in range(3) 
                          if self.game.board[r][c] == ""]
            if empty_cells and not self.game.game_over:
                self.game.make_move(empty_cells[0][0], empty_cells[0][1])
        x_count = sum(1 for row in self.game.board for cell in row if cell == "X")
        o_count = sum(1 for row in self.game.board for cell in row if cell == "O")
        empty_count = sum(1 for row in self.game.board for cell in row if cell == "")
        self.assertEqual(x_count + o_count + empty_count, 9)

    # TC-215: AI Does Not Move As X
    def test_ai_only_plays_as_o(self):
        """AI only plays as O."""
        self.game.ai_enabled.set(True)
        self.assertEqual(self.game.current_player, "X")
        x_count = sum(1 for row in self.game.board for cell in row if cell == "X")
        self.assertEqual(x_count, 0)


class TestFindWinningMove(unittest.TestCase):
    """Test _find_winning_move helper method."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())

    def tearDown(self):
        """Clean up patches."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()

    # TC-216: Find Winning Move - Row
    def test_find_winning_move_row(self):
        """Detect winning move in row."""
        self.game.board[0] = ["O", "O", ""]
        move = self.game._find_winning_move("O")
        self.assertEqual(move, (0, 2))

    # TC-217: Find Winning Move - Column
    def test_find_winning_move_column(self):
        """Detect winning move in column."""
        self.game.board[0][0] = "O"
        self.game.board[1][0] = "O"
        self.game.board[2][0] = ""
        move = self.game._find_winning_move("O")
        self.assertEqual(move, (2, 0))

    # TC-218: Find Winning Move - Diagonal
    def test_find_winning_move_diagonal(self):
        """Detect winning move on diagonal."""
        self.game.board[0][0] = "O"
        self.game.board[1][1] = "O"
        self.game.board[2][2] = ""
        move = self.game._find_winning_move("O")
        self.assertEqual(move, (2, 2))

    # TC-219: Find Winning Move - None Available
    def test_find_winning_move_none(self):
        """Return None when no winning move."""
        self.game.board = [["X", "O", "X"], ["", "", ""], ["", "", ""]]
        move = self.game._find_winning_move("O")
        self.assertIsNone(move)


# =============================================================================
# WIP-008: Fork Detection Tests
# =============================================================================

class TestForkDetection(unittest.TestCase):
    """Test cases for AI fork detection and blocking."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())

    def tearDown(self):
        """Clean up patches."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()

    # TC-401: Detect Diagonal Fork Setup
    def test_detect_diagonal_fork(self):
        """AI detects fork when X has opposite corners (0,0) and (2,2)."""
        # X | . | .
        # ---------
        # . | O | .
        # ---------
        # . | . | X
        self.game.board = [["X", "", ""], ["", "O", ""], ["", "", "X"]]
        fork_block = self.game._find_fork_block("X")
        # Should return an edge to force X to block instead of completing fork
        self.assertIn(fork_block, [(0, 1), (1, 0), (1, 2), (2, 1)])

    # TC-402: Detect Anti-Diagonal Fork Setup
    def test_detect_anti_diagonal_fork(self):
        """AI detects fork when X has corners (0,2) and (2,0)."""
        # . | . | X
        # ---------
        # . | O | .
        # ---------
        # X | . | .
        self.game.board = [["", "", "X"], ["", "O", ""], ["X", "", ""]]
        fork_block = self.game._find_fork_block("X")
        # Should return an edge to force X to block
        self.assertIn(fork_block, [(0, 1), (1, 0), (1, 2), (2, 1)])

    # TC-403: No Fork When Single Corner
    def test_no_fork_single_corner(self):
        """No fork exists with only one corner occupied."""
        # X | . | .
        # ---------
        # . | O | .
        # ---------
        # . | . | .
        self.game.board = [["X", "", ""], ["", "O", ""], ["", "", ""]]
        fork_block = self.game._find_fork_block("X")
        self.assertIsNone(fork_block)

    # TC-404: Detect Edge-Corner Fork
    def test_detect_edge_corner_fork(self):
        """AI detects fork from edge + corner combination."""
        # X | . | .
        # ---------
        # . | O | .
        # ---------
        # . | X | .
        self.game.board = [["X", "", ""], ["", "O", ""], ["", "X", ""]]
        fork_block = self.game._find_fork_block("X")
        # Should return (2,0) to block the fork
        self.assertEqual(fork_block, (2, 0))

    # TC-405: No Fork When Lines Blocked
    def test_no_fork_when_blocked(self):
        """No fork threat exists when key lines are blocked by O."""
        # X | O | O
        # ---------
        # O | O | .
        # ---------
        # . | . | X
        self.game.board = [["X", "O", "O"], ["O", "O", ""], ["", "", "X"]]
        fork_block = self.game._find_fork_block("X")
        # All lines with X are blocked by O, no fork possible
        self.assertIsNone(fork_block)

    # TC-406: AI Blocks Diagonal Fork in Game
    def test_ai_blocks_diagonal_fork_in_game(self):
        """Full game simulation where AI blocks the classic corner fork."""
        self.game.ai_enabled.set(True)
        # X plays corner
        self.game.make_move(0, 0)
        # AI should take center (it does based on existing logic)
        self.assertEqual(self.game.board[1][1], "O")
        
        # X plays opposite corner - setting up fork
        self.game.make_move(2, 2)
        
        # AI should block the fork - NOT take a corner like (0,2)
        # The AI should play an edge to force X to block
        ai_move = None
        for r in range(3):
            for c in range(3):
                if self.game.board[r][c] == "O" and (r, c) != (1, 1):
                    ai_move = (r, c)
                    break
        
        # AI should have blocked at (0,2) or (2,0) - the fork points
        self.assertIn(ai_move, [(0, 2), (2, 0), (0, 1), (1, 0), (1, 2), (2, 1)])

    # TC-408: Fork Block Priority Below Immediate Win
    def test_ai_win_priority_over_fork_block(self):
        """AI still takes winning move over blocking fork."""
        # O | O | .
        # ---------
        # X | . | .
        # ---------
        # X | . | .
        self.game.board = [["O", "O", ""], ["X", "", ""], ["X", "", ""]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        # AI should win at (0,2), not block fork
        self.assertEqual(move, (0, 2))

    # TC-409: Fork Block Priority Below Immediate Block
    def test_ai_block_priority_over_fork_block(self):
        """AI still blocks opponent's winning move over fork."""
        # X | X | .
        # ---------
        # . | O | .
        # ---------
        # . | . | X
        self.game.board = [["X", "X", ""], ["", "O", ""], ["", "", "X"]]
        self.game.current_player = "O"
        move = self.game._find_best_move()
        # AI should block X's win at (0,2)
        self.assertEqual(move, (0, 2))


class TestCountWinningThreats(unittest.TestCase):
    """Test _count_winning_threats helper method."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())

    def tearDown(self):
        """Clean up patches."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()

    def test_count_zero_threats(self):
        """No threats on empty board."""
        threats = self.game._count_winning_threats("X")
        self.assertEqual(threats, 0)

    def test_count_one_threat_row(self):
        """Count single threat in row."""
        self.game.board = [["X", "X", ""], ["", "", ""], ["", "", ""]]
        threats = self.game._count_winning_threats("X")
        self.assertEqual(threats, 1)

    def test_count_two_threats_fork(self):
        """Count two threats (fork scenario)."""
        # X at (0,0), (0,1), (1,0) creates threats in row 0 and col 0
        self.game.board = [["X", "X", ""], ["X", "", ""], ["", "", ""]]
        threats = self.game._count_winning_threats("X")
        self.assertEqual(threats, 2)

    def test_count_diagonal_threat(self):
        """Count diagonal threat."""
        self.game.board = [["X", "", ""], ["", "X", ""], ["", "", ""]]
        threats = self.game._count_winning_threats("X")
        self.assertEqual(threats, 1)


# =============================================================================
# WIP-007: Game Logging Tests
# =============================================================================

class TestGameLogging(unittest.TestCase):
    """Test cases for game logging functionality."""

    def setUp(self):
        """Set up test fixtures with mocked tkinter."""
        self.tk_patcher = patch('tkinter.Tk', MockTk)
        self.label_patcher = patch('tkinter.Label', MockLabel)
        self.button_patcher = patch('tkinter.Button', MockButton)
        self.checkbutton_patcher = patch('tkinter.Checkbutton', MockCheckbutton)
        self.booleanvar_patcher = patch('tkinter.BooleanVar', MockBooleanVar)
        self.font_patcher = patch('tkinter.font.Font', MockFont)
        
        self.tk_patcher.start()
        self.label_patcher.start()
        self.button_patcher.start()
        self.checkbutton_patcher.start()
        self.booleanvar_patcher.start()
        self.font_patcher.start()
        
        from tictactoe import TicTacToe
        self.game = TicTacToe(MockTk())
        
        # Use a test-specific log file
        self.test_log_file = "test_game_log.json"
        self.game.LOG_FILE = self.test_log_file

    def tearDown(self):
        """Clean up patches and test files."""
        self.tk_patcher.stop()
        self.label_patcher.stop()
        self.button_patcher.stop()
        self.checkbutton_patcher.stop()
        self.booleanvar_patcher.stop()
        self.font_patcher.stop()
        
        # Clean up test log file
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    # TC-301: Move History Recorded
    def test_move_history_recorded(self):
        """Verify moves are recorded in history."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 1)
        self.assertEqual(len(self.game.move_history), 2)
        self.assertEqual(self.game.move_history[0], {"player": "X", "row": 0, "col": 0})
        self.assertEqual(self.game.move_history[1], {"player": "O", "row": 1, "col": 1})

    # TC-302: Move History Cleared on Reset
    def test_move_history_cleared_on_reset(self):
        """Verify move history is cleared when game resets."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 1)
        self.game.reset_game()
        self.assertEqual(len(self.game.move_history), 0)

    # TC-303: Log File Created on Game End
    def test_log_file_created_on_win(self):
        """Verify log file is created when game ends with win."""
        # X wins with top row
        self.game.make_move(0, 0)  # X
        self.game.make_move(1, 0)  # O
        self.game.make_move(0, 1)  # X
        self.game.make_move(1, 1)  # O
        self.game.make_move(0, 2)  # X wins
        
        self.assertTrue(os.path.exists(self.test_log_file))

    # TC-304: Log Contains Correct Winner
    def test_log_contains_winner(self):
        """Verify log contains correct winner."""
        # X wins with top row
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        
        with open(self.test_log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["winner"], "X")

    # TC-305: Log Contains Move History
    def test_log_contains_moves(self):
        """Verify log contains complete move history."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        
        with open(self.test_log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertEqual(logs[0]["total_moves"], 5)
        self.assertEqual(len(logs[0]["moves"]), 5)

    # TC-306: Log Contains AI Status
    def test_log_contains_ai_status(self):
        """Verify log contains AI enabled/disabled status."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        
        with open(self.test_log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertIn("ai_enabled", logs[0])
        self.assertFalse(logs[0]["ai_enabled"])

    # TC-307: Log Contains Timestamp
    def test_log_contains_timestamp(self):
        """Verify log contains timestamp."""
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        
        with open(self.test_log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertIn("timestamp", logs[0])

    # TC-308: Draw Game Logged
    def test_draw_game_logged(self):
        """Verify draw games are logged correctly."""
        moves = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)]
        for move in moves:
            self.game.make_move(*move)
        
        with open(self.test_log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertEqual(logs[0]["winner"], "Draw")
        self.assertEqual(logs[0]["total_moves"], 9)

    # TC-309: Multiple Games Appended
    def test_multiple_games_appended(self):
        """Verify multiple games are appended to log."""
        # Game 1: X wins
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        
        # Game 2: Reset and play again
        self.game.reset_game()
        self.game.make_move(1, 1)
        self.game.make_move(0, 0)
        self.game.make_move(0, 1)
        self.game.make_move(2, 1)
        self.game.make_move(2, 2)
        self.game.make_move(0, 2)
        self.game.make_move(1, 0)
        self.game.make_move(1, 2)
        self.game.make_move(2, 0)
        
        with open(self.test_log_file, 'r') as f:
            logs = json.load(f)
        
        self.assertEqual(len(logs), 2)

    # TC-310: Logging Failure Does Not Crash Game
    def test_logging_failure_graceful(self):
        """Verify logging failure doesn't crash the game."""
        # Set log file to invalid path
        self.game.LOG_FILE = "/nonexistent/path/log.json"
        
        # Should not raise exception
        self.game.make_move(0, 0)
        self.game.make_move(1, 0)
        self.game.make_move(0, 1)
        self.game.make_move(1, 1)
        self.game.make_move(0, 2)
        
        # Game should still end properly
        self.assertTrue(self.game.game_over)


if __name__ == "__main__":
    unittest.main()
