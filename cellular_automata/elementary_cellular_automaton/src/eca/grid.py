"""Module for the 2D grid data structure used in cellular automata and grid
visualizations.
"""

import random as rd

from eca.config.config_model import ConfigModel
from eca.constants import Dimensions
from eca.errors import UnsupportedBoundaryModeError, UnsupportedInitializationModeError


class Grid:
    """Holds and manipulates a 2D grid of cell states.

    Attributes:
        dimensions (Dimensions): Number of rows and columns of the grid.
        grid (list[list[int]]): Cell states, one inner list per row.
        _initialization_mode (str): How the first row is generated.
        _boundary_mode (str): How propagation is handled at the grid edges.
        _rule_set (int): Elementary cellular automaton rule number.
        _iteration (int): Index of the most recently generated row.
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initializes an empty square grid filled with a constant value.

        Args:
            config (ConfigModel): Pydantic-validated configuration model.
        """
        self.dimensions: Dimensions = Dimensions(
            rows=config.grid.dim, cols=config.grid.dim
        )

        self._initialization_mode: str = config.game.initialization_mode
        self._boundary_mode: str = config.game.boundary_mode
        self._rule_set: int = config.game.rule_set

        self.grid: list[list[int]] = [
            [0 for _ in range(self.dimensions.cols)]
            for _ in range(self.dimensions.rows)
        ]

        self._iteration: int = 0

    @staticmethod
    def _get_padded_row(row: list[int], boundary_mode: str) -> list[int]:
        """Returns a row padded according to the specified boundary mode.

        Args:
            row (list[int]): The current row of cell states.
            boundary_mode (str): Boundary condition to apply. Supported modes
                are "zero", "periodic", and "reflective".

        Returns:
            padded_row (list[int]): The row with one boundary cell added to each
                side.

        Raises:
            UnsupportedBoundaryModeError: If the boundary mode is not supported.
        """
        if boundary_mode == "zero":
            padded_row = [0] + row + [0]
        elif boundary_mode == "periodic":
            padded_row = [row[-1]] + row + [row[0]]
        elif boundary_mode == "reflective":
            padded_row = [row[0]] + row + [row[-1]]
        else:
            raise UnsupportedBoundaryModeError(
                f"Unsupported boundary mode: {boundary_mode!r}."
            )

        return padded_row

    def initialize(self) -> None:
        """Initializes the cells in the first row based on the initialization
        mode.

        Raises:
            UnsupportedInitializationModeError: If the initialization mode is
                not supported.
        """
        if self._initialization_mode == "single_alive_cell":
            row = [0] * self.dimensions.cols
            row[self.dimensions.cols // 2] = 1
        elif self._initialization_mode == "single_dead_cell":
            row = [1] * self.dimensions.cols
            row[self.dimensions.cols // 2] = 0
        elif self._initialization_mode == "random":
            row = [rd.randint(0, 1) for _ in range(self.dimensions.cols)]
        else:
            raise UnsupportedInitializationModeError(
                f"Unsupported initialization mode: {self._initialization_mode!r}."
            )

        self.grid[0] = row

    @property
    def is_full(self) -> bool:
        """Whether every row of the grid has been generated.

        Returns:
            is_full (bool): True once the last row has been generated.
        """
        is_full = self._iteration >= self.dimensions.rows - 1

        return is_full

    def propagate(self) -> None:
        """Generates the next grid row from the current row using the rule set.

        Each cell's next state is determined by its three-cell neighborhood
        (left, center, right) and the configured elementary cellular automaton
        rule. The resulting row is stored at the next iteration.
        """
        current_row = self.grid[self._iteration]

        padded_row = self._get_padded_row(
            row=current_row, boundary_mode=self._boundary_mode
        )

        next_row: list[int] = []

        for left, center, right in zip(padded_row, padded_row[1:], padded_row[2:]):
            neighborhood = (left << 2) | (center << 1) | right
            next_value = (self._rule_set >> neighborhood) & 1
            next_row.append(next_value)

        self._iteration += 1

        self.grid[self._iteration] = next_row
