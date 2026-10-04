"""Module for pygame window setup and rendering."""

import colorsys

import pygame as pg

from src.voronoi_diagram.config_model import ConfigModel
from src.voronoi_diagram.constants import Size
from src.voronoi_diagram.grid import Grid
from src.voronoi_diagram.utils.utils_colors import generate_voronoi_colors
from src.voronoi_diagram.utils.utils_pygame import (
    get_window_size_from_screen_resolution,
)


class Renderer:
    """Manages the pygame window and draws each frame."""

    def __init__(self, config: ConfigModel) -> None:
        """Initializes the renderer with configuration.

        Args:
            config (ConfigModel): Pydantic-validated configuration model.
        """
        self.window_background_color = config.window.background_color
        self.margin_size = config.window.margin_size
        self.show_gridlines = config.grid.show_gridlines
        self.grid_line_color = config.grid.grid_line_color
        self.grid_line_width = config.grid.grid_line_width
        self.grid_dim = config.grid.dim
        self.seed_point_radius = config.voronoi.seed_point_radius
        self.num_seeds = config.voronoi.num_seeds

        window_caption = config.window.caption

        pg.init()

        # Get screen size, but don't open the PyGame display yet. Cell size is
        # a function of grid dimensions and window-grid margin, and is rarely
        # a whole number of pixels — pygame's Rect truncates float dimensions,
        # which leaves sub-pixel gaps between cells, visible as thin horizontal
        # and vertical lines. The block below snaps cell size to an integer
        # pixel and rescales window size accordingly before the display opens.
        self.screen_size = Size(*get_window_size_from_screen_resolution())

        # Grid is always square: sized from the smaller of the two
        # margin-adjusted screen dimensions, and hugs the top-left corner.
        self.grid_size = min(
            self.screen_size.width - 2 * self.margin_size,
            self.screen_size.height - 2 * self.margin_size,
        )
        self.cell_size = self.grid_size / self.grid_dim

        self._snap_to_pixel_grid()

        self.screen = pg.display.set_mode(
            (self.screen_size.width, self.screen_size.height)
        )
        self.clock = pg.time.Clock()

        pg.display.set_caption(window_caption)

        self.seed_point_colors, self.voronoi_cell_colors = generate_voronoi_colors(
            num_seeds=self.num_seeds
        )

    def _snap_to_pixel_grid(self, verbose: bool = True) -> None:
        """Snaps cell size to the nearest integer pixel.

        PyGame's Rect silently truncates float dimensions to integers on
        construction, which causes sub-pixel gaps to accumulate across rows and
        columns during rendering. Window size and margin are rescaled by the
        same ratio so the grid still fills the available space exactly, with no
        leftover gap on any edge. The resulting window size adjustment is
        printed for visibility.
        """
        original_screen_size = self.screen_size

        snap_ratio = round(self.cell_size) / self.cell_size
        self.cell_size = round(self.cell_size)
        self.margin_size = round(self.margin_size * snap_ratio)
        self.screen_size = Size(
            round(self.screen_size.width * snap_ratio),
            round(self.screen_size.height * snap_ratio),
        )
        self.grid_size = self.cell_size * self.grid_dim

        if verbose:
            adjustment_pct = (snap_ratio - 1) * 100
            print(
                f"[cell-size snapping] window size adjusted from "
                f"[{original_screen_size.width}, {original_screen_size.height}] to "
                f"[{self.screen_size.width}, {self.screen_size.height}] "
                f"({adjustment_pct:+.2f}%) to keep cells pixel-aligned"
            )

    def _generate_seed_point_colors(self) -> list[tuple[int, int, int]]:
        """Generates a coherent color palette for seed points using HSV.

        Distributes hues evenly across the color wheel while keeping saturation
        and value constant for visual coherence.

        Args:
            num_seeds (int): Number of colors to generate.

        Returns:
            colors (list[tuple[int, int, int]]): RGB color tuples, one per seed
                point.
        """
        colors = []

        for i in range(self.num_seeds):
            hue = i / self.num_seeds
            saturation = 0.7
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            rgb_int = tuple(int(c * 255) for c in rgb)
            colors.append(rgb_int)

        return colors

    def tick(self, fps: int) -> float:
        """Advances the frame clock and reports the elapsed time.

        Args:
            fps (int): Target frames per second to cap the loop at.

        Returns:
            dt (float): Time in seconds elapsed since the last frame.
        """
        dt = self.clock.tick(fps) / 1000

        return dt

    def _draw_grid_lines(self) -> None:
        """Draws horizontal and vertical grid lines across the grid area."""
        for row in range(self.grid_dim + 1):
            y = int(self.margin_size + row * self.cell_size)
            pg.draw.line(
                self.screen,
                self.grid_line_color,
                (self.margin_size, y),
                (int(self.margin_size + self.grid_size), y),
                self.grid_line_width,
            )

        for col in range(self.grid_dim + 1):
            x = int(self.margin_size + col * self.cell_size)
            pg.draw.line(
                self.screen,
                self.grid_line_color,
                (x, self.margin_size),
                (x, int(self.margin_size + self.grid_size)),
                self.grid_line_width,
            )

    def render_grid(self, grid: Grid) -> None:
        """Draws every cell of the grid onto the display surface.

        Args:
            grid (Grid): The grid whose cells will be drawn.
        """
        for row in range(grid.dimensions.rows):
            for col in range(grid.dimensions.cols):
                value = grid.cells[row][col]
                color = self.voronoi_cell_colors[value]

                rect = pg.Rect(
                    self.margin_size + col * self.cell_size,
                    self.margin_size + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pg.draw.rect(self.screen, color, rect)

    def _draw_seed_points(self, grid: Grid) -> None:
        """Draws seed points as circles on the display.

        Args:
            grid (Grid): The grid whose seed points will be drawn.
        """
        for idx, seed in enumerate(grid.seed_points):
            x = int(self.margin_size + seed.x * self.cell_size)
            y = int(self.margin_size + seed.y * self.cell_size)
            color = self.seed_point_colors[idx]
            pg.draw.circle(self.screen, color, (x, y), self.seed_point_radius)

    def render(self, grid: Grid) -> None:
        """Draws the current frame and presents it to the display.

        1. Fill the screen with the window background color.
        2. Draw the grid cells on top.
        3. Draw the grid lines.
        4. Flip the display buffer to show the frame.

        Args:
            grid (Grid): The grid whose cells will be drawn.
        """
        self.screen.fill(self.window_background_color)
        self.render_grid(grid=grid)
        self._draw_seed_points(grid=grid)

        if self.show_gridlines:
            self._draw_grid_lines()

        pg.display.flip()

    def quit(self) -> None:
        """Shuts down pygame."""
        pg.quit()
