"""Module that simulates 2D water ripples using PyGame."""

# Imports
import numba
import pygame as pg
import numpy as np
import matplotlib.pyplot as plt

# Size and dimension related parameters
WINDOW_WIDTH = 4000
WINDOW_HEIGHT = 2500
NUMBER_OF_COLUMNS = 300
NUMBER_OF_ROWS = int(NUMBER_OF_COLUMNS * (WINDOW_HEIGHT / WINDOW_WIDTH))

# Algorithm related parameters
DAMPING = 0.99
WAVE_BRIGHTNESS = 255
MAXIMUM_BRIGHTNESS = 255
CURSOR_SPLASH_SIZE = 2
FRAMERATE = 60
BACKGROUND_COLOR = (0, 0, 0)

# Trapezoid related parameters.
"""
This variable defines the normalized coordinates of a trapezoid.
A trapezoid is a four-side polygon with at least one pair of parallel sides, known as the bases. In
our case the parallel sides are the two horizontal lines.

- For 'y', 0 corresponds with top of the window, 1 would be the bottom of the window.
- For 'x', 0 corresponds with the left side of the window, 1 would be the right side.
"""
NORMALIZED_TRAPEZOID: dict = {
    "y_top": 0.2,
    "y_bottom": 0.8,
    "x_top_left": 0.6,
    "x_top_right": 0.8,
    "x_bottom_left": 0,
    "x_bottom_right": 1,
}

