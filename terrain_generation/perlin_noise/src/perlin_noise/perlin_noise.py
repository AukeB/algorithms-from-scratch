"""Module for generating 2D Perlin noise and running its visualization."""

import math

import numpy as np
import pygame as pg

from perlin_noise.config_model import ConfigModel
from perlin_noise.constants import Dimensions, SmoothingVersion
from perlin_noise.pn_visualizer import PNVisualizer, VisibilityState
from perlin_noise.utils import smooth_perlin_polynomial


class PerlinNoise:
    """Generate 2D Perlin noise on a grid of random gradients and show it with PyGame.

    Attributes:
        gradient_grid_dimensions (Dimensions): Rows and columns of gradient nodes. There is one
            more node than cells along each side.
        cell_resolution (int): Number of samples per cell along one dimension.
        step_size (float): Distance between two samples, in grid coordinates.
        noise_grid_dimensions (Dimensions): Rows and columns of the noise grid.
        smoothing_version (SmoothingVersion): The fade curve used for interpolation.
        gradient_grid (np.ndarray): Unit gradient vector at each node, shape (rows, cols, 2).
        noise_grid (np.ndarray): Noise value at each sample.
        rng (np.random.Generator): Random generator for the gradients.
        pn_visualizer (PNVisualizer): Draws the grids and owns the GUI panel.
        buttons (ButtonState): The visibility toggle buttons.

    Example:
        >>> config = ConfigManager().read_config()
        >>> perlin_noise = PerlinNoise(config=config)
        >>> perlin_noise.run()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Set up the grids, the random generator, and the visualizer.

        Args:
            config (ConfigModel): The validated configuration model.
        """
        self.gradient_grid_dimensions = Dimensions(
            rows=config.grid.dim + 1, cols=config.grid.dim + 1
        )
        self.cell_resolution = config.grid.cell_resolution
        self.step_size = 1 / self.cell_resolution
        self.noise_grid_dimensions = Dimensions(
            rows=config.grid.dim * self.cell_resolution,
            cols=config.grid.dim * self.cell_resolution,
        )
        self.smoothing_version: SmoothingVersion = config.grid.smoothing_version

        self.gradient_grid = np.zeros(
            (self.gradient_grid_dimensions.rows, self.gradient_grid_dimensions.cols, 2)
        )
        self.noise_grid = np.zeros(self.noise_grid_dimensions)

        self.rng = np.random.default_rng(config.grid.random_seed)

        self.pn_visualizer = PNVisualizer(config=config)
        self.buttons = self.pn_visualizer.register_buttons()

    def _populate_gradient_grid(self) -> np.ndarray:
        """Fill the nodes with random unit gradient vectors.

        A random angle is drawn uniformly from [0, 2π) for each node, and converted to a unit vector
        with cos and sin.

        Returns:
            gradient_grid (np.ndarray): Array of shape (rows, cols, 2) with one unit vector per node.
        """
        angles = self.rng.uniform(0, 2 * np.pi, self.gradient_grid_dimensions)
        gradient_grid = np.stack([np.cos(angles), np.sin(angles)], axis=-1)

        return gradient_grid

    def _compute_noise_grid(self, interpolate: bool = True) -> np.ndarray:
        """Compute the Perlin noise value at every sample.

        For each sample, the four corners of its cell are found, the dot product of each corner's
        gradient with the offset to the sample is computed, and those values are combined. With
        interpolation, the combination is a smoothed bilinear blend. Without it, the dot products are
        averaged.

        Args:
            interpolate (bool): Whether to blend the corner values with a smoothed bilinear
                interpolation. If False, the corner values are averaged instead.

        Returns:
            noise_grid (np.ndarray): Array of shape (rows, cols) with the noise value at each sample.
        """
        noise_grid = np.zeros(self.noise_grid_dimensions)

        for row in range(self.noise_grid_dimensions.rows):
            for col in range(self.noise_grid_dimensions.cols):
                x_coordinate = col * self.step_size
                y_coordinate = row * self.step_size
                sample_point = np.array([x_coordinate, y_coordinate])

                cell_x = math.floor(x_coordinate)
                cell_y = math.floor(y_coordinate)

                c1 = np.array([cell_x, cell_y])
                c2 = np.array([cell_x + 1, cell_y])
                c3 = np.array([cell_x, cell_y + 1])
                c4 = np.array([cell_x + 1, cell_y + 1])

                corners = [c1, c2, c3, c4]
                offset_vectors = [sample_point - corner for corner in corners]

                if not interpolate:
                    dots = [
                        np.dot(self.gradient_grid[corner[1], corner[0]], offset)
                        for corner, offset in zip(corners, offset_vectors)
                    ]
                    total_dot = sum(dots)
                    noise_grid[row, col] = total_dot / 4
                else:
                    dot_bl, dot_br, dot_tl, dot_tr = [
                        np.dot(self.gradient_grid[corner[1], corner[0]], offset)
                        for corner, offset in zip(corners, offset_vectors)
                    ]

                    dx, dy = offset_vectors[0]
                    sx = smooth_perlin_polynomial(
                        t=dx, smoothing_version=self.smoothing_version
                    )
                    sy = smooth_perlin_polynomial(
                        t=dy, smoothing_version=self.smoothing_version
                    )

                    bottom = dot_bl + sx * (dot_br - dot_bl)
                    top = dot_tl + sx * (dot_tr - dot_tl)

                    noise_grid[row, col] = bottom + sy * (top - bottom)

        return noise_grid

    def generate(self) -> None:
        """Generate the gradient grid, then the noise grid from it."""
        self.gradient_grid = self._populate_gradient_grid()
        self.noise_grid = self._compute_noise_grid()

    def _handle_events(self) -> bool:
        """Pass the pending PyGame events to the GUI panel and check for quit requests.

        Returns:
            keep_running (bool): False once the window is closed or ESC is pressed, otherwise True.
        """
        keep_running = True

        for event in pg.event.get():
            if event.type == pg.QUIT:
                keep_running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                keep_running = False

            self.pn_visualizer.gui_panel.handle_event(event=event)

        return keep_running

    def run(self) -> None:
        """Run the event loop until the window is closed or ESC is pressed.

        The noise is generated once on startup. Every frame, events are handled and the layers that
        are toggled on are drawn.
        """
        self.generate()

        keep_running = True
        while keep_running:
            keep_running = self._handle_events()

            visibility = VisibilityState.from_buttons(self.buttons)
            self.pn_visualizer.draw_frame(
                gradient_grid=self.gradient_grid,
                noise_grid=self.noise_grid,
                visibility=visibility,
            )

        pg.quit()
