import tkinter as tk
from tkinter import messagebox

from game_state import GameState, SessionStats


class TicTacToeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.root.resizable(False, False)

        self.game = GameState()
        self.stats = SessionStats()

        self.status_var = tk.StringVar(value="Turn: X")
        self.stats_var = tk.StringVar(value=self._stats_text())

        status_label = tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 12, "bold"))
        status_label.grid(row=0, column=0, columnspan=3, padx=8, pady=(8, 4), sticky="w")

        self.buttons: list[tk.Button] = []
        for index in range(9):
            button = tk.Button(
                root,
                text="",
                width=6,
                height=3,
                font=("Segoe UI", 16, "bold"),
                command=lambda i=index: self._on_cell_click(i),
            )
            button.grid(row=1 + index // 3, column=index % 3, padx=4, pady=4)
            self.buttons.append(button)

        restart_button = tk.Button(root, text="Restart", command=self._on_restart)
        restart_button.grid(row=4, column=0, columnspan=3, pady=(6, 2))

        stats_label = tk.Label(root, textvariable=self.stats_var, font=("Segoe UI", 10))
        stats_label.grid(row=5, column=0, columnspan=3, padx=8, pady=(2, 8), sticky="w")

    def _on_cell_click(self, index: int) -> None:
        try:
            changed = self.game.apply_move(index, self.stats)
            if not changed:
                return

            self._refresh_board()
            self._refresh_status()
            self.stats_var.set(self._stats_text())
        except Exception as error:
            messagebox.showerror("Error", f"Unexpected error: {error}")

    def _on_restart(self) -> None:
        self.game.restart_game()
        self._refresh_board()
        self._refresh_status()
        self.stats_var.set(self._stats_text())

    def _refresh_board(self) -> None:
        for index, button in enumerate(self.buttons):
            button.config(text=self.game.board[index])

    def _refresh_status(self) -> None:
        if self.game.status == "X_WON":
            self.status_var.set("Winner: X")
            return
        if self.game.status == "O_WON":
            self.status_var.set("Winner: O")
            return
        if self.game.status == "DRAW":
            self.status_var.set("Draw")
            return
        self.status_var.set(f"Turn: {self.game.current_player}")

    def _stats_text(self) -> str:
        return (
            f"Games: {self.stats.games_played}   "
            f"X Wins: {self.stats.x_wins}   "
            f"O Wins: {self.stats.o_wins}   "
            f"Draws: {self.stats.draws}"
        )


def main() -> None:
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()