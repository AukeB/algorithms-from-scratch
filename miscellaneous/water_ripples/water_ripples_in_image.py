"""Module that simulates 2D water ripples using PyGame."""

# Imports
import numba
import pygame as pg
import numpy as np
import matplotlib.pyplot as plt

# Constants and algorithm parameters

# Size and dimension related parameters
WINDOW_WIDTH = 4000
WINDOW_HEIGHT = 2500
NUMBER_OF_COLUMNS = 120
NUMBER_OF_ROWS = 80

# Algorithm related parameters
DAMPING = 0.99
WAVE_BRIGHTNESS = 255
MAXIMUM_BRIGHTNESS = 255

# Modes
RENDER_MODE = "trapezoid"  # Options are ["surfarray", "rectangle", "trapezoid"]
RGB_MODE = "scaled_colormap"  # Options are ["grayscale", "colormap", "scaled_colormap"]
PROPAGATE_MODE = "numba"  # Options are ["numba", "numpy", "iterative"]

# Other parameter values
CURSOR_SPLASH_SIZE = 1
FRAMERATE = 60
BACKGROUND_COLOR = (0, 0, 0)

# Mode related
# When RENDER_MODE is set 'trapezoid', these are the parameters w.r.t. the window
# NORMALIZED_TRAPEZOID: dict = {
#     "y_top": 0.3,
#     "y_bottom": 0.7,
#     "x_top_left": 0.5,
#     "x_top_right": 0.8,
#     "x_bottom_left": -0.1,
#     "x_bottom_right": 1,
# }

NORMALIZED_TRAPEZOID: dict = {
    "y_top": 0.48,
    "y_bottom": 1.0,
    "x_top_left": 0,
    "x_top_right": 1,
    "x_bottom_left": 0.3,
    "x_bottom_right": 1,
}

# Functions


@numba.njit(parallel=True)
def propagate_with_numba(
    current_state: np.ndarray,
    previous_state: np.ndarray,
    damping: float,
) -> None:
    """
    In-place mutation
    """
    for y in numba.prange(1, len(previous_state) - 1):
        for x in range(1, len(previous_state[y]) - 1):
            # Compute neighbor sum
            neighbor_sum = (
                previous_state[y - 1, x]
                + previous_state[y + 1, x]
                + previous_state[y, x - 1]
                + previous_state[y, x + 1]
            )

            # Apply ripple formula
            current_state[y, x] = neighbor_sum / 2 - current_state[y, x]

            # Apply damping
            current_state[y, x] *= damping


