"""Module for the 2D grid data structure used in cellular automata and grid
visualizations.
"""

import random as rd

from src.eca.config_model import ConfigModel
from src.eca.constants import Dimensions


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

    def initialize(self) -> None:
        """Initialize the cells in the grid based on initialization_mode config."""
        if self.initialization_mode == "single_alive_cell":
            row = [0] * self.dimensions.cols
            row[self.dimensions.cols // 2] = 1
        elif self.initialization_mode == "single_dead_cell":
            row = [1] * self.dimensions.cols
            row[self.dimensions.cols // 2] = 0
        elif self.initialization_mode == "random":
            row = [rd.randint(0, 1) for _ in range(self.dimensions.cols)]

        self.grid[0] = row

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
        next_row = []

        padded_row = self._get_padded_row(
            row=self.grid[self.iteration], boundary_mode=self.boundary_mode
        )

        for left, center, right in zip(padded_row, padded_row[1:], padded_row[2:]):
            neighborhood = (left << 2) | (center << 1) | right
            next_value = (self.rule_set >> neighborhood) & 1
            next_row.append(next_value)

        self.iteration += 1

        self.grid[self.iteration] = next_row
