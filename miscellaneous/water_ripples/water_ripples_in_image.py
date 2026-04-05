"""Module that simulates 2D water ripples using PyGame."""

# Imports
import os

os.environ["NUMBA_CPU_NAME"] = (
    "generic"  # Make sure it works for different architectures.
)

import numba
import pygame as pg
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path

from constants import (
    BACKGROUND_COLOR,
    CURSOR_SPLASH_SIZE,
    DAMPING,
    FRAMERATE,
    IMAGE_PATH,
    MASK_PATH,
    MAXIMUM_BRIGHTNESS,
    NORMALIZED_TRAPEZOID,
    NUMBER_OF_COLUMNS,
    WAVE_BRIGHTNESS,
)
from utils_screen import resolve_window_and_grid


# Functions.


@numba.njit(parallel=True)
def propagate_with_numba(
    current_state: np.ndarray,
    previous_state: np.ndarray,
    damping: float,
) -> None:
    """In-place wave propagation using numba."""
    for y in numba.prange(1, len(previous_state) - 1):
        for x in range(1, len(previous_state[y]) - 1):
            neighbor_sum = (
                previous_state[y - 1, x]
                + previous_state[y + 1, x]
                + previous_state[y, x - 1]
                + previous_state[y, x + 1]
            )
            current_state[y, x] = neighbor_sum / 2 - current_state[y, x]
            current_state[y, x] *= damping


# Classes.


