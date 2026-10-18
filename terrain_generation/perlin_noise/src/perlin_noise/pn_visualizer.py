"""Module for drawing the Perlin noise grid, gradient vectors and noise cells with PyGame."""

from dataclasses import dataclass

import numpy as np
import pygame as pg
from pg_plonker.controls import Button
from pg_plonker.gui_panel import GUIPanel

from perlin_noise.config_model import ConfigModel
from perlin_noise.constants import Dimensions, Size
from perlin_noise.utils import get_window_size_from_screen_resolution, lerp_color


@dataclass
class ButtonState:
    """Toggle buttons for the Perlin noise visualization.

    Attributes:
        grid (Button): Toggles the grid lines.
        gradient_vectors (Button): Toggles the gradient arrows.
        noise_vectors (Button): Toggles the noise cells.
    """

    grid: Button
    gradient_vectors: Button
    noise_vectors: Button


@dataclass
class VisibilityState:
    """Toggleable visibility flags for the Perlin noise visualization.

    Attributes:
        show_grid (bool): Whether to draw the grid lines.
        show_gradients (bool): Whether to draw the gradient arrows.
        show_noise (bool): Whether to draw the noise cells.
    """

    show_grid: bool
    show_gradients: bool
    show_noise: bool

    @classmethod
    def from_buttons(cls, buttons: ButtonState) -> "VisibilityState":
        """Read the current state of each toggle button.

        Args:
            buttons (ButtonState): The registered toggle buttons.

        Returns:
            visibility (VisibilityState): The current visibility state.
        """
        visibility = cls(
            show_grid=buttons.grid.value,
            show_gradients=buttons.gradient_vectors.value,
            show_noise=buttons.noise_vectors.value,
        )

        return visibility


class PNVisualizer:
    """Draw the Perlin noise grid, its gradient vectors and its noise in a PyGame window.

    Attributes:
        margin_size (int): Pixel margin around the grid on all sides.
        arrow_length (float): Length of the gradient arrows, in grid cells.
        background_color (RGBColor): Background color of the window.
        grid_line_color (RGBColor): Color of the grid lines.
        circle_color (RGBColor): Color of the grid nodes.
        arrow_color (RGBColor): Color of the gradient arrows.
        heatmap_positive_color (RGBColor): Color for the largest positive noise.
        heatmap_negative_color (RGBColor): Color for the most negative noise.
        grid_line_width (int): Width of the grid lines in pixels.
        circle_width (int): Radius of the grid nodes in pixels.
        arrow_width (int): Width of the gradient arrows in pixels.
        gradient_grid_dimensions (Dimensions): Rows and columns of gradient nodes.
        screen_size (Size): Size of the window in pixels.
        screen (pg.Surface): The PyGame window surface.
        gui_panel (GUIPanel): Side panel that holds the toggle buttons.
        grid_size (float): Side length of the square grid area, in pixels.
        cell_size (float): Side length of one grid cell, in pixels.

    Example:
        >>> visualizer = PNVisualizer(config=ConfigManager().read_config())
        >>> buttons = visualizer.register_buttons()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Open the PyGame window and size the grid to fit inside it.

        Args:
            config (ConfigModel): The validated configuration model.
        """
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

        pg.init()

        window_width, window_height = get_window_size_from_screen_resolution()
        self.screen_size = Size(width=window_width, height=window_height)
        self.screen = pg.display.set_mode((window_width, window_height))

        self.gui_panel = GUIPanel(surface=self.screen)

        self.grid_size = min(
            self.screen_size.width - 2 * self.margin_size,
            self.screen_size.height - 2 * self.margin_size,
        )
        self.cell_size = self.grid_size / self.gradient_grid_dimensions.cols

    def _draw_grid_lines(self) -> None:
        """Draw horizontal and vertical grid lines across the grid area."""
        grid_end = int(self.margin_size + self.grid_size)

        for row in range(self.gradient_grid_dimensions.rows + 1):
            y = int(self.margin_size + row * self.cell_size)
            start = (self.margin_size, y)
            end = (grid_end, y)
            pg.draw.line(self.screen, self.grid_line_color, start, end, self.grid_line_width)

        for col in range(self.gradient_grid_dimensions.cols + 1):
            x = int(self.margin_size + col * self.cell_size)
            start = (x, self.margin_size)
            end = (x, grid_end)
            pg.draw.line(self.screen, self.grid_line_color, start, end, self.grid_line_width)

    def _draw_gradient_vectors(self, gradient_grid: np.ndarray) -> None:
        """Draw each grid node as a dot, with its gradient vector as an arrow.

        Args:
            gradient_grid (np.ndarray): Array of shape (rows, cols, 2) containing a unit
                gradient vector at each grid node.
        """
        arrow_length_px = self.cell_size * self.arrow_length

        for row, row_data in enumerate(gradient_grid):
            for col, gradient in enumerate(row_data):
                node_x = self.margin_size + col * self.cell_size
                node_y = self.margin_size + row * self.cell_size
                node_center = (int(node_x), int(node_y))

                pg.draw.circle(self.screen, self.circle_color, node_center, self.circle_width)

                tip_x = node_x + gradient[0] * arrow_length_px
                tip_y = node_y + gradient[1] * arrow_length_px
                arrow_tip = (int(tip_x), int(tip_y))

                pg.draw.line(self.screen, self.arrow_color, node_center, arrow_tip, self.arrow_width)

    def _draw_noise_cells(self, noise_grid: np.ndarray) -> None:
        """Draw the noise grid as colored cells.

        Negative values shade toward the negative color, positive values toward the positive color,
        and values near zero stay close to white. The largest magnitude sets the full color.

        Args:
            noise_grid (np.ndarray): 2D array of scalar noise values.
        """
        rows, cols = noise_grid.shape

        cell_width = self.grid_size / cols
        cell_height = self.grid_size / rows

        absolute_noise = np.abs(noise_grid)
        largest_magnitude = float(np.max(absolute_noise))
        scale = largest_magnitude if largest_magnitude > 0 else 1.0

        for row in range(rows):
            for col in range(cols):
                normalized = noise_grid[row, col] / scale

                if normalized >= 0:
                    color = lerp_color(self.heatmap_positive_color, normalized)
                else:
                    magnitude = abs(normalized)
                    color = lerp_color(self.heatmap_negative_color, magnitude)

                x = self.margin_size + col * cell_width
                y = self.margin_size + row * cell_height
                left = int(x)
                top = int(y)
                width = int(cell_width) + 1
                height = int(cell_height) + 1
                cell_rect = pg.Rect(left, top, width, height)

                pg.draw.rect(self.screen, color, cell_rect)

    def register_buttons(self) -> ButtonState:
        """Register the visualization toggle buttons with the GUI panel.

        Returns:
            buttons (ButtonState): The registered toggle buttons.
        """
        grid_button = self.gui_panel.add_button(text="Toggle Grid")
        gradient_button = self.gui_panel.add_button(text="Toggle gradients")
        noise_button = self.gui_panel.add_button(text="Toggle perlin noise")

        buttons = ButtonState(
            grid=grid_button,
            gradient_vectors=gradient_button,
            noise_vectors=noise_button,
        )

        return buttons

    def draw_frame(
        self,
        gradient_grid: np.ndarray,
        noise_grid: np.ndarray,
        visibility: VisibilityState,
    ) -> None:
        """Render one frame: the noise, the gradients, the grid lines, and the GUI panel.

        Args:
            gradient_grid (np.ndarray): Array of shape (rows, cols, 2) containing unit gradient
                vectors at each grid node.
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
