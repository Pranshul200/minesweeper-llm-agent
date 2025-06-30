import random
from typing import List, Tuple

class Tile:
    def __init__(self):
        self.has_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

    def __str__(self):
        if self.is_flagged:
            return 'F'
        if not self.is_revealed:
            return '?'
        if self.has_mine:
            return '*'
        return str(self.adjacent_mines)

class Minesweeper:
    def __init__(self, rows: int, cols: int, num_mines: int, seed: int = 42):
        self.rows = rows
        self.cols = cols
        self.num_mines = num_mines
        self.seed = seed
        self.board = [[Tile() for _ in range(cols)] for _ in range(rows)]
        self.revealed_tiles = 0
        self.total_safe_tiles = rows * cols - num_mines
        self.terminated = False
        self.won = False
        self.first_move = True

    def _get_neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        return [
            (r + dr, c + dc)
            for dr, dc in directions
            if 0 <= r + dr < self.rows and 0 <= c + dc < self.cols
        ]

    def _place_mines_avoiding(self, safe_r: int, safe_c: int):
        random.seed(self.seed)
        forbidden = set(self._get_neighbors(safe_r, safe_c))
        forbidden.add((safe_r, safe_c))
        all_positions = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        candidates = [pos for pos in all_positions if pos not in forbidden]
        mine_positions = random.sample(candidates, self.num_mines)
        for r, c in mine_positions:
            self.board[r][c].has_mine = True

    def _compute_adjacent_counts(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.board[r][c].has_mine:
                    self.board[r][c].adjacent_mines = sum(
                        self.board[nr][nc].has_mine
                        for nr, nc in self._get_neighbors(r, c)
                    )

    def reveal(self, r: int, c: int):
        if self.terminated or self.board[r][c].is_revealed or self.board[r][c].is_flagged:
            return

        if self.first_move:
            if self.seed is None:
                self.seed = random.randint(0, 99999)

            random.seed(self.seed)
            self._place_mines_avoiding(r, c)
            self._compute_adjacent_counts()
            self.first_move = False

        if self.board[r][c].has_mine:
            self.terminated = True
            self.won = False
            self.board[r][c].is_revealed = True
            return

        self._flood_fill(r, c)

        if self.revealed_tiles == self.total_safe_tiles:
            self.terminated = True
            self.won = True

    def _flood_fill(self, r: int, c: int):
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            tile = self.board[cr][cc]
            if tile.is_revealed or tile.is_flagged:
                continue
            tile.is_revealed = True
            self.revealed_tiles += 1
            if tile.adjacent_mines == 0:
                for nr, nc in self._get_neighbors(cr, cc):
                    stack.append((nr, nc))

    def flag(self, r: int, c: int):
        if self.terminated or self.board[r][c].is_revealed:
            return
        self.board[r][c].is_flagged = not self.board[r][c].is_flagged

    def is_terminal(self) -> bool:
        return self.terminated

    def get_score(self) -> Tuple[bool, int, int]:
        return self.won, self.revealed_tiles, sum(
            1 for row in self.board for tile in row if tile.is_revealed or tile.is_flagged
        )

    def render(self) -> str:
        return '\n'.join(
            ' '.join(str(tile) for tile in row) for row in self.board
        )
