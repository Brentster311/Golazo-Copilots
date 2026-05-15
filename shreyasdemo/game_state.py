from dataclasses import dataclass, field


WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def check_winner(board: list[str]) -> str | None:
    for first, second, third in WINNING_LINES:
        mark = board[first]
        if mark and mark == board[second] and mark == board[third]:
            return mark
    return None


def is_draw(board: list[str]) -> bool:
    return "" not in board and check_winner(board) is None


@dataclass
class SessionStats:
    games_played: int = 0
    x_wins: int = 0
    o_wins: int = 0
    draws: int = 0


@dataclass
class GameState:
    board: list[str] = field(default_factory=lambda: [""] * 9)
    current_player: str = "X"
    status: str = "IN_PROGRESS"
    locked: bool = False

    def apply_move(self, index: int, stats: SessionStats | None = None) -> bool:
        if self.locked:
            return False
        if not isinstance(index, int) or index < 0 or index >= 9:
            return False
        if self.board[index] != "":
            return False

        self.board[index] = self.current_player

        winner = check_winner(self.board)
        if winner == "X":
            self.status = "X_WON"
            self.locked = True
            if stats is not None:
                stats.games_played += 1
                stats.x_wins += 1
            return True

        if winner == "O":
            self.status = "O_WON"
            self.locked = True
            if stats is not None:
                stats.games_played += 1
                stats.o_wins += 1
            return True

        if is_draw(self.board):
            self.status = "DRAW"
            self.locked = True
            if stats is not None:
                stats.games_played += 1
                stats.draws += 1
            return True

        self.current_player = "O" if self.current_player == "X" else "X"
        self.status = "IN_PROGRESS"
        return True

    def restart_game(self) -> None:
        self.board = [""] * 9
        self.current_player = "X"
        self.status = "IN_PROGRESS"
        self.locked = False