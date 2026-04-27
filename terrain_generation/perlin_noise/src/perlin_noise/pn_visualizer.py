"""Module for visualizing Perlin Noise using pygame."""

from typing import Callable

import numpy as np
import pygame as pg

from src.perlin_noise.config_manager import ConfigModel
from src.perlin_noise.constants import Dimensions, Size
from src.perlin_noise.utils import get_window_size_from_screen_resolution, lerp_color


class PNVisualizer:
    """ """

    def __init__(
        self,
        config: ConfigModel,
    ) -> None:
        """
        Initialize pygame and configure the visualizer for the given grid.

        Args:
            config (ConfigModel): The validated configuration model.
            margin_size (int): Pixel margin around the grid on all sides, defaults to 20.
        """
        # Extract relevant variables from configuration variable.
        self.margin_size = config.visualization.margin_size
        self.arrow_length = config.visualization.arrow_length
        self.background_color = config.visualization.background_color
        self.grid_line_color = config.visualization.grid_line_color
        self.circle_color = config.visualization.circle_color
        self.arrow_color = config.visualization.arrow_color
        self.heatmap_positive_color = config.visualization.heatmap_positive_color
        self.heatmap_negative_color = config.visualization.heatmap_negative_color

        self.grid_line_width = config.visualization.grid_line_width
        self.circle_width = config.visualization.circle_width
        self.arrow_width = config.visualization.arrow_width

        self.gradient_grid_dimensions = Dimensions(
            rows=config.grid.dim, cols=config.grid.dim
        )

        # Intializations.
        pg.init()
        self.screen_size = Size(*get_window_size_from_screen_resolution())

        self.screen = pg.display.set_mode(
            (self.screen_size.width, self.screen_size.height)
        )

        self.grid_size = min(
            self.screen_size.width - 2 * self.margin_size,
            self.screen_size.height - 2 * self.margin_size,
        )

        self.cell_size = self.grid_size / self.gradient_grid_dimensions.cols

    def _draw_grid_lines(self) -> None:
        """Draw horizontal and vertical grid lines across the grid area."""
        for row in range(self.gradient_grid_dimensions.rows + 1):
            y = int(self.margin_size + row * self.cell_size)
            pg.draw.line(
                self.screen,
                self.grid_line_color,
                (self.margin_size, y),
                (int(self.margin_size + self.grid_size), y),
                self.grid_line_width,
            )

        for col in range(self.gradient_grid_dimensions.cols + 1):
            x = int(self.margin_size + col * self.cell_size)
            pg.draw.line(
                self.screen,
                self.grid_line_color,
                (x, self.margin_size),
                (x, int(self.margin_size + self.grid_size)),
                self.grid_line_width,
            )

    def _draw_gradient_vectors(self, grid: np.ndarray) -> None:
        """
        Draw each grid node as a point and its gradient vector as an arrow.

        Args:
            grid (np.ndarray): Array of shape (rows, cols, 2) containing a unit
                gradient vector at each grid node.
        """
        for row, row_data in enumerate(grid):
            for col, gradient in enumerate(row_data):
                node_x = self.margin_size + col * self.cell_size
                node_y = self.margin_size + row * self.cell_size

                pg.draw.circle(
                    self.screen,
                    self.circle_color,
                    (int(node_x), int(node_y)),
                    self.circle_width,
                )

                arrow_length_px = self.cell_size * self.arrow_length
                tip_x = node_x + gradient[0] * arrow_length_px
                tip_y = node_y + gradient[1] * arrow_length_px

                pg.draw.line(
                    self.screen,
                    self.arrow_color,
                    (int(node_x), int(node_y)),
                    (int(tip_x), int(tip_y)),
                    self.arrow_width,
                )

    def _draw_noise_cells(self, noise_grid: np.ndarray) -> None:
        """
        Draw the scalar noise grid as colored square cells.

        Negative values map toward blue, positive toward red,
        and values near zero toward white.

        Args:
            noise_grid (np.ndarray): 2D array of scalar noise values.
        """
        rows, cols = noise_grid.shape

        cell_width = self.grid_size / cols
        cell_height = self.grid_size / rows

        max_abs = np.max(np.abs(noise_grid))

        for row in range(rows):
            for col in range(cols):
                value = noise_grid[row, col]

                normalized = value / max_abs

                if normalized >= 0:
                    color = lerp_color(self.heatmap_positive_color, normalized)
                else:
                    color = lerp_color(self.heatmap_negative_color, abs(normalized))

                x = self.margin_size + col * cell_width
                y = self.margin_size + row * cell_height

                rect = pg.Rect(
                    int(x),
                    int(y),
                    int(cell_width) + 1,
                    int(cell_height) + 1,
                )

                pg.draw.rect(self.screen, color, rect)

    def _render(self, draw_operations: list[Callable]) -> None:
        """
        Clear the screen, execute draw operations, present the frame,
        and keep the window alive until exit.
        """
        self.screen.fill(self.background_color)

        for draw_operation in draw_operations:
            draw_operation()

        pg.display.flip()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT or (
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
                ):
                    pg.quit()
                    raise SystemExit

    def visualize_gradient_grid(self, gradient_grid: np.ndarray) -> None:
        """
        Visualize the gradient vector field on the lattice nodes.

        Renders:
            1. The grid lines defining the lattice structure.
            2. A gradient vector at each lattice node.

        Args:
            gradient_grid (np.ndarray): Array of shape (rows, cols, 2)
                containing unit gradient vectors for each lattice node.
        """
        self._render(
            [
                self._draw_grid_lines,
                lambda: self._draw_gradient_vectors(grid=gradient_grid),
            ]
        )

    def visualize_noise_grid(self, noise_grid: np.ndarray) -> None:
        """
        Visualize the raw scalar noise field before interpolation.

        Each sample point is rendered as a distinct colored square cell.
        Negative values map toward blue, positive values toward red,
        and values near zero toward white.

        This visualization is useful for inspecting the raw dot-product
        contributions prior to Perlin interpolation.

        Args:
            noise_grid (np.ndarray): 2D array of scalar noise values
                with shape (rows, cols).
        """
        self._render(
            [
                lambda: self._draw_noise_cells(noise_grid=noise_grid),
                self._draw_grid_lines,
            ]
        )
