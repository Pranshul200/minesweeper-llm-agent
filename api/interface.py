# api/interface.py

from minesweeper.engine import Minesweeper

class MinesweeperAPI:
    """
    Simple API wrapper for the Minesweeper engine.

    Provides:
    - current visible board
    - action interface: reveal, flag, unflag
    - terminal status & score
    """

    def __init__(self, rows: int = 5, cols: int = 5, num_mines: int = 3, seed: int = 42):
        print(f"Initializing MinesweeperAPI with {rows} rows, {cols} cols, {num_mines} mines, seed={seed}")
        self.game = Minesweeper(rows, cols, num_mines, seed)

    def get_board(self) -> str:
        """Returns the current visible board as a text string."""
        return self.game.render()

    def perform_action(self, action: str, row: int, col: int) -> str:
        """Performs a validated action on the board."""
        if self.game.is_terminal():
            return "Game is already over."

        # Validate coordinates
        if not (0 <= row < self.game.rows and 0 <= col < self.game.cols):
            return f"Invalid coordinates: ({row}, {col})"

        if action == "reveal":
            self.game.reveal(row, col)
        elif action == "flag":
            self.game.flag(row, col)
        else:
            return "Invalid action."

        return self.game.render()

        
 

    def is_game_over(self) -> bool:
        """Returns whether the game has ended."""
        return self.game.is_terminal()

    def get_score(self) -> dict:
        """Returns win/loss, number of safe tiles revealed, and number of steps taken."""
        won, revealed, steps = self.game.get_score()
        return {
            "won": won,
            "revealed": revealed,
            "steps": steps
        }
