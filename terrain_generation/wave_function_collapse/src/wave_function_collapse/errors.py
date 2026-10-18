"""Module for custom exceptions raised by the Wave Function Collapse algorithm."""


class ContradictionError(RuntimeError):
    """Raised when a grid cell is left with no tile that fits its neighbors."""

    def __init__(self, row: int, col: int) -> None:
        """Record the position of the cell that has no valid tile.

        Args:
            row (int): Row of the cell in the grid.
            col (int): Column of the cell in the grid.
        """
        super().__init__(f"No valid tile for the grid cell at row {row}, column {col}.")
        self.row = row
        self.col = col