class WaterRipples:
    """Simulation of 2D water ripples using a discrete wave equation."""

    def __init__(
        self,
        window_width: int | None = None,
        window_height: int | None = None,
        number_of_columns: int = NUMBER_OF_COLUMNS,
        number_of_rows: int | None = None,
        damping: float = DAMPING,
        wave_brightness: int = WAVE_BRIGHTNESS,
        maximum_brightness: int = MAXIMUM_BRIGHTNESS,
        cursor_splash_size: int = CURSOR_SPLASH_SIZE,
        framerate: int = FRAMERATE,
        background_color: tuple[int, int, int] = BACKGROUND_COLOR,
        normalized_trapezoid: dict = NORMALIZED_TRAPEZOID,
        image_path: Path = IMAGE_PATH,
        mask_path: Path = MASK_PATH,
    ) -> None:
        """
        Initialize the ripple simulation class.

        The simulation maintains two grids (previous_state and current_state).
        At each step, values propagate from the previous grid to the current
        grid, and then the grids are swapped.

        Args:
            window_width: Window width in pixels, or None for ~90% of desktop
                (windowed).
            window_height: Window height in pixels, or None with window_width.
            number_of_columns: Number of columns in the simulation grid.
            number_of_rows: Number of rows, or None for aspect-matched grid.
            damping: Factor between 0 and 1 that reduces wave amplitude each
                frame.
            wave_brightness: Intensity value for the waves.
            maximum_brightness: Maximum brightness the visualization can display.
            cursor_splash_size: The size of the splash when clicking.
            framerate: Target framerate. Units: frames / second.
            background_color: The background color of the canvas.
            normalized_trapezoid: Normalized coordinates of the trapezoid.
            perspective_exponent: Controls the strength of the perspective effect.
            image_path: Path to the background image.
            mask_path: Path to the precomputed lake mask.
        """
        window_width, window_height, number_of_rows = resolve_window_and_grid(
            window_width,
            window_height,
            number_of_columns,
            number_of_rows,
        )

        # Window and grid related settings.
        self.window_width = window_width
        self.window_height = window_height
        self.number_of_columns = number_of_columns
        self.number_of_rows = number_of_rows
        self.grid_cell_width = int(self.window_width / number_of_columns)
        self.grid_cell_height = int(self.window_height / number_of_rows)

        # Algorithm related parameters.
        self.damping = damping
        self.wave_brightness = wave_brightness
        self.maximum_brightness = maximum_brightness
        self.cursor_splash_size = cursor_splash_size
        self.framerate = framerate
        self.background_color = background_color

        # Initialize algorithmic state with a single splash at the start.
        self.current_state: np.ndarray = np.zeros(
            (number_of_rows, number_of_columns), dtype=np.float32
        )
        self.previous_state: np.ndarray = np.zeros(
            (number_of_rows, number_of_columns), dtype=np.float32
        )
        self.previous_state[number_of_rows // 2, number_of_columns // 2] = (
            self.wave_brightness
        )

        # Trapezoid related parameters.
        self.normalized_trapezoid = normalized_trapezoid
        self.trapezoid = {
            key: (
                value * self.window_height
                if key.startswith("y")
                else value * self.window_width
            )
            for key, value in normalized_trapezoid.items()
        }

        # Image related variables.
        self.image_path = image_path
        self.mask_path = mask_path

        # Initialize PyGame.
        pg.init()
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        self.clock = pg.time.Clock()

        # Load background image and mask.
        self.background_image = pg.image.load(self.image_path).convert()
        self.background_image = pg.transform.scale(
            self.background_image, (self.window_width, self.window_height)
        )
        self.mask = np.load(self.mask_path)

    def _compute_vertical_scaling(self, y: float, y_start: float = 0.5) -> float:
        """
        Maps grid row index y to a scaled y_adjusted value using perspective
        foreshortening.

        The formula is quadratic in y, meaning rows further down the grid get
        a disproportionately larger y_adjusted value than rows near the top.
        This causes rows to appear taller toward the bottom of the trapezoid
        and shorter toward the top, simulating the look of a surface receding
        into the distance.

        The y_start parameter controls the strength of the perspective effect:

        y_start = 0.0: No perspective — all rows get equal height, completely flat.
        y_start = 0.1: Very subtle perspective, barely noticeable.
        y_start = 0.5: Moderate perspective, good default for a natural look.
        y_start = 1.0: Strong perspective — rows at the bottom are noticeably
            larger than rows at the top.
        y_start > 1.0: Very heavy perspective — top rows become extremely
            compressed, can look unrealistic.

        Args:
            y: Grid row index, starting at 0 for the top row.
            y_start: Controls the strength of the perspective foreshortening.

        Returns:
            A scaled float value representing the projected position of row y.
        """
        y_scaling_factor = y_start / self.number_of_rows * 2
        return y * y_start + (y * (y + 1) / 2) * y_scaling_factor

    def _inverse_vertical_scaling(
        self, y_adjusted: float, y_start: float = 0.5
    ) -> float:
        """
        Given a projected screen position y_adjusted, returns the grid row y
        that produces it — i.e. the inverse of _compute_vertical_scaling.

        This is needed to convert a mouse y pixel position back to a grid row
        index when the user clicks or drags on the trapezoid. Since
        _compute_vertical_scaling is a quadratic function of y, its inverse
        is derived analytically using the quadratic formula. We always take
        the positive root since grid row indices are non-negative.

        Args:
            y_adjusted: The projected screen position to invert.
            y_start: Must match the value used in _compute_vertical_scaling.

        Returns:
            The grid row index y that maps to y_adjusted under
            _compute_vertical_scaling.
        """
        s = y_start / self.number_of_rows * 2
        a = s / 2
        b = y_start + s / 2
        discriminant = b**2 + 4 * a * y_adjusted
        y = (-b + np.sqrt(discriminant)) / (2 * a)
        return y

    def _mouse_y_to_grid_y(self, my: int) -> int | None:
        """
        Convert a mouse y pixel position to a grid row index.

        First checks whether the mouse is within the vertical bounds of the
        trapezoid — if not, returns None to signal that the click should be
        ignored. Otherwise, normalizes the mouse position into the vertical
        space that _compute_vertical_scaling operates in, then applies the
        analytical inverse to find the corresponding grid row index.

        Args:
            my: The y pixel position of the mouse in the pygame window.

        Returns:
            The grid row index corresponding to the mouse y position,
            or None if the mouse is outside the trapezoid bounds.
        """
        if my < self.trapezoid["y_top"] or my > self.trapezoid["y_bottom"]:
            return None

        scaled_grid_cell_height = self.grid_cell_height * (
            self.normalized_trapezoid["y_bottom"] - self.normalized_trapezoid["y_top"]
        )
        y_adjusted = (my - self.trapezoid["y_top"]) / scaled_grid_cell_height
        grid_y = int(self._inverse_vertical_scaling(y_adjusted=y_adjusted))
        return max(0, min(grid_y, self.number_of_rows - 1))

    def _mouse_x_to_grid_x(self, mx: int, grid_y: int) -> int:
        """
        Convert a mouse x pixel position to a grid column index.

        Uses the given grid row index to look up the x boundaries of that row
        via _compute_vertical_scaling and trapezoid interpolation, then
        interpolates the column position within those boundaries. The result
        is clamped to stay within valid grid column indices.

        Args:
            mx: The x pixel position of the mouse in the pygame window.
            grid_y: The grid row index, needed to determine that row's x boundaries.

        Returns:
            The grid column index corresponding to the mouse x position.
        """
        y_adj = self._compute_vertical_scaling(y=grid_y)
        x_left = self.trapezoid["x_top_left"] + (
            self.normalized_trapezoid["x_bottom_left"]
            - self.normalized_trapezoid["x_top_left"]
        ) * y_adj * (self.window_height / self.number_of_rows)
        x_right = self.trapezoid["x_top_right"] + (
            self.normalized_trapezoid["x_bottom_right"]
            - self.normalized_trapezoid["x_top_right"]
        ) * y_adj * (self.window_height / self.number_of_rows)
        grid_x = int((mx - x_left) / (x_right - x_left) * self.number_of_columns)
        return max(0, min(grid_x, self.number_of_columns - 1))

    def _handle_mouse(self) -> None:
        """
        Create a disturbance at the current mouse position.

        Converts the mouse position to grid coordinates using _mouse_y_to_grid_y
        and _mouse_x_to_grid_x, then disturbs a square region of size
        cursor_splash_size around that grid cell. Returns early if the mouse
        is outside the trapezoid bounds. The disturbance is clamped to stay
        within the grid boundaries so that border cells, which are always kept
        at zero to prevent waves from leaking out, are never disturbed.
        """
        mx, my = pg.mouse.get_pos()

        grid_y = self._mouse_y_to_grid_y(my)
        if grid_y is None:
            return

        grid_x = self._mouse_x_to_grid_x(mx, grid_y)

        self.previous_state[
            max(grid_y - self.cursor_splash_size, 1) : min(
                grid_y + self.cursor_splash_size, self.number_of_rows - 1
            ),
            max(grid_x - self.cursor_splash_size, 1) : min(
                grid_x + self.cursor_splash_size, self.number_of_columns - 1
            ),
        ] = self.wave_brightness

    def _map_state_to_rgba(self) -> np.ndarray:
        """
        Maps the current state to an RGBA array of shape (rows, cols, 4).

        The current state values are clipped to [0, 255] and normalized to
        [0.0, 1.0] before being passed through a matplotlib colormap to produce
        RGB values. The colormap converts each scalar grid value to a color,
        giving waves a visual appearance beyond simple grayscale.

        The alpha channel is set proportional to wave intensity — flat water
        is fully transparent and only active waves are visible, which allows
        the background image to show through where there are no waves.

        Returns:
            A numpy array of shape (rows, cols, 4) with dtype uint8, containing
            RGBA values in the range [0, 255].
        """
        current_state_clipped = np.clip(self.current_state, 0, 255).astype(np.float32)
        normalized_state = current_state_clipped / self.maximum_brightness
        colormap = plt.get_cmap("Blues_r")
        scaled_normalized_state = 0.1 + 0.8 * normalized_state
        rgb_array = (
            colormap(scaled_normalized_state)[..., :3] * self.maximum_brightness
        ).astype(np.uint8)
        alpha_array = (normalized_state * 255).astype(np.uint8)
        return np.concatenate([rgb_array, alpha_array[..., np.newaxis]], axis=-1)

    def _render_state(self, rgba_array: np.ndarray) -> None:
        """
        Render the current RGBA state onto the PyGame screen using per-cell
        polygon drawing.

        For each grid cell, a quadrilateral is computed whose four corners are
        derived from the trapezoid geometry and vertical scaling. The top edge
        of the cell uses the x boundaries of row y, and the bottom edge uses
        the x boundaries of row y+1 — both interpolated from the trapezoid's
        normalized coordinates. This means cells narrow toward the top of the
        trapezoid and widen toward the bottom, creating the perspective effect.

        Before drawing, the center pixel of each cell is checked against the
        lake mask. Cells whose center falls outside the mask are skipped, so
        the wave overlay only appears on the lake and not on surrounding terrain.

        All cells are drawn onto a transparent SRCALPHA overlay surface rather
        than directly onto the screen. This allows the alpha channel of each
        cell — which is proportional to wave intensity — to blend correctly
        with the background image underneath. Flat water has alpha 0 and is
        fully transparent, while active wave peaks have alpha 255 and are
        fully visible. The overlay is blitted onto the screen at the end.

        Args:
            rgba_array: A numpy array of shape (rows, cols, 4) with dtype uint8,
                containing the RGBA values to render for each grid cell.
        """
        overlay = pg.Surface((self.window_width, self.window_height), pg.SRCALPHA)

        for y in range(self.number_of_rows):
            y_adj = self._compute_vertical_scaling(y=y)
            y_adj_plus_one = self._compute_vertical_scaling(y=y + 1)

            for x in range(self.number_of_columns):
                x_left_top = self.trapezoid["x_top_left"] + (
                    self.normalized_trapezoid["x_bottom_left"]
                    - self.normalized_trapezoid["x_top_left"]
                ) * y_adj * (self.window_height / self.number_of_rows)
                x_right_top = self.trapezoid["x_top_right"] + (
                    self.normalized_trapezoid["x_bottom_right"]
                    - self.normalized_trapezoid["x_top_right"]
                ) * y_adj * (self.window_height / self.number_of_rows)
                x_left_bottom = self.trapezoid["x_top_left"] + (
                    self.normalized_trapezoid["x_bottom_left"]
                    - self.normalized_trapezoid["x_top_left"]
                ) * y_adj_plus_one * (self.window_height / self.number_of_rows)
                x_right_bottom = self.trapezoid["x_top_right"] + (
                    self.normalized_trapezoid["x_bottom_right"]
                    - self.normalized_trapezoid["x_top_right"]
                ) * y_adj_plus_one * (self.window_height / self.number_of_rows)

                scaled_grid_cell_width_top = (
                    x_right_top - x_left_top
                ) / self.number_of_columns
                scaled_grid_cell_width_bottom = (
                    x_right_bottom - x_left_bottom
                ) / self.number_of_columns
                scaled_grid_cell_height = self.grid_cell_height * (
                    self.normalized_trapezoid["y_bottom"]
                    - self.normalized_trapezoid["y_top"]
                )

                x_cell_top = x_left_top + x * scaled_grid_cell_width_top
                y_cell_top = self.trapezoid["y_top"] + y_adj * scaled_grid_cell_height
                x_cell_bottom = x_left_bottom + x * scaled_grid_cell_width_bottom
                y_cell_bottom = (
                    self.trapezoid["y_top"] + y_adj_plus_one * scaled_grid_cell_height
                )

                cx = int(x_cell_top + scaled_grid_cell_width_top / 2)
                cy = int((y_cell_top + y_cell_bottom) / 2)
                cx = max(0, min(cx, self.window_width - 1))
                cy = max(0, min(cy, self.window_height - 1))
                if not self.mask[cy, cx]:
                    continue

                color_rgba = tuple(rgba_array[y, x])

                pg.draw.polygon(
                    overlay,
                    color_rgba,
                    [
                        (x_cell_top, y_cell_top),
                        (x_cell_top + scaled_grid_cell_width_top, y_cell_top),
                        (x_cell_bottom + scaled_grid_cell_width_bottom, y_cell_bottom),
                        (x_cell_bottom, y_cell_bottom),
                    ],
                )

        self.screen.blit(overlay, (0, 0))

    def _draw_current_state(self) -> None:
        """
        Render the current simulation state to the PyGame window.

        This method acts as a thin coordinator between the two steps of
        visualization: converting the simulation state to an RGBA array via
        _map_state_to_rgba, and then rendering that array onto the screen via
        _render_state.
        """
        rgba_array = self._map_state_to_rgba()
        self._render_state(rgba_array=rgba_array)

    def execute(self) -> None:
        """
        Run the simulation loop until the user exits.

        Each frame, mouse input is checked, the wave equation is propagated
        one step forward using numba, the two state buffers are swapped, and
        the current state is rendered to the screen. The clock tick at the end
        of each frame enforces the target framerate. The loop exits when the
        user closes the window or presses ESC, after which pygame is cleaned up.
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

            propagate_with_numba(
                current_state=self.current_state,
                previous_state=self.previous_state,
                damping=self.damping,
            )
            self.current_state, self.previous_state = (
                self.previous_state,
                self.current_state,
            )

            self.screen.blit(self.background_image, (0, 0))
            self._draw_current_state()

            pg.display.flip()
            self.clock.tick(self.framerate)

        pg.quit()


water_ripples = WaterRipples()
water_ripples.execute()
