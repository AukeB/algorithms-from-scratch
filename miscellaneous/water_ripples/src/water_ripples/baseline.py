"""Module for the baseline variant: a flat grid that fills the whole window."""

import numpy as np
import pygame as pg

from water_ripples.config_model import ConfigModel
from water_ripples.simulation import RippleSimulation, colorize


class BaselineRipples(RippleSimulation):
    """Flat ripple simulation that fills the window, with selectable render and propagate modes.

    Attributes:
        render_mode (str): "surfarray" blits the whole array at once, "rectangle" draws each cell.
        rgb_mode (str): How the state becomes RGB: "grayscale", "colormap" or "scaled_colormap".
        propagate_mode (str): How the next state is computed: "numba", "numpy" or "iterative".

    Example:
        >>> simulation = BaselineRipples(config=ConfigManager().load_config_file())
        >>> simulation.execute()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initialize the simulation and the baseline modes.

        Args:
            config (ConfigModel): The validated configuration.
        """
        super().__init__(config=config)

        self.render_mode = config.baseline.render_mode
        self.rgb_mode = config.baseline.rgb_mode
        self.propagate_mode = config.baseline.propagate_mode

    def _propagate_with_numpy(self) -> None:
        """Compute the next state with NumPy slicing, into current_state."""
        neighbor_sum = (
            self.previous_state[:-2, 1:-1]
            + self.previous_state[2:, 1:-1]
            + self.previous_state[1:-1, :-2]
            + self.previous_state[1:-1, 2:]
        )

        self.current_state[1:-1, 1:-1] = (
            neighbor_sum / 2 - self.current_state[1:-1, 1:-1]
        )

        self.current_state[1:-1, 1:-1] *= self.damping

    def _propagate_iterative(self) -> None:
        """Compute the next state with nested Python loops, into current_state."""
        for y in range(1, len(self.previous_state) - 1):
            for x in range(1, len(self.previous_state[y]) - 1):
                neighbor_sum = (
                    self.previous_state[y - 1, x]
                    + self.previous_state[y + 1, x]
                    + self.previous_state[y, x - 1]
                    + self.previous_state[y, x + 1]
                )

                self.current_state[y, x] = neighbor_sum / 2 - self.current_state[y, x]

                self.current_state[y, x] *= self.damping

    def _compute_next_state(self) -> None:
        """Compute the next state with the propagate mode from the configuration."""
        if self.propagate_mode == "numba":
            super()._compute_next_state()
        elif self.propagate_mode == "numpy":
            self._propagate_with_numpy()
        else:
            self._propagate_iterative()

    def _map_state_to_rgb(self, mode: str) -> np.ndarray:
        """Map the current state to an RGB array of shape (rows, cols, 3).

        Args:
            mode (str): "grayscale" stacks the state into three channels. "colormap" uses the full
                colormap. "scaled_colormap" uses a colormap that keeps the darkest color lighter.

        Returns:
            rgb_array (np.ndarray): A uint8 array of shape (rows, cols, 3).
        """
        if mode == "grayscale":
            clipped_state = np.clip(self.current_state, 0, 255).astype(np.float32)
            stacked_state = np.stack([clipped_state] * 3, axis=-1)
            rgb_array = stacked_state.astype(np.uint8)
        elif mode == "colormap":
            rgb_array = colorize(
                state=self.current_state,
                maximum_brightness=self.maximum_brightness,
                floor=0.0,
                span=1.0,
            )
        else:
            rgb_array = colorize(
                state=self.current_state,
                maximum_brightness=self.maximum_brightness,
                floor=0.1,
                span=0.8,
            )

        return rgb_array

    def _render_state(self, rgb_array: np.ndarray, mode: str) -> None:
        """Render an RGB array onto the window.

        Args:
            rgb_array (np.ndarray): A uint8 array of shape (rows, cols, 3).
            mode (str): "surfarray" blits the whole array at once. "rectangle" draws each cell.
        """
        if mode == "surfarray":
            transposed_array = rgb_array.swapaxes(0, 1)
            surface = pg.surfarray.make_surface(transposed_array)
            scaled_surface = pg.transform.scale(
                surface, (self.window_width, self.window_height)
            )
            self.screen.blit(scaled_surface, (0, 0))
        else:
            for y in range(len(rgb_array)):
                for x in range(len(rgb_array[y])):
                    color = tuple(rgb_array[y, x])
                    rect = pg.Rect(
                        x * self.grid_cell_width,
                        y * self.grid_cell_height,
                        self.grid_cell_width,
                        self.grid_cell_height,
                    )
                    pg.draw.rect(self.screen, color, rect)

    def _mouse_to_grid(self, mx: int, my: int) -> tuple[int, int] | None:
        """Convert a mouse pixel position to a grid cell of the uniform grid.

        Args:
            mx (int): The x pixel position of the mouse.
            my (int): The y pixel position of the mouse.

        Returns:
            grid_position (tuple[int, int] | None): The (column, row) under the mouse.
        """
        grid_x = mx // self.grid_cell_width
        grid_y = my // self.grid_cell_height
        grid_position = (grid_x, grid_y)

        return grid_position

    def _draw_frame(self) -> None:
        """Draw the current state onto the window."""
        rgb_array = self._map_state_to_rgb(mode=self.rgb_mode)
        self._render_state(rgb_array=rgb_array, mode=self.render_mode)
