"""Module for the 2D grid data structure used in cellular automata and grid
visualizations.
"""

import random as rd

from src.voronoi_diagram.config_model import ConfigModel
from src.voronoi_diagram.constants import Dimensions, Position


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

        # Voronoi seed points stored as grid coordinates.
        self.seed_points: list[Position] = []

    def generate_seed_points(self, num_seeds: int) -> None:
        """Generates random seed points uniformly distributed across the grid.

        Each seed point is positioned at the center of its grid cell. Seed
        points are expressed as continuous coordinates (column + 0.5, row +
        0.5).

        Args:
            num_seeds (int): Number of seed points to generate.
        """
        self.seed_points = [
            Position(
                x=rd.randint(0, self.dimensions.cols - 1) + 0.5,
                y=rd.randint(0, self.dimensions.rows - 1) + 0.5,
            )
            for _ in range(num_seeds)
        ]

    def _find_closest_seed(self, point: Position) -> int:
        """Finds the index of the closest seed point to the given point.

        Args:
            point (Position): The point to measure from.

        Returns:
            closest_idx (int): Index of the closest seed point.
        """
        min_distance_squared = float("inf")
        closest_idx = 0

        for idx, seed in enumerate(self.seed_points):
            distance_squared = (point.x - seed.x) ** 2 + (point.y - seed.y) ** 2
            if distance_squared < min_distance_squared:
                min_distance_squared = distance_squared
                closest_idx = idx

        return closest_idx

    def generate_voronoi_diagram(self) -> None:
        """Assigns each grid cell to its closest seed point.

        Iterates over all grid cells, calculates the distance to each seed
        point, and assigns the cell to the closest seed point's region.
        """
        for row in range(self.dimensions.rows):
            for col in range(self.dimensions.cols):
                cell_center = Position(x=col + 0.5, y=row + 0.5)
                closest_seed_idx = self._find_closest_seed(cell_center)
                self.cells[row][col] = closest_seed_idx
