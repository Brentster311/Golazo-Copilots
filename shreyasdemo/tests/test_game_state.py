import unittest

from game_state import GameState, SessionStats, check_winner, is_draw


class GameStateTests(unittest.TestCase):
    def test_initial_state(self):
        game = GameState()

        self.assertEqual(game.board, [""] * 9)
        self.assertEqual(game.current_player, "X")
        self.assertEqual(game.status, "IN_PROGRESS")
        self.assertFalse(game.locked)

    def test_valid_move_places_mark_and_toggles_turn(self):
        game = GameState()

        changed = game.apply_move(0)

        self.assertTrue(changed)
        self.assertEqual(game.board[0], "X")
        self.assertEqual(game.current_player, "O")
        self.assertEqual(game.status, "IN_PROGRESS")

    def test_occupied_cell_move_is_rejected_without_turn_change(self):
        game = GameState()
        game.apply_move(0)

        changed = game.apply_move(0)

        self.assertFalse(changed)
        self.assertEqual(game.board[0], "X")
        self.assertEqual(game.current_player, "O")
        self.assertEqual(game.status, "IN_PROGRESS")

    def test_invalid_indices_are_ignored_without_exception_or_state_change(self):
        game = GameState()
        original_board = game.board.copy()

        self.assertFalse(game.apply_move(-1))
        self.assertFalse(game.apply_move(9))
        self.assertFalse(game.apply_move("bad"))

        self.assertEqual(game.board, original_board)
        self.assertEqual(game.current_player, "X")
        self.assertEqual(game.status, "IN_PROGRESS")

    def test_check_winner_detects_all_winning_lines_for_both_players(self):
        winning_lines = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for player in ("X", "O"):
            for a, b, c in winning_lines:
                board = [""] * 9
                board[a] = player
                board[b] = player
                board[c] = player
                self.assertEqual(check_winner(board), player)

    def test_detects_x_win_and_locks_board_and_updates_stats(self):
        game = GameState()
        stats = SessionStats()

        game.apply_move(0, stats)
        game.apply_move(3, stats)
        game.apply_move(1, stats)
        game.apply_move(4, stats)
        game.apply_move(2, stats)

        self.assertEqual(game.status, "X_WON")
        self.assertTrue(game.locked)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.x_wins, 1)
        self.assertEqual(stats.o_wins, 0)
        self.assertEqual(stats.draws, 0)

    def test_draw_detection(self):
        board = [
            "X",
            "O",
            "X",
            "X",
            "O",
            "O",
            "O",
            "X",
            "X",
        ]
        self.assertTrue(is_draw(board))
        self.assertIsNone(check_winner(board))

    def test_detects_draw_and_locks_board_and_updates_stats(self):
        game = GameState()
        stats = SessionStats()

        sequence = [0, 1, 2, 4, 3, 5, 7, 6, 8]
        for move in sequence:
            game.apply_move(move, stats)

        self.assertEqual(game.status, "DRAW")
        self.assertTrue(game.locked)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.x_wins, 0)
        self.assertEqual(stats.o_wins, 0)
        self.assertEqual(stats.draws, 1)

    def test_post_terminal_move_attempts_are_blocked(self):
        game = GameState()
        stats = SessionStats()

        game.apply_move(0, stats)
        game.apply_move(3, stats)
        game.apply_move(1, stats)
        game.apply_move(4, stats)
        game.apply_move(2, stats)

        board_after_win = game.board.copy()
        self.assertFalse(game.apply_move(8, stats))
        self.assertEqual(game.board, board_after_win)
        self.assertEqual(game.status, "X_WON")
        self.assertEqual(stats.games_played, 1)

    def test_restart_resets_game_state_but_preserves_stats(self):
        game = GameState()
        stats = SessionStats()

        game.apply_move(0, stats)
        game.apply_move(3, stats)
        game.apply_move(1, stats)
        game.apply_move(4, stats)
        game.apply_move(2, stats)

        self.assertEqual(stats.x_wins, 1)
        game.restart_game()

        self.assertEqual(game.board, [""] * 9)
        self.assertEqual(game.current_player, "X")
        self.assertEqual(game.status, "IN_PROGRESS")
        self.assertFalse(game.locked)
        self.assertEqual(stats.games_played, 1)
        self.assertEqual(stats.x_wins, 1)
        self.assertEqual(stats.o_wins, 0)
        self.assertEqual(stats.draws, 0)


if __name__ == "__main__":
    unittest.main()