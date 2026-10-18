"""Module for the trapezoid variant: the grid is projected onto a trapezoid for a sense of depth."""

from dataclasses import dataclass

import numpy as np
import pygame as pg

from water_ripples.config_model import ConfigModel
from water_ripples.simulation import (
    RippleSimulation,
    clamp,
    colorize,
    to_trapezoid_pixels,
)


@dataclass
class RowGeometry:
    """Pixel bounds of one grid row.

    Attributes:
        y_top (int): Top pixel row of the grid row.
        y_bottom (int): Bottom pixel row of the grid row.
        x_left (int): Left pixel column at this row.
        x_right (int): Right pixel column at this row.
    """

    y_top: int
    y_bottom: int
    x_left: int
    x_right: int


class TrapezoidRipples(RippleSimulation):
    """Ripple simulation projected onto a trapezoid, so rows near the top look smaller.

    Attributes:
        perspective_exponent (float): Strength of the perspective. 0 is flat, higher values make the
            bottom rows dominate.
        trapezoid (TrapezoidPixels): The trapezoid in window pixel coordinates.
        row_geometry (list[RowGeometry]): Pixel bounds of every grid row, computed once.

    Example:
        >>> simulation = TrapezoidRipples(config=ConfigManager().load_config_file())
        >>> simulation.execute()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initialize the simulation and precompute the row geometry.

        Args:
            config (ConfigModel): The validated configuration.
        """
        super().__init__(config=config)

        self.perspective_exponent = config.trapezoid.perspective_exponent
        self.trapezoid = to_trapezoid_pixels(
            normalized=config.trapezoid,
            window_width=self.window_width,
            window_height=self.window_height,
        )

        self.row_geometry = self._compute_row_geometry()

    def _compute_row_geometry(self) -> list[RowGeometry]:
        """Precompute the pixel bounds of every row, which gives the perspective effect.

        Row i gets weight (i + 1) ** perspective_exponent, so rows near the bottom are taller than
        rows near the top. The cumulative weights become normalized row boundaries, which place each
        row's top and bottom edges. The left and right edges are interpolated between the top and
        bottom corners of the trapezoid at the top edge of the row.

        Returns:
            geometry (list[RowGeometry]): One entry per grid row, from top to bottom.
        """
        weights = [
            (i + 1) ** self.perspective_exponent for i in range(self.number_of_rows)
        ]
        total_weight = sum(weights)

        cumulative = 0.0
        t_values = [0.0]
        for weight in weights:
            cumulative += weight / total_weight
            t_values.append(cumulative)

        trapezoid_height = self.trapezoid.y_bottom - self.trapezoid.y_top

        geometry: list[RowGeometry] = []
        for y in range(self.number_of_rows):
            t_top = t_values[y]
            t_bottom = t_values[y + 1]

            y_top = int(self.trapezoid.y_top + t_top * trapezoid_height)
            y_bottom = int(self.trapezoid.y_top + t_bottom * trapezoid_height)

            left_span = self.trapezoid.x_bottom_left - self.trapezoid.x_top_left
            right_span = self.trapezoid.x_bottom_right - self.trapezoid.x_top_right
            x_left = int(self.trapezoid.x_top_left + left_span * t_top)
            x_right = int(self.trapezoid.x_top_right + right_span * t_top)

            row = RowGeometry(y_top=y_top, y_bottom=y_bottom, x_left=x_left, x_right=x_right)
            geometry.append(row)

        geometry[-1].y_bottom = int(self.trapezoid.y_bottom)

        return geometry

    def _mouse_x_to_grid_x(self, mx: int, grid_y: int) -> int:
        """Find the grid column for a mouse x position, using the bounds of the row.

        Args:
            mx (int): The x pixel position of the mouse.
            grid_y (int): The grid row, which determines the bounds to interpolate within.

        Returns:
            grid_x (int): The grid column, clamped to the valid range.
        """
        geometry = self.row_geometry[grid_y]
        row_width = geometry.x_right - geometry.x_left
        fraction = (mx - geometry.x_left) / row_width
        grid_x = int(fraction * self.number_of_columns)
        clamped_x = clamp(grid_x, 0, self.number_of_columns - 1)

        return clamped_x

    def _mouse_y_to_grid_y(self, my: int) -> int:
        """Find the grid row whose pixel range contains a mouse y position.

        Args:
            my (int): The y pixel position of the mouse.

        Returns:
            grid_y (int): The grid row. Positions below every row map to the last row.
        """
        for grid_y, geometry in enumerate(self.row_geometry):
            if geometry.y_top <= my < geometry.y_bottom:
                return grid_y

        last_row = self.number_of_rows - 1

        return last_row

    def _mouse_to_grid(self, mx: int, my: int) -> tuple[int, int] | None:
        """Convert a mouse pixel position to a grid cell of the trapezoid.

        Args:
            mx (int): The x pixel position of the mouse.
            my (int): The y pixel position of the mouse.

        Returns:
            grid_position (tuple[int, int] | None): The (column, row) under the mouse.
        """
        grid_y = self._mouse_y_to_grid_y(my=my)
        grid_x = self._mouse_x_to_grid_x(mx=mx, grid_y=grid_y)
        grid_position = (grid_x, grid_y)

        return grid_position

    def _map_state_to_rgba(self) -> np.ndarray:
        """Map the current state to an RGBA array of shape (rows, cols, 4).

        The alpha channel is 255 everywhere, so the whole grid is opaque.

        Returns:
            rgba_array (np.ndarray): A uint8 array of shape (rows, cols, 4).
        """
        rgb_array = colorize(
            state=self.current_state,
            maximum_brightness=self.maximum_brightness,
            floor=0.0,
            span=1.0,
        )
        alpha_array = np.full_like(self.current_state, 255, dtype=np.uint8)
        alpha_channel = alpha_array[..., np.newaxis]
        rgba_array = np.concatenate([rgb_array, alpha_channel], axis=-1)

        return rgba_array

    def _render_rows(self, rgba_array: np.ndarray) -> None:
        """Draw each grid row as a stretched strip at its trapezoid position.

        Each row is drawn as a one-pixel-tall surface, scaled to the row's pixel bounds. Rows with no
        width or height are skipped.

        Args:
            rgba_array (np.ndarray): A uint8 array of shape (rows, cols, 4).
        """
        self.screen.fill(self.background_color)

        for y, geometry in enumerate(self.row_geometry):
            row_height = geometry.y_bottom - geometry.y_top
            row_width = geometry.x_right - geometry.x_left

            if row_height <= 0 or row_width <= 0:
                continue

            row_rgba = rgba_array[y]
            row_surface = pg.Surface((self.number_of_columns, 1), pg.SRCALPHA)
            pg.surfarray.pixels3d(row_surface)[:, 0, :] = row_rgba[:, :3]
            pg.surfarray.pixels_alpha(row_surface)[:, 0] = row_rgba[:, 3]

            scaled_row = pg.transform.scale(row_surface, (row_width, row_height))
            self.screen.blit(scaled_row, (geometry.x_left, geometry.y_top))

    def _draw_frame(self) -> None:
        """Draw the current state onto the window."""
        rgba_array = self._map_state_to_rgba()
        self._render_rows(rgba_array=rgba_array)