"""
This variable determines the 'amount' of persective you see in the trapezoid window

Exponent = 0: Completely flat, no perspective at all.
Exponent = 1 (linear): Equal distribution — every row gets progressively a little taller than the 
    previous, but the difference between rows is constant. Not much perspective feel.
Exponent = 2 (quadratic): Moderate perspective — rows grow noticeably faster toward the bottom.
Exponent = 3 (cubic): Strong perspective — rows at the bottom are much taller than rows at the top. 
Exponent > 3: Very heavy perspective — the top rows become extremely compressed, almost invisible, 
    and the bottom rows dominate. Can look unrealistic.
"""
PERSPECTIVE_EXPONENT = 1


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
        normalized_trapezoid: dict = NORMALIZED_TRAPEZOID,
        perspective_exponent: float = PERSPECTIVE_EXPONENT,
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
        # Window and grid related settings:
        self.window_width = window_width
        self.window_height = window_height
        self.number_of_columns = number_of_columns
        self.number_of_rows = number_of_rows
        self.grid_cell_width = int(self.window_width / number_of_columns)

        # Algortihm related parameters.
        self.damping = damping
        self.wave_brightness = wave_brightness
        self.maximum_brightness = maximum_brightness
        self.cursor_splash_size = cursor_splash_size
        self.framerate = framerate
        self.background_color = background_color

        # Intialize algorithmic state with a single splash at the start.
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
        self.perspective_exponent = perspective_exponent

        self.row_geometry = self._compute_row_geometry()

        pg.init()
        self.screen = pg.display.set_mode((self.window_width, self.window_height))
        self.clock = pg.time.Clock()

    def _compute_row_geometry(self) -> list[dict]:
        """
        Precomputes pixel geometry for each row — y position and x boundaries.
        Both are derived from the same vertical scaling, ensuring consistency.

        The perspective effect is achieved by assigning each row a weight of
        (i + 1) ** perspective_exponent, where i is the row index. This means
        rows at the bottom get a larger weight and therefore more pixels in the
        y direction than rows at the top, simulating depth. An exponent of 0
        gives equal row heights, 1 is linear, 2 is quadratic, and so on — the
        higher the exponent, the more dramatic the perspective effect.

        These weights are converted to normalized boundary positions t_values,
        where t is an interpolation parameter running from 0.0 (top of the
        trapezoid) to 1.0 (bottom of the trapezoid). Each t value represents
        how far along the trapezoid a row boundary sits. These t values are
        then used to interpolate both the y pixel positions and the x boundaries
        of each row within the trapezoid.

        The result is stored in geometry — a list of dicts, one per row, each
        containing the pixel coordinates of that row's bounding rectangle:
        - y_top: top pixel position of the row in the pygame window
        - y_bottom: bottom pixel position of the row in the pygame window
        - x_left: left pixel position of the row, interpolated between
            x_top_left and x_bottom_left of the trapezoid
        - x_right: right pixel position of the row, interpolated between
            x_top_right and x_bottom_right of the trapezoid

        This is computed once at startup and reused every frame, so there are
        no geometry calculations in the main loop.

        Returns:
            gemeotry (list): List of dicts with keys y_top, y_bottom, x_left, x_right per row,
            in pixel coordinates relative to the pygame window.
        """
        weights = [
            (i + 1) ** self.perspective_exponent for i in range(self.number_of_rows)
        ]
        total_weight = sum(weights)

        cumulative = 0.0
        t_values = [0.0]
        for w in weights:
            cumulative += w / total_weight
            t_values.append(cumulative)

        trapezoid_height = self.trapezoid["y_bottom"] - self.trapezoid["y_top"]

        geometry = []
        for y in range(self.number_of_rows):
            t_top = t_values[y]
            t_bottom = t_values[y + 1]

            y_top = int(self.trapezoid["y_top"] + t_top * trapezoid_height)
            y_bottom = int(self.trapezoid["y_top"] + t_bottom * trapezoid_height)

            x_left = int(
                self.trapezoid["x_top_left"]
                + (self.trapezoid["x_bottom_left"] - self.trapezoid["x_top_left"])
                * t_top
            )
            x_right = int(
                self.trapezoid["x_top_right"]
                + (self.trapezoid["x_bottom_right"] - self.trapezoid["x_top_right"])
                * t_top
            )

            geometry.append(
                {
                    "y_top": y_top,
                    "y_bottom": y_bottom,
                    "x_left": x_left,
                    "x_right": x_right,
                }
            )

        geometry[-1]["y_bottom"] = int(self.trapezoid["y_bottom"])

        return geometry

    def _mouse_x_to_grid_x(self, mx: int, grid_y: int) -> int:
        """
        Find the grid column corresponding to a mouse x pixel position.

        This method is needed because the grid columns are not uniformly distributed
        over the pygame window — due to the trapezoid shape, each row has its own
        x_left and x_right boundaries. A simple division like `mx // grid_cell_width`
        would only work if the grid spanned the full window width uniformly. Instead,
        we look up the x boundaries of the given row from row_geometry and interpolate
        the column position within those boundaries. The result is clamped to stay
        within valid grid column indices.

        Args:
            mx: The x pixel position of the mouse in the pygame window.
            grid_y: The grid row index, needed to look up that row's x boundaries.

        Returns:
            The grid column index corresponding to the mouse x position.
        """
        geom = self.row_geometry[grid_y]
        x_left = geom["x_left"]
        x_right = geom["x_right"]
        grid_x = int((mx - x_left) / (x_right - x_left) * self.number_of_columns)
        return max(0, min(grid_x, self.number_of_columns - 1))

    def _mouse_y_to_grid_y(self, my: int) -> int:
        """
        Find the grid row corresponding to a mouse y pixel position.

        This method is needed because the grid rows are not uniformly distributed
        over the pygame window — due to the perspective scaling, rows at the top
        are smaller and rows at the bottom are larger. A simple division like
        `my // grid_cell_height` would only work if all rows had equal height.
        Instead, we look up which row's pixel range contains the mouse y position
        using the precomputed row_geometry. If the mouse is below all rows, we
        clamp to the last row.

        Args:
            my: The y pixel position of the mouse in the pygame window.

        Returns:
            The grid row index corresponding to the mouse y position.
        """
        for grid_y, geom in enumerate(self.row_geometry):
            if geom["y_top"] <= my < geom["y_bottom"]:
                return grid_y

        return self.number_of_rows - 1

    def _handle_mouse(self) -> None:
        """
        Create a disturbance at the current mouse position.

        The mouse position is converted to grid coordinates using
        `_mouse_y_to_grid_y` for the y axis (which accounts for the perspective
        scaling) and a simple division for the x axis (which is uniform).
        A square region of size cursor_splash_size around the grid cell is
        disturbed rather than a single cell, to make the splash more visible.
        The disturbance is clamped to stay within the grid boundaries so that
        the border cells, which are always kept at zero to prevent waves from
        leaking out, are never disturbed.
        """
        mx, my = pg.mouse.get_pos()
        grid_y = self._mouse_y_to_grid_y(my)
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

        The alpha channel is set to 255 for all cells, making the entire grid
        fully opaque at all times.

        Returns:
            A numpy array of shape (rows, cols, 4) with dtype uint8, containing
            RGBA values in the range [0, 255].
        """
        current_state_clipped = np.clip(self.current_state, 0, 255).astype(np.float32)
        normalized_state = current_state_clipped / self.maximum_brightness
        colormap = plt.get_cmap("Blues_r")

        scaled_normalized_state = 0.0 + 1.0 * normalized_state
        rgb_array = (
            colormap(scaled_normalized_state)[..., :3] * self.maximum_brightness
        ).astype(np.uint8)

        alpha_array = np.full_like(normalized_state, 255, dtype=np.uint8)
        return np.concatenate([rgb_array, alpha_array[..., np.newaxis]], axis=-1)

    def _render_state(self, rgba_array: np.ndarray) -> None:
        """
        Render the current RGBA state onto the PyGame screen.

        Each row is rendered as a 1-pixel-tall surface of width number_of_columns,
        which is then scaled to the row's actual pixel dimensions as defined by
        row_geometry. This gives smaller rows at the top and larger rows at the
        bottom, creating the perspective effect. Blitting each row at its correct
        x_left position also creates the trapezoid shape, where rows narrow toward
        the top. Rows with zero height or width are skipped to avoid pygame errors.
        """
        self.screen.fill(self.background_color)

        for y, geom in enumerate(self.row_geometry):
            y_top = geom["y_top"]
            y_bottom = geom["y_bottom"]
            x_left = geom["x_left"]
            x_right = geom["x_right"]

            row_height = y_bottom - y_top
            row_width = x_right - x_left

            if row_height <= 0 or row_width <= 0:
                continue

            row_rgba = rgba_array[y]

            row_surface = pg.Surface((self.number_of_columns, 1), pg.SRCALPHA)
            pg.surfarray.pixels3d(row_surface)[:, 0, :] = row_rgba[:, :3]
            pg.surfarray.pixels_alpha(row_surface)[:, 0] = row_rgba[:, 3]

            row_surface = pg.transform.scale(row_surface, (row_width, row_height))
            self.screen.blit(row_surface, (x_left, y_top))

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

            self._draw_current_state()

            pg.display.flip()
            self.clock.tick(self.framerate)

        pg.quit()


water_ripples = WaterRipples()
water_ripples.execute()
