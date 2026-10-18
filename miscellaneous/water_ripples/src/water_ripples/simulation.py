"""Module for the shared core of the water ripple variants: state, propagation and event loop."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numba
import numpy as np
import pygame as pg

from water_ripples.config_model import ConfigModel
from water_ripples.screen import resolve_window_and_grid

_COLORMAP_NAME = "Blues_r"


@dataclass
class TrapezoidPixels:
    """Corners of the trapezoid in window pixel coordinates.

    Attributes:
        y_top (float): Pixel row where the trapezoid starts.
        y_bottom (float): Pixel row where the trapezoid ends.
        x_top_left (float): Left edge at the top.
        x_top_right (float): Right edge at the top.
        x_bottom_left (float): Left edge at the bottom.
        x_bottom_right (float): Right edge at the bottom.
    """

    y_top: float
    y_bottom: float
    x_top_left: float
    x_top_right: float
    x_bottom_left: float
    x_bottom_right: float


@numba.njit(parallel=True)
def propagate_with_numba(
    current_state: np.ndarray,
    previous_state: np.ndarray,
    damping: float,
) -> None:
    """Propagate the wave equation one step in place, using numba.

    Args:
        current_state (np.ndarray): Output grid, written in place.
        previous_state (np.ndarray): Grid of the previous step.
        damping (float): Factor that reduces the wave amplitude each step.
    """
    # numba.prange is a parallel range that ty does not model as iterable.
    for y in numba.prange(1, len(previous_state) - 1):  # ty: ignore[not-iterable]
        for x in range(1, len(previous_state[y]) - 1):
            neighbor_sum = (
                previous_state[y - 1, x]
                + previous_state[y + 1, x]
                + previous_state[y, x - 1]
                + previous_state[y, x + 1]
            )
            current_state[y, x] = neighbor_sum / 2 - current_state[y, x]
            current_state[y, x] *= damping


def colorize(
    state: np.ndarray,
    maximum_brightness: int,
    floor: float,
    span: float,
) -> np.ndarray:
    """Map a state grid to RGB colors using the Blues_r colormap.

    The normalized state is mapped to floor + span * normalized before it is looked up in the
    colormap, so floor=0.0 and span=1.0 use the full colormap, while floor=0.1 and span=0.8 keep the
    darkest color lighter.

    Args:
        state (np.ndarray): The grid of state values, clipped to [0, 255] before mapping.
        maximum_brightness (int): The value that normalizes to 1.0.
        floor (float): Position in the colormap for a state of 0.
        span (float): How much of the colormap the state range covers.

    Returns:
        rgb_array (np.ndarray): A uint8 array of shape (rows, cols, 3).
    """
    clipped_state = np.clip(state, 0, 255).astype(np.float32)
    normalized_state = clipped_state / maximum_brightness
    scaled_normalized_state = floor + span * normalized_state

    colormap = plt.get_cmap(_COLORMAP_NAME)
    rgba_colors = colormap(scaled_normalized_state)
    rgb_colors = rgba_colors[..., :3] * maximum_brightness
    rgb_array = rgb_colors.astype(np.uint8)

    return rgb_array


def clamp(value: int, lower: int, upper: int) -> int:
    """Limit an integer to the closed range [lower, upper].

    Args:
        value (int): The value to limit.
        lower (int): Smallest allowed value.
        upper (int): Largest allowed value.

    Returns:
        clamped (int): The value, limited to [lower, upper].
    """
    raised = max(lower, value)
    clamped = min(raised, upper)

    return clamped


def to_trapezoid_pixels(
    normalized: ConfigModel.Trapezoid,
    window_width: int,
    window_height: int,
) -> TrapezoidPixels:
    """Convert the normalized trapezoid to window pixel coordinates.

    Args:
        normalized (ConfigModel.Trapezoid): The trapezoid in normalized coordinates.
        window_width (int): Window width in pixels.
        window_height (int): Window height in pixels.

    Returns:
        trapezoid_pixels (TrapezoidPixels): The trapezoid in pixel coordinates.
    """
    trapezoid_pixels = TrapezoidPixels(
        y_top=normalized.y_top * window_height,
        y_bottom=normalized.y_bottom * window_height,
        x_top_left=normalized.x_top_left * window_width,
        x_top_right=normalized.x_top_right * window_width,
        x_bottom_left=normalized.x_bottom_left * window_width,
        x_bottom_right=normalized.x_bottom_right * window_width,
    )

    return trapezoid_pixels


class RippleSimulation(ABC):
    """Base class for the 2D water ripple variants.

    The simulation keeps two grids (previous_state and current_state). Each step propagates the
    previous grid into the current one, and then the two are swapped. Subclasses decide how the
    mouse maps to the grid and how the state is drawn.

    Attributes:
        window_width (int): Window width in pixels.
        window_height (int): Window height in pixels.
        number_of_columns (int): Number of columns in the simulation grid.
        number_of_rows (int): Number of rows in the simulation grid.
        grid_cell_width (int): Width of one grid cell in pixels, for a uniform grid.
        grid_cell_height (int): Height of one grid cell in pixels, for a uniform grid.
        damping (float): Factor that reduces the wave amplitude each step.
        wave_brightness (int): Intensity of a splash.
        maximum_brightness (int): Maximum brightness the visualization shows.
        cursor_splash_size (int): Half-width of the disturbed square under the cursor.
        framerate (int): Target frames per second.
        background_color (tuple[int, int, int]): Background color of the canvas.
        current_state (np.ndarray): The grid written by the current step.
        previous_state (np.ndarray): The grid read by the current step.
        screen (pg.Surface): The PyGame window surface.
        clock (pg.time.Clock): Used to enforce the framerate.
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initialize the grid, the splash and the PyGame window.

        Args:
            config (ConfigModel): The validated configuration.
        """
        window_width, window_height, number_of_rows = resolve_window_and_grid(
            window_width=config.window.window_width,
            window_height=config.window.window_height,
            number_of_columns=config.simulation.number_of_columns,
            number_of_rows=None,
        )

        self.window_width = window_width
        self.window_height = window_height
        self.number_of_columns = config.simulation.number_of_columns
        self.number_of_rows = number_of_rows
        self.grid_cell_width = int(window_width / self.number_of_columns)
        self.grid_cell_height = int(window_height / number_of_rows)

        self.damping = config.simulation.damping
        self.wave_brightness = config.simulation.wave_brightness
        self.maximum_brightness = config.simulation.maximum_brightness
        self.cursor_splash_size = config.simulation.cursor_splash_size
        self.framerate = config.simulation.framerate
        self.background_color = config.simulation.background_color

        grid_shape = (self.number_of_rows, self.number_of_columns)
        self.current_state: np.ndarray = np.zeros(grid_shape, dtype=np.float32)
        self.previous_state: np.ndarray = np.zeros(grid_shape, dtype=np.float32)

        center_row = self.number_of_rows // 2
        center_column = self.number_of_columns // 2
        self.previous_state[center_row, center_column] = self.wave_brightness

        pg.init()
        self.screen = pg.display.set_mode((window_width, window_height))
        self.clock = pg.time.Clock()

    def _compute_next_state(self) -> None:
        """Compute the next state into current_state, using numba."""
        propagate_with_numba(
            current_state=self.current_state,
            previous_state=self.previous_state,
            damping=self.damping,
        )

    def _propagate(self) -> None:
        """Advance the simulation one step and swap the two grids."""
        self._compute_next_state()

        self.current_state, self.previous_state = (
            self.previous_state,
            self.current_state,
        )

    def _splash(self, grid_x: int, grid_y: int) -> None:
        """Disturb a square of cells around a grid cell, clear of the border.

        Args:
            grid_x (int): Column of the cell at the center of the splash.
            grid_y (int): Row of the cell at the center of the splash.
        """
        row_start = max(grid_y - self.cursor_splash_size, 1)
        row_end = min(grid_y + self.cursor_splash_size, self.number_of_rows - 1)
        column_start = max(grid_x - self.cursor_splash_size, 1)
        column_end = min(grid_x + self.cursor_splash_size, self.number_of_columns - 1)

        self.previous_state[row_start:row_end, column_start:column_end] = (
            self.wave_brightness
        )

    @abstractmethod
    def _mouse_to_grid(self, mx: int, my: int) -> tuple[int, int] | None:
        """Convert a mouse pixel position to a grid cell.

        Args:
            mx (int): The x pixel position of the mouse.
            my (int): The y pixel position of the mouse.

        Returns:
            grid_position (tuple[int, int] | None): The (column, row) under the mouse, or None if
                the mouse is outside the simulated area.
        """

    def _handle_mouse(self) -> None:
        """Create a disturbance at the mouse position while the left button is held."""
        mx, my = pg.mouse.get_pos()
        grid_position = self._mouse_to_grid(mx=mx, my=my)

        if grid_position is None:
            return

        grid_x, grid_y = grid_position
        self._splash(grid_x=grid_x, grid_y=grid_y)

    @abstractmethod
    def _draw_frame(self) -> None:
        """Draw the current state onto the window."""

    def execute(self) -> None:
        """Run the simulation loop until the window is closed or ESC is pressed.

        Each frame handles input, advances the simulation, draws it, and enforces the framerate.
        """
        running = True

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False

            if pg.mouse.get_pressed()[0]:
                self._handle_mouse()

            self._propagate()
            self._draw_frame()

            pg.display.flip()
            self.clock.tick(self.framerate)

        pg.quit()
