"""Module for the Perlin noise grid and gradient vector initialization."""

import math

import numpy as np

from src.perlin_noise.config_model import ConfigModel
from src.perlin_noise.constants import Dimensions
from src.perlin_noise.pn_visualizer import PNVisualizer
from src.perlin_noise.utils import smooth_perline_polyominal


class PerlinNoise:
    """Manages the Perlin noise gradient grid and exposes noise sampling."""

    def __init__(self, config: ConfigModel) -> None:
        """
        Unpack config and initialize the gradient grid.

        Args:
            config (ConfigModel): Configuration settings as a Pydantic model.
        """
        # Initializations.
        self.gradient_grid_dimensions = Dimensions(
            rows=config.grid.dim + 1, cols=config.grid.dim + 1
        )
        self.cell_resolution = config.grid.cell_resolution
        self.step_size = 1 / self.cell_resolution
        self.noise_grid_dimensions = Dimensions(
            rows=config.grid.dim * self.cell_resolution,
            cols=config.grid.dim * self.cell_resolution,
        )
        self.smoothing_version: str = config.grid.smoothing_version

        self.gradient_grid: np.ndarray
        self.noise_grid: np.ndarray = np.zeros(self.noise_grid_dimensions)

        if config.grid.random_seed is not None:
            self.rng = np.random.default_rng(config.grid.random_seed)
        else:
            self.rng = np.random.default_rng()

        self.pn_visualizer = PNVisualizer(config=config)

    def _populate_gradient_grid(self) -> np.ndarray:
        """
        Populate a grid of random unit gradient vectors at each node.

        Each node sits at an integer coordinate corner. A random angle is
        sampled uniformly from [0, 2π) and projected onto the unit circle
        via cos/sin, producing a unit gradient vector at every node.

        Returns:
            grid (np.ndarray): Array of shape (rows, cols, 2) containing
                a unit gradient vector at each grid node.
        """
        angles = self.rng.uniform(0, 2 * np.pi, self.gradient_grid_dimensions)
        gradient_grid = np.stack([np.cos(angles), np.sin(angles)], axis=-1)

        return gradient_grid

    def _compute_noise_grid(self, interpolate: bool = True) -> np.ndarray:
        """
        Compute the dot product between gradient vectors and offset vectors for each sample point.

        1. Iterate over every sample point in the noise grid.
        2. Determine which grid cell the sample point falls in.
        3. Identify the four corner nodes of that cell.
        4. Compute the offset vector from each corner to the sample point.
        5. Compute the dot product of each corner's gradient with its offset vector.

        Returns:
            noise_grid (np.ndarray): Array of shape (rows, cols) containing
                the dot product value at each sample point.
        """
        noise_grid = np.zeros(self.noise_grid_dimensions)

        for row in range(self.noise_grid_dimensions.rows):
            for col in range(self.noise_grid_dimensions.cols):
                x_coordinate = col * self.step_size
                y_coordinate = row * self.step_size
                sample_point = np.array([x_coordinate, y_coordinate])

                gradient_grid_x = math.floor(x_coordinate)
                gradient_grid_y = math.floor(y_coordinate)

                c1 = np.array([gradient_grid_x, gradient_grid_y])
                c2 = np.array([gradient_grid_x + 1, gradient_grid_y])
                c3 = np.array([gradient_grid_x, gradient_grid_y + 1])
                c4 = np.array([gradient_grid_x + 1, gradient_grid_y + 1])

                corners = [c1, c2, c3, c4]
                offset_vectors = [sample_point - c for c in corners]

                if not interpolate:
                    dots = [
                        np.dot(self.gradient_grid[c[1], c[0]], v)
                        for c, v in zip(corners, offset_vectors)
                    ]

                    noise_grid[row, col] = sum(dots) / 4
                else:
                    dot_bl, dot_br, dot_tl, dot_tr = [
                        np.dot(self.gradient_grid[c[1], c[0]], offset)
                        for c, offset in zip(corners, offset_vectors)
                    ]

                    dx, dy = offset_vectors[0]

                    # Smoothing
                    sx = smooth_perline_polyominal(
                        dx, smoothing_version=self.smoothing_version
                    )
                    sy = smooth_perline_polyominal(
                        dy, smoothing_version=self.smoothing_version
                    )

                    # Interpolation.
                    bottom = dot_bl + sx * (dot_br - dot_bl)
                    top = dot_tl + sx * (dot_tr - dot_tl)

                    noise_grid[row, col] = bottom + sy * (top - bottom)

        return noise_grid

    def generate(self, visualize_substeps: bool = False) -> None:
        """Execute the Perlin Noise generation algorithm."""
        # 1. Populate the gradient grid with vectors at each node.
        self.gradient_grid = self._populate_gradient_grid()

        # Visualizations.
        if visualize_substeps:
            # self.pn_visualizer.visualize_gradient_grid(gradient_grid=self.gradient_grid)
            self.noise_grid = self._compute_noise_grid(interpolate=False)

            self.pn_visualizer.visualize_noise_grid(noise_grid=self.noise_grid)

        self.noise_grid = self._compute_noise_grid()
        self.pn_visualizer.visualize_noise_grid(noise_grid=self.noise_grid)
