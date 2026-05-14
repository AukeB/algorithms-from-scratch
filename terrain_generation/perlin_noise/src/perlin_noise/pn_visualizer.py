"""Module for visualizing Perlin Noise using pygame."""

from dataclasses import dataclass
from typing import Callable, NamedTuple

import numpy as np
import pg_plonker as pgp
import pygame as pg
from pg_plonker.controls.button import Button
from pg_plonker.gui_panel import GUIPanel

from src.perlin_noise.config_manager import ConfigModel
from src.perlin_noise.constants import Dimensions, Size
from src.perlin_noise.utils import get_window_size_from_screen_resolution, lerp_color


@dataclass
class ButtonState:
    """Toggle buttons for the Perlin noise visualization."""

    grid: Button
    gradient_vectors: Button
    noise_vectors: Button


@dataclass
class VisibilityState:
    """Toggleable visibility flags for the Perlin noise visualization."""

    show_grid: bool
    show_gradients: bool
    show_noise: bool

    @classmethod
    def from_buttons(cls, buttons: ButtonState) -> "VisibilityState":
        """
        Construct a VisibilityState by reading the current state of each button.

        Args:
            buttons (ButtonState): The registered toggle buttons.

        Returns:
            visibility (VisibilityState): The current visibility state.
        """
        return cls(
            show_grid=buttons.grid.state,
            show_gradients=buttons.gradient_vectors.state,
            show_noise=buttons.noise_vectors.state,
        )


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

        self.gui_panel = GUIPanel(surface=self.screen)

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

    def _draw_gradient_vectors(self, gradient_grid: np.ndarray) -> None:
        """
        Draw each grid node as a point and its gradient vector as an arrow.

        Args:
            grid (np.ndarray): Array of shape (rows, cols, 2) containing a unit
                gradient vector at each grid node.
        """
        for row, row_data in enumerate(gradient_grid):
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

    def register_buttons(self) -> ButtonState:
        """
        Register all visualization toggle buttons with the GUI panel.

        Returns:
            buttons (ButtonState): The registered toggle buttons.
        """
        return ButtonState(
            grid=self.gui_panel.add_button(text="Toggle Grid"),
            gradient_vectors=self.gui_panel.add_button(text="Toggle gradients"),
            noise_vectors=self.gui_panel.add_button(text="Toggle perlin noise"),
        )

    def draw_frame(
        self,
        gradient_grid: np.ndarray,
        noise_grid: np.ndarray,
        visibility: VisibilityState,
    ) -> None:
        """
        Render a single frame of the Perlin noise visualization.

        Args:
            gradient_grid (np.ndarray): Array of shape (rows, cols, 2) containing
                unit gradient vectors at each grid node.
            noise_grid (np.ndarray): 2D array of scalar noise values.
            visibility (VisibilityState): Flags controlling which layers are drawn.
        """
        self.screen.fill(self.background_color)
        self.gui_panel.draw()

        if visibility.show_noise:
            self._draw_noise_cells(noise_grid=noise_grid)

        if visibility.show_gradients:
            self._draw_gradient_vectors(gradient_grid=gradient_grid)

        if visibility.show_grid:
            self._draw_grid_lines()

        pg.display.flip()
