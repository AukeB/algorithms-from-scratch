"""Module for the grid that holds the Voronoi diagram: its cells and seed points."""

import random

from voronoi_diagram.config_model import ConfigModel
from voronoi_diagram.constants import Dimensions, Position


class Grid:
    """Hold the grid cells, and assign each cell to the region of its nearest seed
    point.

    Attributes:
        dimensions (Dimensions): Number of rows and columns of the grid.
        cells (list[list[int]]): Index of the owning seed point for each cell.
        seed_points (list[Position]): Seed point positions, in grid coordinates.
        rng (random.Random): Random generator used to place the seed points.

    Example:
        >>> grid = Grid(config=ConfigManager().load_config_file())
        >>> grid.generate_seed_points(num_seeds=20)
        >>> grid.generate_voronoi_diagram()
    """

    def __init__(self, config: ConfigModel, rng: random.Random | None = None) -> None:
        """Initialize an empty square grid.

        Args:
            config (ConfigModel): The validated configuration model.
            rng (random.Random | None): Random generator for the seed points. Defaults
                to a new, unseeded generator.
        """
        self.dimensions = Dimensions(rows=config.grid.dim, cols=config.grid.dim)

        self.cells: list[list[int]] = [
            [0 for _ in range(self.dimensions.cols)]
            for _ in range(self.dimensions.rows)
        ]

        self.seed_points: list[Position] = []

        self.rng = rng if rng is not None else random.Random()

    def generate_seed_points(self, num_seeds: int) -> None:
        """Place seed points at random cell centers across the grid.

        Args:
            num_seeds (int): Number of seed points to generate.
        """
        seed_points: list[Position] = []

        for _ in range(num_seeds):
            column = self.rng.randint(0, self.dimensions.cols - 1)
            row = self.rng.randint(0, self.dimensions.rows - 1)
            seed = Position(x=column + 0.5, y=row + 0.5)
            seed_points.append(seed)

        self.seed_points = seed_points

    def _find_closest_seed(self, point: Position) -> int:
        """Find the index of the seed point nearest to a point.

        Args:
            point (Position): The point to measure from.

        Returns:
            closest_idx (int): Index of the nearest seed point.
        """
        min_distance_squared = float("inf")
        closest_idx = 0

        for idx, seed in enumerate(self.seed_points):
            delta_x = point.x - seed.x
            delta_y = point.y - seed.y
            distance_squared = delta_x**2 + delta_y**2

            if distance_squared < min_distance_squared:
                min_distance_squared = distance_squared
                closest_idx = idx

        return closest_idx

    def generate_voronoi_diagram(self) -> None:
        """Assign every cell to the region of its nearest seed point."""
        for row in range(self.dimensions.rows):
            for col in range(self.dimensions.cols):
                cell_center = Position(x=col + 0.5, y=row + 0.5)
                closest_seed_idx = self._find_closest_seed(cell_center)
                self.cells[row][col] = closest_seed_idx
