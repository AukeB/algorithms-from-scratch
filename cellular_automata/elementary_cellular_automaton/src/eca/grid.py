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
        self.initialization_mode = config.game.initialization_mode
        self.boundary_mode = config.game.boundary_mode
        self.rule_set = config.game.rule_set

        self.grid: list[list[int]] = [
            [0 for _ in range(self.dimensions.cols)]
            for _ in range(self.dimensions.rows)
        ]

        self.iteration: int = 0

    def set_cell(self, position: Position, value: int) -> None:
        """Sets the state of the cell at the given position.

        Args:
            position (Position): x/y coordinate to write, where x maps to the
                column and y maps to the row.
            value (int): The new state to store at that position.
        """
        self.grid[position.y][position.x] = value

    def initialize(self) -> None:
        """Initialize the cells in the grid based on the grid mode config."""
        if self.initialization_mode == "single_alive_cell":
            self.set_cell(position=Position(x=self.dimensions.cols // 2, y=0), value=1)
        elif self.initialization_mode == "single_dead_cell":
            for x in range(self.dimensions.cols):
                self.set_cell(position=Position(x=x, y=0), value=1)
            self.set_cell(position=Position(x=self.dimensions.cols // 2, y=0), value=0)
        elif self.initialization_mode == "random":
            for x in range(self.dimensions.cols):
                self.set_cell(
                    position=Position(x=x, y=0),
                    value=rd.randint(0, 1),
                )

    @staticmethod
    def _get_padded_row(row: list[int], boundary_mode: str) -> list[int]:
        """Returns a row padded according to the specified boundary mode.

        Args:
            row (list[int]): The current row of cell states.
            boundary_mode (str): Boundary condition to apply. Supported modes
                are "zero", "periodic", and "reflective".

        Returns:
            list[int]: The row with one boundary cell added to each side.

        Raises:
            ValueError: If the boundary mode is not supported.
        """
        padded_row: list[int]

        if boundary_mode == "zero":
            padded_row = [0] + row + [0]
        elif boundary_mode == "periodic":
            padded_row = [row[-1]] + row + [row[0]]
        elif boundary_mode == "reflective":
            padded_row = [row[0]] + row + [row[-1]]

        return padded_row

    def propagate(self) -> None:
        """Generates the next grid row from the current row using the rule set.

        Each cell's next state is determined by its three-cell neighborhood
        (left, center, right) and the configured elementary cellular automaton
        rule. The resulting row is stored at the next iteration.
        """
        next_iteration = []

        padded_row = self._get_padded_row(
            row=self.grid[self.iteration], boundary_mode=self.boundary_mode
        )

        for left, center, right in zip(padded_row, padded_row[1:], padded_row[2:]):
            neighborhood = (left << 2) | (center << 1) | right
            next_value = (self.rule_set >> neighborhood) & 1
            next_iteration.append(next_value)

        self.iteration += 1

        self.grid[self.iteration] = next_iteration