# Classes


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
        render_mode: str = RENDER_MODE,
        rgb_mode: str = RGB_MODE,
        propagate_mode: str = PROPAGATE_MODE,
        background_color: tuple[int, int, int] = BACKGROUND_COLOR,
        normalized_trapezoid: dict = NORMALIZED_TRAPEZOID,
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
            wave_brightness: Intensity value for the waves. Defaults to 255.
                While the simulation itself allows values outside the range
                [0, 255], the visualization clips to this range, so higher
                values effectively produce higher visual contrast in the
                ripples.
            maximum_brightness: Maximum brightness the visualization can display
            cursor_splash_size (int): The size of the 'splash' when you click on
                the screen
            framerate: Target framerate for rendering. Units: frames / second.
            render_mode (str): The way you render the RGB data. Options are
                "surfarray" (fast, blitting the entire rgb array on the surface
                at once), and "rectangle" (iterating through the RGB array and
                drawing each element as a rectangle on the surface), or
                "trapezoid" (visualizing the grid as a rectangle on the grid,
                with the purpose of creating depth in the simulation).
            rgb_mode (str): The method for converting your current state to an
                RGB array. Options are "grayscale", "colormap" (uses matplotlib
                color maps to visualize the RGB data), or "scaled_colormap"
                (gives you the option to apply scaling to a colormap).
            propagate_mode (str): The method you use for computing the next
                state (propagating). Options are "numba" (uses numba to compute
                next state, converts python loops into executable machine code
                very fast), "numpy" (uses numpy slicing and matrix
                multiplication to compute next state, fast) or "iterative"
                (iterates through grid and computese each next grid element
                individually, slow).
            background_color (tuple(int, int, int)): The background color of the
                canvas.
            normalized_trapezoid (dict[str, float]): If render_mode is set to
                'trapezoid', these are the normalized coordinates of the
                trapezoid w.r.t. the window size.
        """
        # User input variables
        self.window_width = window_width
        self.window_height = window_height
        self.number_of_columns = number_of_columns
        self.number_of_rows = number_of_rows
        self.damping = damping
        self.wave_brightness = wave_brightness
        self.maximum_brightness = maximum_brightness
        self.cursor_splash_size = cursor_splash_size
        self.framerate = framerate
        self.render_mode = render_mode
        self.rgb_mode = rgb_mode
        self.propagate_mode = propagate_mode
        self.background_color = background_color

        # Optional input
        if render_mode == "trapezoid":
            self.normalized_trapezoid = normalized_trapezoid
            self.trapezoid = {
                key: (
                    value * self.window_height
                    if key.startswith("y")
                    else value * self.window_width
                )
                for key, value in normalized_trapezoid.items()
            }

        # Determine grid cell size
        self.grid_cell_width = int(self.window_width / number_of_columns)
        self.grid_cell_height = int(self.window_height / number_of_rows)

        # Initialize with an empty state.
        self.current_state = np.zeros(
            (number_of_rows, number_of_columns), dtype=np.float32
        )
        self.previous_state = np.zeros(
            (number_of_rows, number_of_columns), dtype=np.float32
        )

        # Add a 'splash' when starting the visualization
        self.previous_state[number_of_rows // 2, number_of_columns // 2] = (
            self.wave_brightness
        )

        # Initialize PyGame
        pg.init()
        self.screen = pg.display.set_mode(
            (self.window_width, self.window_height)
        )
        self.clock = pg.time.Clock()  # Used for setting the framerate

    def _handle_mouse(self, event: pg.event.Event) -> None:
        if event.type not in (pg.MOUSEBUTTONDOWN, pg.MOUSEMOTION):
            return

        mx, my = event.pos

        if self.render_mode == "trapezoid":
            if my < self.trapezoid["y_top"] or my > self.trapezoid["y_bottom"]:
                return
            # Invert vertical scaling to find grid_y
            y_top = self.trapezoid["y_top"]
            y_bottom = self.trapezoid["y_bottom"]

            # Normalize my into the vertical space _compute_vertical_scaling operates in
            scaled_grid_cell_height = self.grid_cell_height * (
                self.normalized_trapezoid["y_bottom"] - self.normalized_trapezoid["y_top"]
            )
            y_adjusted = (my - y_top) / scaled_grid_cell_height
            grid_y = int(self._inverse_vertical_scaling(y_adjusted=y_adjusted))
            grid_y = max(0, min(grid_y, self.number_of_rows - 1))

            # Use grid_y to find the x boundaries of that row, then interpolate grid_x
            y_adj = self._compute_vertical_scaling(y=grid_y)
            x_left = self.trapezoid["x_top_left"] + (
                self.normalized_trapezoid["x_bottom_left"] - self.normalized_trapezoid["x_top_left"]
            ) * y_adj * (self.window_height / self.number_of_rows)
            x_right = self.trapezoid["x_top_right"] + (
                self.normalized_trapezoid["x_bottom_right"] - self.normalized_trapezoid["x_top_right"]
            ) * y_adj * (self.window_height / self.number_of_rows)

            # Interpolate x within that row
            grid_x = int((mx - x_left) / (x_right - x_left) * self.number_of_columns)
            grid_x = max(0, min(grid_x, self.number_of_columns - 1))

        else:
            # Normal rectangular mode
            grid_x = mx // self.grid_cell_width
            grid_y = my // self.grid_cell_height

        # Apply disturbance in ripple grid
        self.previous_state[
            max(grid_y - self.cursor_splash_size, 1) : min(
                grid_y + self.cursor_splash_size, self.number_of_rows - 1
            ),
            max(grid_x - self.cursor_splash_size, 1) : min(
                grid_x + self.cursor_splash_size, self.number_of_columns - 1
            ),
        ] = self.wave_brightness

    def _propagate_with_numpy(self) -> None:
        """
        Perform one simulation step of wave propagation using NumPy.

        The new value of each grid cell is computed as the average of its
        four orthogonal neighbors from the previous state, minus the current
        value. A damping factor is applied to simulate energy loss.

        Updates are written in place to `self.current_state`.
        """
        # Compute neighbor sum matrix
        neighbor_sum = (
            self.previous_state[:-2, 1:-1]
            + self.previous_state[2:, 1:-1]
            + self.previous_state[1:-1, :-2]
            + self.previous_state[1:-1, 2:]
        )

        # Apply ripple formula
        self.current_state[1:-1, 1:-1] = (
            neighbor_sum / 2 - self.current_state[1:-1, 1:-1]
        )

        # Apply damping
        self.current_state[1:-1, 1:-1] *= self.damping

    def _propagate_iterative(self) -> None:
        """
        Perform one simulation step of wave propagation using nested loops.

        The new value of each grid cell is computed as the average of its
        four orthogonal neighbors from the previous state, minus the current
        value. A damping factor is applied to simulate energy loss.
        Updates are written in place to `self.current_state`.
        """
        for y in range(1, len(self.previous_state) - 1):
            for x in range(1, len(self.previous_state[y]) - 1):
                # Compute neighbor sum
                neighbor_sum = (
                    self.previous_state[y - 1, x]
                    + self.previous_state[y + 1, x]
                    + self.previous_state[y, x - 1]
                    + self.previous_state[y, x + 1]
                )

                # Apply ripple formula
                self.current_state[y, x] = (
                    neighbor_sum / 2 - self.current_state[y, x]
                )

                # Apply damping
                self.current_state[y, x] *= self.damping

    def _propagate(self, mode: str) -> None:
        """
        Perform one simulation step of wave propagation.
        """
        if mode == "numba":
            propagate_with_numba(
                current_state=self.current_state,
                previous_state=self.previous_state,
                damping=self.damping,
            )
        elif mode == "numpy":
            self._propagate_with_numpy()
        elif mode == "iterative":
            self._propagate_iterative()
        else:
            raise ValueError(f"Unknown mode: {mode}")

        # Python swapping
        self.current_state, self.previous_state = (
            self.previous_state,
            self.current_state,
        )

    def _map_state_to_rgb(
        self,
        mode: str,
    ) -> np.ndarray:
        """
        Maps the current state (a 2D-numpy array with integer values) to a
        RGB-array (a 2D-numpy array with tuples consisting of three elements
        representing the color value)

        Args:
            mode(str): The way t1400he converstion from the current state to RGB
                is performed. Options are
                - "grayscale": Maps the values to just black and white.
                - "colormap": Use a colormap to visualize your state.
                - "scaled_colormap": Option to apply some scaling to your
                    colormap if you dont like the outer edges of the colormap.
        """

        # All values smaller than 0 become 0, and larger than 255 become 255.
        current_state_clipped: np.ndarray = np.clip(
            self.current_state, 0, 255
        ).astype(np.float32)

        if mode == "grayscale":
            # Take the current state value and stack it three times to get
            # greyscale RGB value.
            rgb_array = np.stack([current_state_clipped] * 3, axis=-1).astype(
                np.uint8
            )

        elif mode == "colormap":
            normalized_state = current_state_clipped / self.maximum_brightness
            colormap = plt.get_cmap("Blues_r")
            rgb_array = (
                colormap(normalized_state)[..., :3] * self.maximum_brightness
            ).astype(np.uint8)

        elif mode == "scaled_colormap":
            # Scale from 0–255 to 0.3–1.0 (raise the floor so the darkest is lighter)
            normalized_state = current_state_clipped / self.maximum_brightness
            scaled_normalized_state = 0.1 + 0.8 * normalized_state

            # Using `colormap` on scaled state converts each grid element (a value
            # between 0 and 1, to an RGBA value, so a tuple consisting of 4 elements).
            # The `[..., :3]` removes the alpha layer (transparency/opaqueness) and
            # multiplying it with `self.maximum_brightness` de-normalizes it. Finally,
            # each grid element is converted to an 8-bit unsigned integers, the standard
            # format for image pixel data.
            colormap = plt.get_cmap("Blues_r")
            rgb_array = (
                colormap(scaled_normalized_state)[..., :3]
                * self.maximum_brightness
            ).astype(np.uint8)

        else:
            raise ValueError(f"Unknown mode: {mode}")

        return rgb_array

    def _inverse_vertical_scaling(self, y_adjusted: float, y_start: float = 0.5) -> float:
        """
        Given a projected screen position y_adjusted, returns the grid row y
        that produces it — i.e. the inverse of _compute_vertical_scaling.
        """
        s = y_start / self.number_of_rows * 2
        a = s / 2
        b = y_start + s / 2

        # Quadratic formula: a*y^2 + b*y - y_adjusted = 0
        discriminant = b**2 + 4 * a * y_adjusted
        y = (-b + np.sqrt(discriminant)) / (2 * a)

        return y

    def _compute_vertical_scaling(
        self,
        y,
        y_start: float = 0.5,
    ) -> float:
        """ """
        y_scaling_factor = y_start / self.number_of_rows * 2
        y_adjusted = y * y_start + (y * (y + 1) / 2) * y_scaling_factor

        return y_adjusted

    def _render_state(
        self, 
        rgb_array: np.ndarray, 
        mask: np.ndarray,
        mode: str = "surfarray",
    ) -> None:
        """
        Render the current state onto the PyGame screen.

        Args:
            rgb_array (np.ndarray): A 3D NumPy array of shape (height, width, 3)
                containing RGB values in range [0, 255]. Must have dtype uint8.
            mode (str, optional): Rendering mode. Options:
                - "surfarray": Fast rendering using pg.surfarray.make_surface().
                - "rectangle": Draw each grid element as a PyGame rectangle.
                    Slower, but useful for debugging and customization.
                    Defaults to "surfarray".
                - "trapezoid": Visualize the grid as a trapezoid

        Raises:
            ValueError: If an unknown rendering mode is provided.

        Returns:
            None
        """
        if mode == "surfarray":
            # Pygame surfarray expects arrays in the form (width, height, channels)
            # Therefore we have to swap the width and the height first.
            # The `surfarray` method converts RGB-numpy arrays into a PyGame surface
            # object.
            surface = pg.surfarray.make_surface(rgb_array.swapaxes(0, 1))

            # Match the surface with the window size.
            surface = pg.transform.scale(
                surface, (self.window_width, self.window_height)
            )

            self.screen.blit(surface, (0, 0))

        elif mode == "rectangle":
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
        elif mode == "trapezoid":
            overlay = pg.Surface(
                (self.window_width, self.window_height), pg.SRCALPHA
            )

            for y in range(len(rgb_array)):
                y_adj = self._compute_vertical_scaling(y=y)
                y_adj_plus_one = self._compute_vertical_scaling(y=y + 1)

                for x in range(len(rgb_array[y])):
                    color = rgb_array[y][x]
                    color_rgba = (*color, 200)

                    # Scaled top width based on y coordinate
                    x_left_top = self.trapezoid["x_top_left"] + (
                        self.normalized_trapezoid["x_bottom_left"]
                        - self.normalized_trapezoid["x_top_left"]
                    ) * y_adj * (self.window_height / self.number_of_rows)
                    x_right_top = self.trapezoid["x_top_right"] + (
                        self.normalized_trapezoid["x_bottom_right"]
                        - self.normalized_trapezoid["x_top_right"]
                    ) * y_adj * (self.window_height / self.number_of_rows)

                    # Scaled bottom width based on y_adj coordinate
                    x_left_bottom = self.trapezoid["x_top_left"] + (
                        self.normalized_trapezoid["x_bottom_left"]
                        - self.normalized_trapezoid["x_top_left"]
                    ) * y_adj_plus_one * (
                        self.window_height / self.number_of_rows
                    )
                    x_right_bottom = self.trapezoid["x_top_right"] + (
                        self.normalized_trapezoid["x_bottom_right"]
                        - self.normalized_trapezoid["x_top_right"]
                    ) * y_adj_plus_one * (
                        self.window_height / self.number_of_rows
                    )

                    # Scaled grid cell width top
                    scaled_grid_cell_width_top = (
                        x_right_top - x_left_top
                    ) / self.number_of_columns

                    # Scaled grid cell width bottom
                    scaled_grid_cell_width_bottom = (
                        x_right_bottom - x_left_bottom
                    ) / self.number_of_columns

                    # Scaled height
                    scaled_grid_cell_height = self.grid_cell_height * (
                        self.normalized_trapezoid["y_bottom"]
                        - self.normalized_trapezoid["y_top"]
                    )

                    # Cell coordinates
                    x_cell_top = x_left_top + x * scaled_grid_cell_width_top
                    y_cell_top = (
                        self.trapezoid["y_top"]
                        + y_adj * scaled_grid_cell_height
                    )

                    x_cell_bottom = (
                        x_left_bottom + x * scaled_grid_cell_width_bottom
                    )
                    y_cell_bottom = (
                        self.trapezoid["y_top"]
                        + y_adj_plus_one * scaled_grid_cell_height
                    )

                    if mask is not None:
                        cx = int((x_cell_top + x_cell_top + scaled_grid_cell_width_top) / 2)
                        cy = int((y_cell_top + y_cell_bottom) / 2)
                        cx = max(0, min(cx, self.window_width - 1))
                        cy = max(0, min(cy, self.window_height - 1))
                        if not mask[cy, cx]:
                            continue  # Skip this cell, it's outside the lake

                    wave_intensity = float(self.current_state[y, x])
                    wave_intensity = max(0.0, min(wave_intensity, 255.0))
                    alpha = int((wave_intensity / 255.0) * 255)  # 180 = max alpha, tune to taste
                    color_rgba = (*color, alpha)
                                        

                    pg.draw.polygon(
                        overlay,
                        color_rgba,
                        [
                            (x_cell_top, y_cell_top),
                            (
                                x_cell_top + scaled_grid_cell_width_top,
                                y_cell_top,
                            ),
                            (
                                x_cell_bottom + scaled_grid_cell_width_bottom,
                                y_cell_bottom,
                            ),
                            (x_cell_bottom, y_cell_bottom),
                        ],
                    )

            self.screen.blit(overlay, (0, 0))

        else:
            raise ValueError(f"Unknown rendering mode: {mode}")

    def _draw_current_state(self, mask: np.ndarray) -> None:
        """
        Render the current simulation state to the PyGame window.
        """
        rgb_array = self._map_state_to_rgb(mode=self.rgb_mode)
        self._render_state(rgb_array=rgb_array, mode=self.render_mode, mask=mask)

    def execute(self) -> None:
        """
        Run the simulation loop until the user exits.

        Handles events (QUIT, ESC), updates the simulation each frame,
        draws the current state, and enforces the desired framerate.
        """
        # Main loop
        running = True

        background = pg.image.load(
            "miscellaneous/water_ripples/images/patagonia_lake.jpg"
        ).convert()
        background = pg.transform.scale(
            background, (self.window_width, self.window_height)
        )
        mask = np.load("miscellaneous/water_ripples/lake_mask.npy")

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                elif event.type == pg.MOUSEMOTION:
                    if pg.mouse.get_pressed()[0]:  # Left button held
                        self._handle_mouse(event)

            self.screen.blit(background, (0, 0))
            self._propagate(mode=self.propagate_mode)
            self._draw_current_state(mask=mask)

            pg.display.flip()
            self.clock.tick(self.framerate)

        pg.quit()


water_ripples = WaterRipples()
water_ripples.execute()
