"""Module for the image variant: the wave overlay is drawn on a photo of the lake."""

import numpy as np
import pygame as pg

from water_ripples.config_model import ConfigModel
from water_ripples.masks import load_mask
from water_ripples.simulation import (
    RippleSimulation,
    clamp,
    colorize,
    to_trapezoid_pixels,
)


class ImageRipples(RippleSimulation):
    """Ripple overlay on a background photograph, drawn only where the lake mask is set.

    Attributes:
        perspective_start (float): Strength of the perspective. 0 is flat, higher values
            make the bottom rows dominate.
        trapezoid (TrapezoidPixels): The trapezoid in window pixel coordinates.
        scaled_cell_height (float): Height of one row of the trapezoid in pixels.
        background_image (pg.Surface): The photograph, scaled to the window.
        mask (np.ndarray): Boolean array of the window size, True where the lake is.

    Example:
        >>> simulation = ImageRipples(config=ConfigManager().load_config_file())
        >>> simulation.execute()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initialize the simulation, the trapezoid and the image and mask.

        Args:
            config (ConfigModel): The validated configuration.
        """
        super().__init__(config=config)

        self.perspective_start = config.image.perspective_start
        self._normalized_trapezoid = config.trapezoid
        self.trapezoid = to_trapezoid_pixels(
            normalized=config.trapezoid,
            window_width=self.window_width,
            window_height=self.window_height,
        )

        normalized_height = config.trapezoid.y_bottom - config.trapezoid.y_top
        self.scaled_cell_height = self.grid_cell_height * normalized_height

        background = pg.image.load(config.image.image_path).convert()
        self.background_image = pg.transform.scale(
            background, (self.window_width, self.window_height)
        )
        self.mask = load_mask(
            mask_path=config.image.mask_path,
            height=self.window_height,
            width=self.window_width,
        )

    def _compute_vertical_scaling(self, y: float) -> float:
        """Map a grid row to its projected vertical position.

        The projection is quadratic in y, so rows near the bottom get more height than
        rows near the top. perspective_start controls how strong that effect is: 0 gives
        equal rows, and larger values make the bottom rows dominate.

        Args:
            y (float): Grid row, starting at 0 for the top row.

        Returns:
            y_adjusted (float): The projected position of the row.
        """
        scaling_rate = self.perspective_start / self.number_of_rows * 2
        linear_term = y * self.perspective_start
        quadratic_term = (y * (y + 1) / 2) * scaling_rate
        y_adjusted = linear_term + quadratic_term

        return y_adjusted

    def _inverse_vertical_scaling(self, y_adjusted: float) -> float:
        """Invert _compute_vertical_scaling: find the grid row that projects to a
        position.

        The projection is quadratic, so the inverse comes from the positive root of the
        quadratic formula.

        Args:
            y_adjusted (float): The projected position to invert.

        Returns:
            y (float): The grid row that projects to y_adjusted.
        """
        scaling_rate = self.perspective_start / self.number_of_rows * 2
        a = scaling_rate / 2
        b = self.perspective_start + scaling_rate / 2
        discriminant = b**2 + 4 * a * y_adjusted
        root = np.sqrt(discriminant)
        y = (-b + root) / (2 * a)

        return y

    def _row_x_bounds(self, y_adjusted: float) -> tuple[float, float]:
        """Find the left and right pixel edges of a projected row.

        Args:
            y_adjusted (float): The projected row position, from
                _compute_vertical_scaling.

        Returns:
            x_bounds (tuple[float, float]): The left and right pixel edges of the row.
        """
        height_per_row = self.window_height / self.number_of_rows
        left_span = (
            self._normalized_trapezoid.x_bottom_left
            - self._normalized_trapezoid.x_top_left
        )
        right_span = (
            self._normalized_trapezoid.x_bottom_right
            - self._normalized_trapezoid.x_top_right
        )

        x_left = self.trapezoid.x_top_left + left_span * y_adjusted * height_per_row
        x_right = self.trapezoid.x_top_right + right_span * y_adjusted * height_per_row
        x_bounds = (x_left, x_right)

        return x_bounds

    def _mouse_y_to_grid_y(self, my: int) -> int | None:
        """Find the grid row for a mouse y position, or None outside the trapezoid.

        Args:
            my (int): The y pixel position of the mouse.

        Returns:
            grid_y (int | None): The grid row, clamped to the valid range, or None if
                the mouse is above or below the trapezoid.
        """
        if my < self.trapezoid.y_top or my > self.trapezoid.y_bottom:
            return None

        y_adjusted = (my - self.trapezoid.y_top) / self.scaled_cell_height
        inverse_row = self._inverse_vertical_scaling(y_adjusted=y_adjusted)
        grid_y = int(inverse_row)
        clamped_y = clamp(grid_y, 0, self.number_of_rows - 1)

        return clamped_y

    def _mouse_x_to_grid_x(self, mx: int, grid_y: int) -> int:
        """Find the grid column for a mouse x position, using the bounds of the row.

        Args:
            mx (int): The x pixel position of the mouse.
            grid_y (int): The grid row, which determines the bounds to interpolate
                within.

        Returns:
            grid_x (int): The grid column, clamped to the valid range.
        """
        y_adjusted = self._compute_vertical_scaling(y=grid_y)
        x_left, x_right = self._row_x_bounds(y_adjusted=y_adjusted)
        fraction = (mx - x_left) / (x_right - x_left)
        grid_x = int(fraction * self.number_of_columns)
        clamped_x = clamp(grid_x, 0, self.number_of_columns - 1)

        return clamped_x

    def _mouse_to_grid(self, mx: int, my: int) -> tuple[int, int] | None:
        """Convert a mouse pixel position to a grid cell of the trapezoid.

        Args:
            mx (int): The x pixel position of the mouse.
            my (int): The y pixel position of the mouse.

        Returns:
            grid_position (tuple[int, int] | None): The (column, row) under the mouse,
                or None if the mouse is outside the trapezoid.
        """
        grid_y = self._mouse_y_to_grid_y(my=my)

        if grid_y is None:
            return None

        grid_x = self._mouse_x_to_grid_x(mx=mx, grid_y=grid_y)
        grid_position = (grid_x, grid_y)

        return grid_position

    def _map_state_to_rgba(self) -> np.ndarray:
        """Map the current state to an RGBA array, with alpha proportional to the wave
        intensity.

        Flat water is fully transparent, so the photograph shows through. Active waves
        are opaque.

        Returns:
            rgba_array (np.ndarray): A uint8 array of shape (rows, cols, 4).
        """
        rgb_array = colorize(
            state=self.current_state,
            maximum_brightness=self.maximum_brightness,
            floor=0.1,
            span=0.8,
        )
        clipped_state = np.clip(self.current_state, 0, 255).astype(np.float32)
        normalized_state = clipped_state / self.maximum_brightness
        alpha_float = normalized_state * 255
        alpha_array = alpha_float.astype(np.uint8)
        alpha_channel = alpha_array[..., np.newaxis]
        rgba_array = np.concatenate([rgb_array, alpha_channel], axis=-1)

        return rgba_array

    def _render_state(self, rgba_array: np.ndarray) -> None:
        """Draw each grid cell as a quadrilateral on a transparent overlay, where the
        mask is set.

        Each cell's corners come from the projected rows above and below it. A cell is
        skipped when its center is outside the lake mask. The overlay is blitted over
        the background at the end, so the alpha of each cell blends with the photograph.

        Args:
            rgba_array (np.ndarray): A uint8 array of shape (rows, cols, 4).
        """
        overlay = pg.Surface((self.window_width, self.window_height), pg.SRCALPHA)

        for y in range(self.number_of_rows):
            y_adjusted_top = self._compute_vertical_scaling(y=y)
            y_adjusted_bottom = self._compute_vertical_scaling(y=y + 1)
            x_left_top, x_right_top = self._row_x_bounds(y_adjusted=y_adjusted_top)
            x_left_bottom, x_right_bottom = self._row_x_bounds(
                y_adjusted=y_adjusted_bottom
            )

            cell_width_top = (x_right_top - x_left_top) / self.number_of_columns
            cell_width_bottom = (
                x_right_bottom - x_left_bottom
            ) / self.number_of_columns
            y_cell_top = self.trapezoid.y_top + y_adjusted_top * self.scaled_cell_height
            y_cell_bottom = (
                self.trapezoid.y_top + y_adjusted_bottom * self.scaled_cell_height
            )

            for x in range(self.number_of_columns):
                x_cell_top = x_left_top + x * cell_width_top
                x_cell_bottom = x_left_bottom + x * cell_width_bottom

                center_x = int(x_cell_top + cell_width_top / 2)
                center_y = int((y_cell_top + y_cell_bottom) / 2)
                clamped_x = clamp(center_x, 0, self.window_width - 1)
                clamped_y = clamp(center_y, 0, self.window_height - 1)

                if not self.mask[clamped_y, clamped_x]:
                    continue

                color_rgba = tuple(rgba_array[y, x])
                corners = [
                    (x_cell_top, y_cell_top),
                    (x_cell_top + cell_width_top, y_cell_top),
                    (x_cell_bottom + cell_width_bottom, y_cell_bottom),
                    (x_cell_bottom, y_cell_bottom),
                ]
                pg.draw.polygon(overlay, color_rgba, corners)

        self.screen.blit(overlay, (0, 0))

    def _draw_frame(self) -> None:
        """Draw the background photograph, then the wave overlay on top of it."""
        self.screen.blit(self.background_image, (0, 0))
        rgba_array = self._map_state_to_rgba()
        self._render_state(rgba_array=rgba_array)
