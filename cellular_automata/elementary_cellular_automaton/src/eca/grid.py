"""Module for the 2D grid data structure used in cellular automata and grid
visualizations.
"""

import random as rd

from src.eca.config_model import ConfigModel
from src.eca.constants import Dimensions, Position


class Grid:
    """Holds and manipulates a 2D grid of cell states."""

    def __init__(self, config: ConfigModel) -> None:
        """Initializes an empty square grid filled with a constant value.

        Args:
            config (ConfigModel): Pydantic-validated configuration model.
        """
        self.dimensions = Dimensions(rows=config.grid.dim, cols=config.grid.dim)

        self.cells: list[list[int]] = [
            [0 for _ in range(self.dimensions.cols)]
            for _ in range(self.dimensions.rows)
        ]

    def set_cell(self, position: Position, value: int) -> None:
        """Sets the state of the cell at the given position.

        Args:
            position (Position): x/y coordinate to write, where x maps to the
                column and y maps to the row.
            value (int): The new state to store at that position.
        """
        self.cells[position.y][position.x] = value

    def randomize(self, values: list[int] | None = None) -> None:
        """Fills the grid with random values drawn from the given options.

        Args:
            values (list[int]): Pool of possible cell states to sample from.
                Defaults to `[0, 1]`.
        """
        values = values or [0, 1]

        for row in range(self.dimensions.rows):
            for col in range(self.dimensions.cols):
                self.cells[row][col] = rd.choice(values)
