"""Module that simulates 2D water ripples using PyGame."""

# Imports
import numba
import pygame as pg
import numpy as np
import matplotlib.pyplot as plt

# Size and dimension related parameters
WINDOW_WIDTH = 4000
WINDOW_HEIGHT = 2500
NUMBER_OF_COLUMNS = 1000
NUMBER_OF_ROWS = int(NUMBER_OF_COLUMNS * (WINDOW_HEIGHT / WINDOW_WIDTH))

# Algorithm related parameters
DAMPING = 0.99
WAVE_BRIGHTNESS = 255
MAXIMUM_BRIGHTNESS = 255
CURSOR_SPLASH_SIZE = 5
FRAMERATE = 25
BACKGROUND_COLOR = (0, 0, 0)


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
        window_width: int = WINDOW_WIDTH,
        window_height: int = WINDOW_HEIGHT,
        number_of_columns: int = NUMBER_OF_COLUMNS,
        number_of_rows: int = NUMBER_OF_ROWS,
        damping: float = DAMPING,
        wave_brightness: int = WAVE_BRIGHTNESS,
        maximum_brightness: int = MAXIMUM_BRIGHTNESS,
        cursor_splash_size: int = CURSOR_SPLASH_SIZE,
        framerate: int = FRAMERATE,
        background_color: tuple[int, int, int] = BACKGROUND_COLOR,
    ) -> None:
        """
        Initialize the ripple simulation class.

        The simulation maintains two grids (previous_state and current_state).
        At each step, values propagate from the previous grid to the current
        grid, and then the grids are swapped.

        Args:
            window_width: Width of the PyGame window in pixels.
            window_height: Height of the PyGame window in pixels.
            number_of_columns: Number of columns in the simulation grid.
            number_of_rows: Number of rows in the simulation grid.
            damping: Factor between 0 and 1 that reduces wave amplitude each
                frame.
            wave_brightness: Intensity value for the waves.
            maximum_brightness: Maximum brightness the visualization can display.
            cursor_splash_size: The size of the splash when clicking.
            framerate: Target framerate. Units: frames / second.
            background_color: The background color of the canvas.
        """
        self.window_width = window_width
        self.window_height = window_height
        self.number_of_columns = number_of_columns
        self.number_of_rows = number_of_rows
        self.damping = damping
        self.wave_brightness = wave_brightness
        self.maximum_brightness = maximum_brightness
        self.cursor_splash_size = cursor_splash_size
        self.framerate = framerate
        self.background_color = background_color

        self.grid_cell_width = int(self.window_width / number_of_columns)
        self.grid_cell_height = int(self.window_height / number_of_rows)

        self.current_state = np.zeros(
            (number_of_rows, number_of_columns), dtype=np.float32
        )
        self.previous_state = np.zeros(
            (number_of_rows, number_of_columns), dtype=np.float32
        )

        self.previous_state[number_of_rows // 2, number_of_columns // 2] = (
            self.wave_brightness
        )

        self.row_pixel_positions = self._compute_row_pixel_positions()

        pg.init()
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        self.clock = pg.time.Clock()
    
    def _compute_row_pixel_positions(self) -> list[tuple[int, int]]:
        """
        Computes the top and bottom pixel position for each row,
        with smaller rows at the top (far away) and larger rows at the bottom (close).

        Returns:
            List of (y_top, y_bottom) tuples in pixels, one per row.
        """
        PERSPECTIVE_EXPONENT = 3
        weights = [(i + 1) ** PERSPECTIVE_EXPONENT for i in range(self.number_of_rows)]
        total_weight = sum(weights)

        row_heights = [max(1, int(w / total_weight * self.window_height)) for w in weights]
        row_heights[-1] += self.window_height - sum(row_heights)

        positions = []
        y_top = 0
        for height in row_heights:
            positions.append((y_top, y_top + height))
            y_top += height

        return positions
    
    def _mouse_y_to_grid_y(self, my: int) -> int:
        """Find the grid row corresponding to a mouse y pixel position."""
        for grid_y, (y_top, y_bottom) in enumerate(self.row_pixel_positions):
            if y_top <= my < y_bottom:
                return grid_y
        return self.number_of_rows - 1

    def _handle_mouse(self) -> None:
        """Create a disturbance at the current mouse position."""
        mx, my = pg.mouse.get_pos()
        grid_x = mx // self.grid_cell_width
        grid_y = self._mouse_y_to_grid_y(my)

        self.previous_state[
            max(grid_y - self.cursor_splash_size, 1) : min(
                grid_y + self.cursor_splash_size, self.number_of_rows - 1
            ),
            max(grid_x - self.cursor_splash_size, 1) : min(
                grid_x + self.cursor_splash_size, self.number_of_columns - 1
            ),
        ] = self.wave_brightness

    def _map_state_to_rgba(self) -> np.ndarray:
        """Maps the current state to an RGBA array."""
        current_state_clipped = np.clip(self.current_state, 0, 255).astype(np.float32)
        normalized_state = current_state_clipped / self.maximum_brightness
        colormap = plt.get_cmap("hot")

        scaled_normalized_state = 0.0 + 1.0 * normalized_state
        rgb_array = (
            colormap(scaled_normalized_state)[..., :3] * self.maximum_brightness
        ).astype(np.uint8)

        #alpha_array = (normalized_state * 255).astype(np.uint8)
        alpha_array = np.full_like(normalized_state, 255, dtype=np.uint8)
        return np.concatenate([rgb_array, alpha_array[..., np.newaxis]], axis=-1)


    def _render_state(self, rgba_array: np.ndarray) -> None:
        """Render the current RGBA state onto the PyGame screen."""
        self.screen.fill(self.background_color)

        for y, (y_top, y_bottom) in enumerate(self.row_pixel_positions):
            row_height = y_bottom - y_top

            if row_height <= 0:
                continue

            row_rgba = rgba_array[y]

            row_surface = pg.Surface((self.number_of_columns, 1), pg.SRCALPHA)
            pg.surfarray.pixels3d(row_surface)[:, 0, :] = row_rgba[:, :3]
            pg.surfarray.pixels_alpha(row_surface)[:, 0] = row_rgba[:, 3]

            row_surface = pg.transform.scale(
                row_surface, (self.window_width, row_height)
            )

            self.screen.blit(row_surface, (0, y_top))

    def _draw_current_state(self) -> None:
        """Render the current simulation state to the PyGame window."""
        rgba_array = self._map_state_to_rgba()
        self._render_state(rgba_array=rgba_array)

    def execute(self) -> None:
        """Run the simulation loop until the user exits."""
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

            self._draw_current_state()

            pg.display.flip()
            self.clock.tick(self.framerate)

        pg.quit()


water_ripples = WaterRipples()
water_ripples.execute()